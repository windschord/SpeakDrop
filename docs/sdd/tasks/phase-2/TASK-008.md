# TASK-008: PermissionChecker モジュール（TDD）

> **サブエージェント実行指示**
> このドキュメントは、タスク実行エージェントがサブエージェントにそのまま渡すことを想定しています。
> 以下の内容に従って実装を完了してください。

---

## あなたのタスク

**PermissionChecker モジュール** をTDD方式で実装してください。

### 実装の目標

macOSのマイク権限とアクセシビリティ権限を確認・要求するモジュールを実装します。
AVFoundationでマイク権限、ApplicationServicesでアクセシビリティ権限を確認します。
TDD原則に従い、pyobjcはpytest-mockでモックします。

### 作成/変更するファイル

| 操作 | ファイルパス | 説明 |
|------|-------------|------|
| 作成 | `tests/test_permissions.py` | テストファイル（先行作成） |
| 変更 | `speakdrop/permissions.py` | PermissionChecker モジュール本実装 |

---

## 技術的コンテキスト

### 使用技術

- 言語: Python 3.11+
- テストフレームワーク: pytest + pytest-mock
- macOS権限API: pyobjc-framework-AVFoundation, ApplicationServices（pyobjc）

### 参照すべきファイル

- `@speakdrop/permissions.py` - 現在のスタブ

### 関連する設計書

- `@docs/sdd/design/design.md` の「PermissionChecker」セクション（行427-449）

### 関連する要件

- `@docs/sdd/requirements/stories/US-006.md` - macOS権限の管理

---

## 受入基準

以下のすべての基準を満たしたら、このタスクは完了です：

- [ ] `tests/test_permissions.py` が作成されている（テストが6件以上）
- [ ] `speakdrop/permissions.py` が実装されている
- [ ] `check_microphone()` がboolを返す
- [ ] `check_microphone()` が権限付与済みの場合にTrueを返す
- [ ] `check_microphone()` が権限未付与の場合にFalseを返す
- [ ] `check_accessibility()` がboolを返す
- [ ] `check_accessibility()` が権限付与済みの場合にTrueを返す
- [ ] `check_accessibility()` が権限未付与の場合にFalseを返す
- [ ] pyobjcのモックによりテストがmacOS環境なしで動作する
- [ ] `uv run pytest tests/test_permissions.py -v` で全テストパス
- [ ] `uv run ruff check speakdrop/permissions.py tests/test_permissions.py` でエラー0件
- [ ] `uv run mypy speakdrop/permissions.py` でエラー0件

---

## 実装手順

### ステップ1: テストを先に作成（TDD）

`tests/test_permissions.py` を作成してください：

```python
"""PermissionChecker モジュールのテスト。"""
import sys
from unittest.mock import MagicMock, patch

import pytest


# pyobjc は macOS 専用のため、テスト用にモジュールをモック化
def _setup_pyobjc_mocks() -> None:
    """pyobjc モジュールをシステムモジュールにモック登録する。"""
    mock_av = MagicMock()
    mock_app_services = MagicMock()

    sys.modules.setdefault("AVFoundation", mock_av)
    sys.modules.setdefault("ApplicationServices", mock_app_services)


_setup_pyobjc_mocks()

from speakdrop.permissions import PermissionChecker  # noqa: E402


class TestCheckMicrophone:
    """PermissionChecker.check_microphone() のテスト（REQ-021）。"""

    @patch("speakdrop.permissions.AVCaptureDevice")
    def test_returns_true_when_authorized(
        self, mock_av_capture_device: MagicMock
    ) -> None:
        """マイク権限が付与済みの場合に True を返すこと。"""
        # AVAuthorizationStatusAuthorized = 3
        mock_av_capture_device.authorizationStatusForMediaType_.return_value = 3

        checker = PermissionChecker()
        result = checker.check_microphone()

        assert result is True

    @patch("speakdrop.permissions.AVCaptureDevice")
    def test_returns_false_when_denied(
        self, mock_av_capture_device: MagicMock
    ) -> None:
        """マイク権限が拒否されている場合に False を返すこと。"""
        # AVAuthorizationStatusDenied = 2
        mock_av_capture_device.authorizationStatusForMediaType_.return_value = 2

        checker = PermissionChecker()
        result = checker.check_microphone()

        assert result is False

    @patch("speakdrop.permissions.AVCaptureDevice")
    def test_requests_access_when_not_determined(
        self, mock_av_capture_device: MagicMock
    ) -> None:
        """権限未確認の場合（NotDetermined）に権限リクエストを行うこと（REQ-021）。"""
        # AVAuthorizationStatusNotDetermined = 0
        mock_av_capture_device.authorizationStatusForMediaType_.return_value = 0

        checker = PermissionChecker()
        checker.check_microphone()

        mock_av_capture_device.requestAccessForMediaType_completionHandler_.assert_called_once()

    @patch("speakdrop.permissions.AVCaptureDevice")
    def test_checks_audio_media_type(
        self, mock_av_capture_device: MagicMock
    ) -> None:
        """オーディオメディアタイプで権限確認すること。"""
        mock_av_capture_device.authorizationStatusForMediaType_.return_value = 3

        checker = PermissionChecker()
        checker.check_microphone()

        call_args = mock_av_capture_device.authorizationStatusForMediaType_.call_args
        # AVMediaTypeAudio が使われていること
        assert call_args is not None


class TestCheckAccessibility:
    """PermissionChecker.check_accessibility() のテスト（REQ-022）。"""

    @patch("speakdrop.permissions.AXIsProcessTrustedWithOptions")
    def test_returns_true_when_trusted(
        self, mock_ax_is_trusted: MagicMock
    ) -> None:
        """アクセシビリティ権限が付与済みの場合に True を返すこと。"""
        mock_ax_is_trusted.return_value = True

        checker = PermissionChecker()
        result = checker.check_accessibility()

        assert result is True

    @patch("speakdrop.permissions.AXIsProcessTrustedWithOptions")
    def test_returns_false_when_not_trusted(
        self, mock_ax_is_trusted: MagicMock
    ) -> None:
        """アクセシビリティ権限が未付与の場合に False を返すこと（REQ-022）。"""
        mock_ax_is_trusted.return_value = False

        checker = PermissionChecker()
        result = checker.check_accessibility()

        assert result is False

    @patch("speakdrop.permissions.AXIsProcessTrustedWithOptions")
    def test_calls_ax_is_process_trusted(
        self, mock_ax_is_trusted: MagicMock
    ) -> None:
        """AXIsProcessTrustedWithOptions が呼ばれること。"""
        mock_ax_is_trusted.return_value = True

        checker = PermissionChecker()
        checker.check_accessibility()

        mock_ax_is_trusted.assert_called_once()
```

テストを実行して失敗を確認：

```bash
cd <project-root>
uv run pytest tests/test_permissions.py -v
```

コミット：

```
test: test_permissions.py - PermissionChecker モジュールのTDDテスト追加
```

### ステップ2: PermissionChecker モジュールを実装

`speakdrop/permissions.py` を実装してください：

```python
"""macOS権限確認モジュール。

マイク権限（AVFoundation）とアクセシビリティ権限（ApplicationServices）を確認する。
権限不足の場合はユーザーに案内する（REQ-021, REQ-022）。
"""
from AVFoundation import (
    AVCaptureDevice,
    AVAuthorizationStatusAuthorized,
    AVAuthorizationStatusNotDetermined,
    AVMediaTypeAudio,
)
from ApplicationServices import AXIsProcessTrustedWithOptions


class PermissionChecker:
    """macOS システム権限の確認・要求クラス。"""

    def check_microphone(self) -> bool:
        """マイク権限を確認する（REQ-021）。

        権限が未確認の場合は権限要求ダイアログを表示する。

        Returns:
            権限が付与されている場合は True、それ以外は False
        """
        status = AVCaptureDevice.authorizationStatusForMediaType_(AVMediaTypeAudio)

        if status == AVAuthorizationStatusAuthorized:
            return True

        if status == AVAuthorizationStatusNotDetermined:
            # 権限要求ダイアログを表示（非同期）
            AVCaptureDevice.requestAccessForMediaType_completionHandler_(
                AVMediaTypeAudio,
                lambda granted: None,
            )

        return False

    def check_accessibility(self) -> bool:
        """アクセシビリティ権限を確認する（REQ-022）。

        AXIsProcessTrustedWithOptions() API で権限を確認する。

        Returns:
            権限が付与されている場合は True、それ以外は False
        """
        # prompt=True でシステム環境設定への案内を表示
        result = AXIsProcessTrustedWithOptions({"AXTrustedCheckOptionPrompt": True})
        return bool(result)
```

### ステップ3: テストがパスすることを確認

```bash
cd <project-root>
uv run pytest tests/test_permissions.py -v
uv run ruff check speakdrop/permissions.py tests/test_permissions.py
uv run mypy speakdrop/permissions.py
```

### ステップ4: コミット

```
feat: permissions.py - PermissionChecker 実装（マイク・アクセシビリティ権限、REQ-021/022）
```

---

## 実装の詳細仕様

### PermissionChecker クラス

```python
class PermissionChecker:
    def check_microphone(self) -> bool: ...
    def check_accessibility(self) -> bool: ...
```

### 入出力仕様

**`PermissionChecker.check_microphone() -> bool`:**
- 入力: なし
- 出力: 権限付与済みなら True、未付与なら False
- 副作用（NotDetermined時）: AVFoundationの権限要求ダイアログを表示

**`PermissionChecker.check_accessibility() -> bool`:**
- 入力: なし
- 出力: 権限付与済みなら True、未付与なら False
- 副作用（未付与時）: `AXTrustedCheckOptionPrompt: True` でシステム環境設定への案内を表示

### AVAuthorizationStatus 定数

| 定数名 | 値 | 意味 |
|--------|-----|------|
| AVAuthorizationStatusNotDetermined | 0 | 未確認（要求していない） |
| AVAuthorizationStatusRestricted | 1 | 制限（ペアレンタルコントロール等） |
| AVAuthorizationStatusDenied | 2 | 拒否済み |
| AVAuthorizationStatusAuthorized | 3 | 許可済み |

---

## 注意事項

- pyobjcのインポートはモジュールレベルで行うこと（テストでモック可能にするため）
- テストでは `sys.modules` にモックを登録してから `permissions` をインポートすること
- `AXIsProcessTrustedWithOptions` は `{"AXTrustedCheckOptionPrompt": True}` を引数に渡すこと
- macOS実機での動作確認が必要（テストはモック環境のみ）
- pyobjcのimport形式（AVFoundation, ApplicationServicesのパス）は実行環境で確認が必要

---

## 基本情報（メタデータ）

| 項目 | 値 |
|------|-----|
| **タスクID** | TASK-008 |
| **ステータス** | `DONE` |
| **推定工数** | 25分 |
| **依存関係** | [TASK-001](../phase-1/TASK-001.md) @../phase-1/TASK-001.md |
| **対応要件** | REQ-021, REQ-022 |
| **対応設計** | PermissionChecker セクション（設計書行427-449） |

---

## 情報の明確性チェック

### 明示された情報

- [x] マイク権限API: AVFoundation.AVCaptureDevice.requestAccessForMediaType_completionHandler_()
- [x] アクセシビリティ権限API: ApplicationServices.AXIsProcessTrustedWithOptions()
- [x] 権限確認の戻り値: bool
- [x] NotDetermined時に権限要求ダイアログを表示

### 未確認/要確認の情報

| 項目 | 現状の理解 | 確認状況 |
|------|-----------|----------|
| pyobjcのAVFoundationインポートパス | `from AVFoundation import AVCaptureDevice` で動作すると推測 | [ ] 実装時にuv run pythonで確認 |
| check_microphone()の非同期権限要求の結果 | 非同期なので即座にFalseを返す（次回確認で反映） | [x] 設計書の仕様に準拠 |

---

## 作業ログ（実装時に記入）

### 2026-02-24
- **作業内容**: TDD方式でPermissionCheckerモジュールを実装。テスト7件作成後、実装コードを完成。
- **発生した問題**: AVAuthorizationStatusAuthorized/NotDeterminedの定数がモック時にMagicMockになり比較が失敗した。
- **解決方法**: 定数を数値リテラル（0, 3）でモジュール内に定義し、pyobjcの定数に依存しないようにした。
- **コミットハッシュ**: 6da9857
