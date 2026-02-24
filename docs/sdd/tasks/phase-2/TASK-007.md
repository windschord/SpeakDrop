# TASK-007: HotkeyListener モジュール（TDD）

> **サブエージェント実行指示**
> このドキュメントは、タスク実行エージェントがサブエージェントにそのまま渡すことを想定しています。
> 以下の内容に従って実装を完了してください。

---

## あなたのタスク

**HotkeyListener モジュール** をTDD方式で実装してください。

### 実装の目標

pynput を使ってグローバルホットキー（右Optionキー）を監視するモジュールを実装します。
ホットキー変更用のキャプチャモード（次のキー押下を記録する機能）も実装します。
TDD原則に従い、`pynput.keyboard.Listener` はpytest-mockでモックします。

### 作成/変更するファイル

| 操作 | ファイルパス | 説明 |
|------|-------------|------|
| 作成 | `/Users/tsk/Sync/git/SpeakDrop/tests/test_hotkey_listener.py` | テストファイル（先行作成） |
| 変更 | `/Users/tsk/Sync/git/SpeakDrop/speakdrop/hotkey_listener.py` | HotkeyListener モジュール本実装 |

---

## 技術的コンテキスト

### 使用技術

- 言語: Python 3.11+
- テストフレームワーク: pytest + pytest-mock
- グローバルホットキー監視: pynput

### 参照すべきファイル

- `@/Users/tsk/Sync/git/SpeakDrop/speakdrop/hotkey_listener.py` - 現在のスタブ

### 関連する設計書

- `@/Users/tsk/Sync/git/SpeakDrop/docs/sdd/design/design.md` の「HotkeyListener」セクション（行353-386）

### 関連する要件

- `@/Users/tsk/Sync/git/SpeakDrop/docs/sdd/requirements/stories/US-001.md` - プッシュトークによる音声入力
- `@/Users/tsk/Sync/git/SpeakDrop/docs/sdd/requirements/stories/US-004.md` - ホットキーの設定

---

## 受入基準

以下のすべての基準を満たしたら、このタスクは完了です：

- [ ] `tests/test_hotkey_listener.py` が作成されている（テストが7件以上）
- [ ] `speakdrop/hotkey_listener.py` が実装されている
- [ ] `HotkeyListener.DEFAULT_HOTKEY == "alt_r"`
- [ ] `HotkeyListener.__init__()` が hotkey_key、on_press、on_release コールバックを受け取る
- [ ] `start()` が非同期スレッドでキーボード監視を開始する
- [ ] `stop()` がキーボード監視を停止する
- [ ] 指定ホットキー押下時に `on_press` コールバックが呼ばれる
- [ ] 指定ホットキー離放時に `on_release` コールバックが呼ばれる
- [ ] `start_capture_mode()` が次のキー押下をキャプチャしてコールバックに渡す
- [ ] pynputのモックによりテストがmacOS環境なしで動作する
- [ ] `uv run pytest tests/test_hotkey_listener.py -v` で全テストパス
- [ ] `uv run ruff check speakdrop/hotkey_listener.py tests/test_hotkey_listener.py` でエラー0件
- [ ] `uv run mypy speakdrop/hotkey_listener.py` でエラー0件

---

## 実装手順

### ステップ1: テストを先に作成（TDD）

`/Users/tsk/Sync/git/SpeakDrop/tests/test_hotkey_listener.py` を作成してください：

```python
"""HotkeyListener モジュールのテスト。"""
from unittest.mock import MagicMock, patch

import pytest

from speakdrop.hotkey_listener import HotkeyListener


class TestHotkeyListenerConstants:
    """HotkeyListener の定数テスト。"""

    def test_default_hotkey(self) -> None:
        """DEFAULT_HOTKEY が 'alt_r' であること（右Optionキー）。"""
        assert HotkeyListener.DEFAULT_HOTKEY == "alt_r"


class TestHotkeyListenerInit:
    """HotkeyListener の初期化テスト。"""

    def test_init_with_callbacks(self) -> None:
        """コールバックを受け取って初期化できること。"""
        on_press = MagicMock()
        on_release = MagicMock()
        listener = HotkeyListener(
            hotkey_key="alt_r",
            on_press=on_press,
            on_release=on_release,
        )
        assert listener._hotkey_key == "alt_r"
        assert listener._on_press == on_press
        assert listener._on_release == on_release

    def test_initial_state_not_running(self) -> None:
        """初期状態でリスナーが起動していないこと。"""
        listener = HotkeyListener(
            hotkey_key="alt_r",
            on_press=MagicMock(),
            on_release=MagicMock(),
        )
        assert listener._listener is None


class TestHotkeyListenerStartStop:
    """HotkeyListener の開始・停止テスト。"""

    @patch("speakdrop.hotkey_listener.keyboard")
    def test_start_creates_listener(self, mock_keyboard: MagicMock) -> None:
        """start() が pynput.keyboard.Listener を作成すること。"""
        mock_listener = MagicMock()
        mock_keyboard.Listener.return_value = mock_listener

        listener = HotkeyListener(
            hotkey_key="alt_r",
            on_press=MagicMock(),
            on_release=MagicMock(),
        )
        listener.start()

        mock_keyboard.Listener.assert_called_once()

    @patch("speakdrop.hotkey_listener.keyboard")
    def test_start_starts_listener(self, mock_keyboard: MagicMock) -> None:
        """start() がリスナーを開始すること。"""
        mock_listener = MagicMock()
        mock_keyboard.Listener.return_value = mock_listener

        listener = HotkeyListener(
            hotkey_key="alt_r",
            on_press=MagicMock(),
            on_release=MagicMock(),
        )
        listener.start()

        mock_listener.start.assert_called_once()

    @patch("speakdrop.hotkey_listener.keyboard")
    def test_stop_stops_listener(self, mock_keyboard: MagicMock) -> None:
        """stop() がリスナーを停止すること。"""
        mock_listener = MagicMock()
        mock_keyboard.Listener.return_value = mock_listener

        listener = HotkeyListener(
            hotkey_key="alt_r",
            on_press=MagicMock(),
            on_release=MagicMock(),
        )
        listener.start()
        listener.stop()

        mock_listener.stop.assert_called_once()


class TestHotkeyListenerCallbacks:
    """HotkeyListener のコールバックテスト。"""

    @patch("speakdrop.hotkey_listener.keyboard")
    def test_on_press_called_for_target_key(self, mock_keyboard: MagicMock) -> None:
        """対象ホットキー押下時に on_press コールバックが呼ばれること。"""
        on_press = MagicMock()
        on_release = MagicMock()

        listener = HotkeyListener(
            hotkey_key="alt_r",
            on_press=on_press,
            on_release=on_release,
        )

        # _handle_press を直接呼び出してテスト
        mock_key = MagicMock()
        mock_key.name = "alt_r"
        listener._handle_press(mock_key)

        on_press.assert_called_once()

    @patch("speakdrop.hotkey_listener.keyboard")
    def test_on_press_not_called_for_other_key(
        self, mock_keyboard: MagicMock
    ) -> None:
        """対象外キー押下時に on_press コールバックが呼ばれないこと。"""
        on_press = MagicMock()
        listener = HotkeyListener(
            hotkey_key="alt_r",
            on_press=on_press,
            on_release=MagicMock(),
        )

        mock_key = MagicMock()
        mock_key.name = "shift"
        listener._handle_press(mock_key)

        on_press.assert_not_called()

    @patch("speakdrop.hotkey_listener.keyboard")
    def test_on_release_called_for_target_key(self, mock_keyboard: MagicMock) -> None:
        """対象ホットキー離放時に on_release コールバックが呼ばれること。"""
        on_release = MagicMock()
        listener = HotkeyListener(
            hotkey_key="alt_r",
            on_press=MagicMock(),
            on_release=on_release,
        )

        mock_key = MagicMock()
        mock_key.name = "alt_r"
        listener._handle_release(mock_key)

        on_release.assert_called_once()


class TestHotkeyListenerCaptureMode:
    """HotkeyListener のキャプチャモードテスト（REQ-015）。"""

    @patch("speakdrop.hotkey_listener.keyboard")
    def test_capture_mode_calls_callback_with_key_name(
        self, mock_keyboard: MagicMock
    ) -> None:
        """キャプチャモード中のキー押下でコールバックが呼ばれること（REQ-015）。"""
        capture_callback = MagicMock()
        listener = HotkeyListener(
            hotkey_key="alt_r",
            on_press=MagicMock(),
            on_release=MagicMock(),
        )
        listener.start_capture_mode(capture_callback)

        mock_key = MagicMock()
        mock_key.name = "ctrl_r"
        listener._handle_press(mock_key)

        capture_callback.assert_called_once_with("ctrl_r")

    @patch("speakdrop.hotkey_listener.keyboard")
    def test_capture_mode_disables_normal_callbacks(
        self, mock_keyboard: MagicMock
    ) -> None:
        """キャプチャモード中は通常のホットキーコールバックが無効になること。"""
        on_press = MagicMock()
        listener = HotkeyListener(
            hotkey_key="alt_r",
            on_press=on_press,
            on_release=MagicMock(),
        )
        listener.start_capture_mode(MagicMock())

        mock_key = MagicMock()
        mock_key.name = "alt_r"
        listener._handle_press(mock_key)

        on_press.assert_not_called()

    @patch("speakdrop.hotkey_listener.keyboard")
    def test_capture_mode_ends_after_first_key(
        self, mock_keyboard: MagicMock
    ) -> None:
        """キャプチャモードは最初のキー押下後に終了すること。"""
        capture_callback = MagicMock()
        listener = HotkeyListener(
            hotkey_key="alt_r",
            on_press=MagicMock(),
            on_release=MagicMock(),
        )
        listener.start_capture_mode(capture_callback)

        mock_key = MagicMock()
        mock_key.name = "shift_r"
        listener._handle_press(mock_key)
        listener._handle_press(mock_key)  # 2回目

        assert capture_callback.call_count == 1  # 1回のみ呼ばれる
```

テストを実行して失敗を確認：

```bash
cd /Users/tsk/Sync/git/SpeakDrop
uv run pytest tests/test_hotkey_listener.py -v
```

コミット：

```
test: test_hotkey_listener.py - HotkeyListener モジュールのTDDテスト追加
```

### ステップ2: HotkeyListener モジュールを実装

`/Users/tsk/Sync/git/SpeakDrop/speakdrop/hotkey_listener.py` を実装してください：

```python
"""グローバルホットキー監視モジュール。

pynput を使ってグローバルキーボードイベントを監視する。
アクセシビリティ権限が必要（REQ-022）。
"""
from collections.abc import Callable
from typing import Any

from pynput import keyboard


class HotkeyListener:
    """グローバルホットキー監視クラス（pynput使用）。"""

    DEFAULT_HOTKEY: str = "alt_r"  # 右Option キー

    def __init__(
        self,
        hotkey_key: str,
        on_press: Callable[[], None],
        on_release: Callable[[], None],
    ) -> None:
        """HotkeyListener を初期化する。

        Args:
            hotkey_key: 監視するキー名（例: "alt_r"）
            on_press: ホットキー押下時のコールバック
            on_release: ホットキー離放時のコールバック
        """
        self._hotkey_key = hotkey_key
        self._on_press = on_press
        self._on_release = on_release
        self._listener: keyboard.Listener | None = None
        self._capture_callback: Callable[[str], None] | None = None

    def _get_key_name(self, key: Any) -> str:
        """pynput のキーオブジェクトからキー名を取得する。"""
        if hasattr(key, "name") and key.name is not None:
            return str(key.name)
        if hasattr(key, "char") and key.char is not None:
            return str(key.char)
        return str(key)

    def _handle_press(self, key: Any) -> None:
        """キー押下イベントハンドラ。"""
        key_name = self._get_key_name(key)

        if self._capture_callback is not None:
            # キャプチャモード: 最初のキー押下をキャプチャして終了（REQ-015）
            callback = self._capture_callback
            self._capture_callback = None
            callback(key_name)
            return

        if key_name == self._hotkey_key:
            self._on_press()

    def _handle_release(self, key: Any) -> None:
        """キー離放イベントハンドラ。"""
        if self._capture_callback is not None:
            return  # キャプチャモード中は無視

        key_name = self._get_key_name(key)
        if key_name == self._hotkey_key:
            self._on_release()

    def start(self) -> None:
        """非同期スレッドでキーボード監視を開始する。"""
        self._listener = keyboard.Listener(
            on_press=self._handle_press,
            on_release=self._handle_release,
            daemon=True,
        )
        self._listener.start()

    def stop(self) -> None:
        """キーボード監視を停止する。"""
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    def start_capture_mode(self, callback: Callable[[str], None]) -> None:
        """ホットキー変更用キャプチャモードを開始する（REQ-015）。

        次のキー押下をキャプチャして callback に渡す。
        通常のホットキー監視は一時停止する。

        Args:
            callback: キャプチャしたキー名を受け取るコールバック
        """
        self._capture_callback = callback
```

### ステップ3: テストがパスすることを確認

```bash
cd /Users/tsk/Sync/git/SpeakDrop
uv run pytest tests/test_hotkey_listener.py -v
uv run ruff check speakdrop/hotkey_listener.py tests/test_hotkey_listener.py
uv run mypy speakdrop/hotkey_listener.py
```

### ステップ4: コミット

```
feat: hotkey_listener.py - HotkeyListener 実装（右Optionキー・キャプチャモード、REQ-001/002/015）
```

---

## 実装の詳細仕様

### HotkeyListener クラス

```python
class HotkeyListener:
    DEFAULT_HOTKEY: str = "alt_r"

    def __init__(self, hotkey_key: str, on_press: Callable[[], None],
                 on_release: Callable[[], None]) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def start_capture_mode(self, callback: Callable[[str], None]) -> None: ...
    def _handle_press(self, key: Any) -> None: ...
    def _handle_release(self, key: Any) -> None: ...
```

### 入出力仕様

**`HotkeyListener.start() -> None`:**
- 副作用: daemon=True の pynput.keyboard.Listener を起動

**`HotkeyListener.start_capture_mode(callback: Callable[[str], None]) -> None`:**
- 入力: キー名を受け取るコールバック
- 副作用: キャプチャモード開始。次のキー押下時にコールバックを呼び、モードを終了

### エラー処理

- キー属性エラー（name/charがない）: `str(key)` でフォールバック
- リスナー未起動時のstop(): 何もしない（Noneチェック）

---

## 注意事項

- `from pynput import keyboard` でモジュールレベルインポートすること（モックのため）
- テストでは `@patch("speakdrop.hotkey_listener.keyboard")` でモックすること
- キャプチャモードは1回のキー押下で自動終了すること（REQ-015仕様）
- `daemon=True` でスレッドを起動すること（アプリ終了時に自動停止）
- キー名の取得は `key.name`、`key.char`、`str(key)` の順でフォールバックすること

---

## 基本情報（メタデータ）

| 項目 | 値 |
|------|-----|
| **タスクID** | TASK-007 |
| **ステータス** | `IN_PROGRESS` |
| **推定工数** | 30分 |
| **依存関係** | [TASK-001](../phase-1/TASK-001.md) @../phase-1/TASK-001.md |
| **対応要件** | REQ-001, REQ-002, REQ-014, REQ-015 |
| **対応設計** | HotkeyListener セクション（設計書行353-386） |

---

## 情報の明確性チェック

### 明示された情報

- [x] デフォルトホットキー: "alt_r"（右Optionキー）
- [x] 使用ライブラリ: pynput
- [x] daemon=True でスレッド起動
- [x] キャプチャモード: 次のキー押下を1回キャプチャして終了（REQ-015）
- [x] キャプチャモード中は通常コールバックを無効化

### 未確認/要確認の情報

| 項目 | 現状の理解 | 確認状況 |
|------|-----------|----------|
| pynput.keyboard.Key の name 属性 | "alt_r"が正しいキー名であることを実機で確認が必要 | [ ] 実装後にmacOSで動作確認 |

---

## 作業ログ（実装時に記入）

### YYYY-MM-DD
- **作業内容**:
- **発生した問題**:
- **解決方法**:
- **コミットハッシュ**:
