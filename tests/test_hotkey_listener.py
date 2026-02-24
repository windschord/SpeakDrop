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
