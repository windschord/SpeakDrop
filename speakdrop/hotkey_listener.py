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
