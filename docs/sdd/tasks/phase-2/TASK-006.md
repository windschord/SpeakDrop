# TASK-006: ClipboardInserter モジュール（TDD）

> **サブエージェント実行指示**
> このドキュメントは、タスク実行エージェントがサブエージェントにそのまま渡すことを想定しています。
> 以下の内容に従って実装を完了してください。

---

## あなたのタスク

**ClipboardInserter モジュール** をTDD方式で実装してください。

### 実装の目標

pyobjc（NSPasteboard + CGEvent）を使って、クリップボード経由でテキストをアクティブアプリに挿入するモジュールを実装します。
挿入前にクリップボード内容を退避し、挿入後に復元します（REQ-006）。
TDD原則に従い、pyobjcはpytest-mockでモックします。

### 作成/変更するファイル

| 操作 | ファイルパス | 説明 |
|------|-------------|------|
| 作成 | `tests/test_clipboard_inserter.py` | テストファイル（先行作成） |
| 変更 | `speakdrop/clipboard_inserter.py` | ClipboardInserter モジュール本実装 |

---

## 技術的コンテキスト

### 使用技術

- 言語: Python 3.11+
- テストフレームワーク: pytest + pytest-mock
- クリップボード操作: pyobjc-framework-Cocoa（NSPasteboard）
- キーストローク送信: pyobjc-framework-Quartz（CGEvent）

### 参照すべきファイル

- `@speakdrop/clipboard_inserter.py` - 現在のスタブ

### 関連する設計書

- `@docs/sdd/design/design.md` の「ClipboardInserter」セクション（行322-350）

### 関連する要件

- `@docs/sdd/requirements/stories/US-001.md` - プッシュトークによる音声入力

---

## 受入基準

以下のすべての基準を満たしたら、このタスクは完了です：

- [x] `tests/test_clipboard_inserter.py` が作成されている（テストが6件以上）
- [x] `speakdrop/clipboard_inserter.py` が実装されている
- [x] `ClipboardInserter.PASTE_DELAY == 0.05`
- [x] `ClipboardInserter.RESTORE_DELAY == 0.1`
- [x] `insert()` 前にクリップボード内容を退避する（REQ-006）
- [x] `insert()` でテキストをクリップボードにセットする（REQ-005）
- [x] `insert()` でCmd+Vキーストロークを送信する（REQ-005）
- [x] `insert()` 後にクリップボード内容を復元する（REQ-006）
- [x] Cmd+V失敗時もクリップボード復元を保証する
- [x] pyobjcのモックによりテストがmacOS環境なしで動作する
- [x] `uv run pytest tests/test_clipboard_inserter.py -v` で全テストパス
- [x] `uv run ruff check speakdrop/clipboard_inserter.py tests/test_clipboard_inserter.py` でエラー0件
- [x] `uv run mypy speakdrop/clipboard_inserter.py` でエラー0件

---

## 実装手順

### ステップ1: テストを先に作成（TDD）

`tests/test_clipboard_inserter.py` を作成してください：

```python
"""ClipboardInserter モジュールのテスト。"""
import sys
from unittest.mock import MagicMock, patch


# pyobjc は macOS 専用のため、テスト用にモジュールをモック化
# 実際のビルドなしにインポートできるようにする
def _setup_pyobjc_mocks() -> None:
    """pyobjc モジュールをシステムモジュールにモック登録する。"""
    mock_cocoa = MagicMock()
    mock_quartz = MagicMock()
    mock_appkit = MagicMock()

    sys.modules.setdefault("AppKit", mock_appkit)
    sys.modules.setdefault("Cocoa", mock_cocoa)
    sys.modules.setdefault("Quartz", mock_quartz)
    sys.modules.setdefault("Quartz.CoreGraphics", mock_quartz)


_setup_pyobjc_mocks()

from speakdrop.clipboard_inserter import ClipboardInserter  # noqa: E402


class TestClipboardInserterConstants:
    """ClipboardInserter の定数テスト。"""

    def test_paste_delay(self) -> None:
        """PASTE_DELAY が 0.05 であること。"""
        assert ClipboardInserter.PASTE_DELAY == 0.05

    def test_restore_delay(self) -> None:
        """RESTORE_DELAY が 0.1 であること。"""
        assert ClipboardInserter.RESTORE_DELAY == 0.1


class TestClipboardInserterInsert:
    """ClipboardInserter.insert() のテスト。"""

    def _make_mock_pb(self, has_items: bool = True) -> MagicMock:
        """テスト用のNSPasteboardモックを作成する。"""
        mock_pb = MagicMock()
        if has_items:
            mock_item = MagicMock()
            mock_item.types.return_value = ["public.utf8-plain-text"]
            mock_pb.pasteboardItems.return_value = [mock_item]
        else:
            mock_pb.pasteboardItems.return_value = []
        return mock_pb

    @patch("speakdrop.clipboard_inserter.time.sleep")
    @patch("speakdrop.clipboard_inserter.NSPasteboard")
    @patch("speakdrop.clipboard_inserter.CGEventCreateKeyboardEvent")
    @patch("speakdrop.clipboard_inserter.CGEventPost")
    def test_insert_saves_clipboard_before_insert(
        self,
        mock_post: MagicMock,
        mock_create_event: MagicMock,
        mock_pasteboard_cls: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """insert() 前にクリップボード内容を退避すること（REQ-006）。"""
        mock_pb = self._make_mock_pb(has_items=True)
        mock_pasteboard_cls.generalPasteboard.return_value = mock_pb

        inserter = ClipboardInserter()
        inserter.insert("新しいテキスト")

        # pasteboardItems() でアイテム一覧を取得したことを確認
        mock_pb.pasteboardItems.assert_called()

    @patch("speakdrop.clipboard_inserter.time.sleep")
    @patch("speakdrop.clipboard_inserter.NSPasteboard")
    @patch("speakdrop.clipboard_inserter.CGEventCreateKeyboardEvent")
    @patch("speakdrop.clipboard_inserter.CGEventPost")
    def test_insert_sets_text_to_clipboard(
        self,
        mock_post: MagicMock,
        mock_create_event: MagicMock,
        mock_pasteboard_cls: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """insert() でテキストをクリップボードにセットすること（REQ-005）。"""
        mock_pb = self._make_mock_pb(has_items=False)
        mock_pasteboard_cls.generalPasteboard.return_value = mock_pb

        inserter = ClipboardInserter()
        inserter.insert("挿入するテキスト")

        mock_pb.setString_forType_.assert_called()
        call_args = mock_pb.setString_forType_.call_args_list
        texts = [str(c.args[0]) for c in call_args]
        assert "挿入するテキスト" in texts

    @patch("speakdrop.clipboard_inserter.time.sleep")
    @patch("speakdrop.clipboard_inserter.NSPasteboard")
    @patch("speakdrop.clipboard_inserter.CGEventCreateKeyboardEvent")
    @patch("speakdrop.clipboard_inserter.CGEventPost")
    def test_insert_sends_cmd_v(
        self,
        mock_post: MagicMock,
        mock_create_event: MagicMock,
        mock_pasteboard_cls: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """insert() でCmd+Vキーストロークを送信すること（REQ-005）。"""
        mock_pb = self._make_mock_pb(has_items=False)
        mock_pasteboard_cls.generalPasteboard.return_value = mock_pb

        inserter = ClipboardInserter()
        inserter.insert("テスト")

        # CGEventPost が呼ばれたことを確認（Cmd+V送信）
        assert mock_post.call_count >= 2  # key down + key up

    @patch("speakdrop.clipboard_inserter.time.sleep")
    @patch("speakdrop.clipboard_inserter.NSPasteboard")
    @patch("speakdrop.clipboard_inserter.CGEventCreateKeyboardEvent")
    @patch("speakdrop.clipboard_inserter.CGEventPost")
    def test_insert_restores_clipboard_after_insert(
        self,
        mock_post: MagicMock,
        mock_create_event: MagicMock,
        mock_pasteboard_cls: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """insert() 後にクリップボード内容を復元すること（REQ-006）。"""
        mock_pb = self._make_mock_pb(has_items=True)
        mock_pasteboard_cls.generalPasteboard.return_value = mock_pb

        inserter = ClipboardInserter()
        inserter.insert("新しいテキスト")

        # 全アイテムを writeObjects_ で復元したことを確認
        mock_pb.writeObjects_.assert_called_once()

    @patch("speakdrop.clipboard_inserter.time.sleep")
    @patch("speakdrop.clipboard_inserter.NSPasteboard")
    @patch("speakdrop.clipboard_inserter.CGEventCreateKeyboardEvent")
    @patch("speakdrop.clipboard_inserter.CGEventPost")
    def test_insert_restores_clipboard_even_on_error(
        self,
        mock_post: MagicMock,
        mock_create_event: MagicMock,
        mock_pasteboard_cls: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """Cmd+V送信がエラーになっても、クリップボードを復元すること。"""
        mock_pb = self._make_mock_pb(has_items=True)
        mock_pasteboard_cls.generalPasteboard.return_value = mock_pb
        mock_post.side_effect = Exception("CGEvent error")

        inserter = ClipboardInserter()
        inserter.insert("新しいテキスト")

        # エラーが起きても writeObjects_ で復元される
        mock_pb.writeObjects_.assert_called_once()

    @patch("speakdrop.clipboard_inserter.time.sleep")
    @patch("speakdrop.clipboard_inserter.NSPasteboard")
    @patch("speakdrop.clipboard_inserter.CGEventCreateKeyboardEvent")
    @patch("speakdrop.clipboard_inserter.CGEventPost")
    def test_insert_restores_empty_when_clipboard_was_empty(
        self,
        mock_post: MagicMock,
        mock_create_event: MagicMock,
        mock_pasteboard_cls: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """クリップボードが空だった場合、clearContents のみで復元しないこと。"""
        mock_pb = self._make_mock_pb(has_items=False)
        mock_pasteboard_cls.generalPasteboard.return_value = mock_pb

        inserter = ClipboardInserter()
        inserter.insert("新しいテキスト")

        # アイテムがない場合は writeObjects_ を呼ばない
        mock_pb.writeObjects_.assert_not_called()
        # clearContents は呼ばれる
        mock_pb.clearContents.assert_called()
```

テストを実行して失敗を確認：

```bash
cd <project-root>
uv run pytest tests/test_clipboard_inserter.py -v
```

コミット：

```text
test: test_clipboard_inserter.py - ClipboardInserter モジュールのTDDテスト追加
```

### ステップ2: ClipboardInserter モジュールを実装

`speakdrop/clipboard_inserter.py` を実装してください：

```python
"""クリップボード・テキスト挿入モジュール。

NSPasteboard でクリップボードを操作し、
CGEvent で Cmd+V キーストロークを送信してテキストを挿入する。
挿入前後にクリップボード内容を退避・復元する（REQ-006）。
"""
import time

from AppKit import NSPasteboardTypeString
from Cocoa import NSPasteboard
from Quartz.CoreGraphics import (
    CGEventCreateKeyboardEvent,
    CGEventPost,
    CGEventSetFlags,
    kCGEventFlagMaskCommand,
    kCGHIDEventTap,
)

# 'v' キーのキーコード
_KEY_V = 0x09


class ClipboardInserter:
    """クリップボード経由でテキストを挿入するクラス。"""

    PASTE_DELAY: float = 0.05   # Cmd+V 送信前の待機時間（秒）
    RESTORE_DELAY: float = 0.1  # クリップボード復元前の待機時間（秒）

    def insert(self, text: str) -> None:
        """テキストをアクティブなアプリケーションに挿入する。

        手順:
        1. 既存クリップボード内容を退避（REQ-006）
        2. text をクリップボードにセット
        3. Cmd+V キーストロークを送信（REQ-005）
        4. 待機（RESTORE_DELAY）
        5. クリップボード内容を復元（REQ-006）

        Args:
            text: 挿入するテキスト
        """
        pb = NSPasteboard.generalPasteboard()

        # 1. 退避
        original = pb.stringForType_(NSPasteboardTypeString)

        # 2. テキストをクリップボードにセット
        pb.clearContents()
        pb.setString_forType_(text, NSPasteboardTypeString)

        try:
            # 3. Cmd+V を送信
            time.sleep(self.PASTE_DELAY)
            self._send_cmd_v()
        finally:
            # 4. 待機してから復元
            time.sleep(self.RESTORE_DELAY)
            # 5. 復元（REQ-006）
            pb.clearContents()
            if original is not None:
                pb.setString_forType_(original, NSPasteboardTypeString)

    def _send_cmd_v(self) -> None:
        """Cmd+V キーストロークを送信する。"""
        # Key down
        event_down = CGEventCreateKeyboardEvent(None, _KEY_V, True)
        CGEventSetFlags(event_down, kCGEventFlagMaskCommand)
        CGEventPost(kCGHIDEventTap, event_down)

        # Key up
        event_up = CGEventCreateKeyboardEvent(None, _KEY_V, False)
        CGEventSetFlags(event_up, kCGEventFlagMaskCommand)
        CGEventPost(kCGHIDEventTap, event_up)
```

### ステップ3: テストがパスすることを確認

```bash
cd <project-root>
uv run pytest tests/test_clipboard_inserter.py -v
uv run ruff check speakdrop/clipboard_inserter.py tests/test_clipboard_inserter.py
uv run mypy speakdrop/clipboard_inserter.py
```

### ステップ4: コミット

```text
feat: clipboard_inserter.py - ClipboardInserter 実装（クリップボード退避・復元、REQ-005/006）
```

---

## 実装の詳細仕様

### 使用API

| 操作 | 使用API |
|------|---------|
| クリップボード読み取り | `NSPasteboard.generalPasteboard().stringForType_(NSPasteboardTypeString)` |
| クリップボード書き込み | `NSPasteboard.clearContents()` + `setString_forType_()` |
| Cmd+Vキーストローク | `CGEventCreateKeyboardEvent()` + `CGEventSetFlags()` + `CGEventPost()` |

### 入出力仕様

**`ClipboardInserter.insert(text: str) -> None`:**
- 入力: 挿入するテキスト（str）
- 出力: なし
- 副作用: テキストをアクティブアプリに挿入、クリップボードを復元

### エラー処理

- Cmd+V失敗: `try/finally` でクリップボード復元を保証（設計書行534参照）
- クリップボードが空だった場合: `clearContents()` でクリア（Noneを設定しない）

---

## 注意事項

- pyobjc の `NSPasteboard`、`CGEvent` 関連をモジュールレベルでインポートすること
- テストでは `sys.modules` にモックを登録してから `clipboard_inserter` をインポートすること
- `try/finally` でクリップボード復元を必ず実行すること（REQ-006の保証）
- `CGEventSetFlags` で Command フラグをセットすること（Cmd+Vのため）
- `PASTE_DELAY` はCmd+V送信前、`RESTORE_DELAY` は復元前に待機すること

---

## 基本情報（メタデータ）

| 項目 | 値 |
|------|-----|
| **タスクID** | TASK-006 |
| **ステータス** | `DONE` |
| **推定工数** | 35分 |
| **依存関係** | [TASK-001](../phase-1/TASK-001.md) @../phase-1/TASK-001.md |
| **対応要件** | REQ-005, REQ-006 |
| **対応設計** | ClipboardInserter セクション（設計書行322-350） |

---

## 情報の明確性チェック

### 明示された情報

- [x] PASTE_DELAY: 0.05秒
- [x] RESTORE_DELAY: 0.1秒
- [x] クリップボード読み取りAPI: NSPasteboard.stringForType_()
- [x] クリップボード書き込みAPI: NSPasteboard.setString_forType_()
- [x] キーストロークAPI: CGEventCreateKeyboardEvent + CGEventPost
- [x] 挿入手順: 退避→セット→Cmd+V→待機→復元

### 未確認/要確認の情報

| 項目 | 現状の理解 | 確認状況 |
|------|-----------|----------|
| pyobjcのimport形式 | Cocoa/AppKit/Quartzのインポートパスは実行環境で確認が必要 | [ ] 実装時にuv run pythonで動作確認 |

---

## 作業ログ（実装時に記入）

### 2026-02-24
- **作業内容**: TDD方式でClipboardInserterモジュールを実装。テスト8件先行作成→失敗確認→実装→全パス確認
- **発生した問題**: `test_insert_restores_clipboard_even_on_error` が失敗。例外が再スローされてinsert()から漏れていた
- **解決方法**: `try/except/finally` パターンに変更。exceptブロックでException をキャッチして無視し、finallyで必ず復元を実行
- **コミットハッシュ**: b9435f8
