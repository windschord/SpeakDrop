"""SpeakDropApp のテスト。

rumps をモック化して、AppState 状態管理・ホットキーコールバック・
トグル機能を検証する。
"""

from __future__ import annotations

import sys
from enum import Enum
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# rumps のモック（テスト環境では AppKit が利用できないため）
# ---------------------------------------------------------------------------


class _FakeMenuItem:
    """rumps.MenuItem のフェイク実装。"""

    def __init__(self, title: str = "", callback: Any = None) -> None:
        self.title = title
        self._callback = callback

    def set_callback(self, callback: Any) -> None:
        self._callback = callback


class _FakeApp:
    """rumps.App のフェイク実装。"""

    def __init__(
        self, name: str, title: str | None = None, quit_button: str | None = "Quit"
    ) -> None:
        self.name = name
        self.title = title or name
        self.menu: list[Any] = []


class _FakeWindow:
    """rumps.Window のフェイク実装。"""

    def __init__(self, **kwargs: Any) -> None:
        self._kwargs = kwargs
        self.run_result = MagicMock(clicked=0)

    def run(self) -> MagicMock:
        return self.run_result


def _fake_quit_application() -> None:
    pass


def _fake_notification(**kwargs: Any) -> None:
    pass


def _fake_alert(**kwargs: Any) -> None:
    pass


# rumps モジュールをフェイクで差し替え
_fake_rumps = MagicMock()
_fake_rumps.App = _FakeApp
_fake_rumps.MenuItem = _FakeMenuItem
_fake_rumps.Window = _FakeWindow
_fake_rumps.quit_application = _fake_quit_application
_fake_rumps.notification = _fake_notification
_fake_rumps.alert = _fake_alert

sys.modules["rumps"] = _fake_rumps

# ---------------------------------------------------------------------------
# 依存モジュールもモック化
# ---------------------------------------------------------------------------

_mock_audio_recorder = MagicMock()
_mock_transcriber = MagicMock()
_mock_text_processor = MagicMock()
_mock_clipboard_inserter = MagicMock()
_mock_hotkey_listener_cls = MagicMock()
_mock_permission_checker = MagicMock()

# デフォルトの戻り値設定
_mock_permission_checker.return_value.check_microphone.return_value = True
_mock_permission_checker.return_value.check_accessibility.return_value = True

sys.modules.setdefault("sounddevice", MagicMock())
sys.modules.setdefault("numpy", MagicMock())
sys.modules.setdefault("faster_whisper", MagicMock())
sys.modules.setdefault("ollama", MagicMock())
sys.modules.setdefault("pynput", MagicMock())
sys.modules.setdefault("pynput.keyboard", MagicMock())
sys.modules.setdefault("AppKit", MagicMock())
sys.modules.setdefault("Cocoa", MagicMock())
sys.modules.setdefault("Quartz", MagicMock())
sys.modules.setdefault("Quartz.CoreGraphics", MagicMock())


# ---------------------------------------------------------------------------
# フィクスチャ
# ---------------------------------------------------------------------------


@pytest.fixture
def app() -> Any:
    """SpeakDropApp インスタンスを返す（全依存をモック化）。"""

    def _call_after(func: Any, *args: Any, **kwargs: Any) -> None:
        func(*args, **kwargs)

    with (
        patch("speakdrop.app.AudioRecorder", return_value=MagicMock()),
        patch("speakdrop.app.Transcriber", return_value=MagicMock()),
        patch("speakdrop.app.TextProcessor", return_value=MagicMock()),
        patch("speakdrop.app.ClipboardInserter", return_value=MagicMock()),
        patch("speakdrop.app.HotkeyListener", return_value=MagicMock()),
        patch("speakdrop.app.PermissionChecker") as mock_pc,
        patch("speakdrop.app.Config") as mock_cfg,
        patch("speakdrop.app.AppHelper") as mock_app_helper,
    ):
        mock_app_helper.callAfter.side_effect = _call_after
        mock_cfg_instance = MagicMock()
        mock_cfg_instance.enabled = True
        mock_cfg_instance.hotkey = "alt_r"
        mock_cfg_instance.model = "kotoba-tech/kotoba-whisper-v1.0"
        mock_cfg_instance.ollama_model = "qwen2.5:7b"
        mock_cfg.return_value.load.return_value = mock_cfg_instance

        mock_pc.return_value.check_microphone.return_value = True
        mock_pc.return_value.check_accessibility.return_value = True

        from speakdrop.app import SpeakDropApp

        instance = SpeakDropApp()
        yield instance


# ---------------------------------------------------------------------------
# テストヘルパー
# ---------------------------------------------------------------------------


def _make_window_response(clicked: int, text: str) -> MagicMock:
    """Window.run() の戻り値を生成するヘルパー。"""
    r = MagicMock()
    r.clicked = clicked
    r.text = text
    return r


def _make_window_mock(response: MagicMock) -> MagicMock:
    """Window インスタンスのモックを生成するヘルパー。"""
    window = MagicMock()
    window.run.return_value = response
    return window


def _window_sequence(*steps: tuple[int, str]) -> list[MagicMock]:
    """複数ダイアログのモック列を生成するヘルパー。"""
    return [_make_window_mock(_make_window_response(clicked, text)) for clicked, text in steps]


# ---------------------------------------------------------------------------
# テスト
# ---------------------------------------------------------------------------


class TestAppState:
    """AppState enum のテスト。"""

    def test_states_defined(self) -> None:
        """IDLE / RECORDING / PROCESSING が定義されている。"""
        from speakdrop.app import AppState

        assert AppState.IDLE is not None
        assert AppState.RECORDING is not None
        assert AppState.PROCESSING is not None

    def test_is_enum(self) -> None:
        """AppState が Enum を継承している。"""
        from speakdrop.app import AppState

        assert issubclass(AppState, Enum)


class TestInitialState:
    """初期状態のテスト。"""

    def test_initial_state_is_idle(self, app: Any) -> None:
        """初期状態が IDLE である。"""
        from speakdrop.app import AppState

        assert app.state == AppState.IDLE

    def test_initial_title_reflects_idle(self, app: Any) -> None:
        """初期タイトルが IDLE アイコンである。"""
        from speakdrop.app import AppState
        from speakdrop.icons import get_icon_title

        assert app.title == get_icon_title(AppState.IDLE)


class TestSetState:
    """set_state() のテスト。"""

    def test_set_state_idle(self, app: Any) -> None:
        """set_state(IDLE) でタイトルと状態が更新される。"""
        from speakdrop.app import AppState
        from speakdrop.icons import get_icon_title

        app.set_state(AppState.IDLE)

        assert app.state == AppState.IDLE
        assert app.title == get_icon_title(AppState.IDLE)
        assert app.status_item.title == "待機中"

    def test_set_state_recording(self, app: Any) -> None:
        """set_state(RECORDING) でタイトルと状態が更新される。"""
        from speakdrop.app import AppState
        from speakdrop.icons import get_icon_title

        app.set_state(AppState.RECORDING)

        assert app.state == AppState.RECORDING
        assert app.title == get_icon_title(AppState.RECORDING)
        assert app.status_item.title == "録音中..."

    def test_set_state_processing(self, app: Any) -> None:
        """set_state(PROCESSING) でタイトルと状態が更新される。"""
        from speakdrop.app import AppState
        from speakdrop.icons import get_icon_title

        app.set_state(AppState.PROCESSING)

        assert app.state == AppState.PROCESSING
        assert app.title == get_icon_title(AppState.PROCESSING)
        assert app.status_item.title == "処理中..."


class TestHotkeyCallbacks:
    """ホットキーコールバックのテスト。"""

    def test_on_hotkey_press_transitions_to_recording(self, app: Any) -> None:
        """on_hotkey_press() が RECORDING 状態に遷移させる。"""
        from speakdrop.app import AppState

        app.on_hotkey_press()

        assert app.state == AppState.RECORDING
        app.audio_recorder.start_recording.assert_called_once()

    def test_on_hotkey_press_ignored_when_not_idle(self, app: Any) -> None:
        """IDLE 以外の状態では on_hotkey_press() は何もしない。"""
        from speakdrop.app import AppState

        app.set_state(AppState.RECORDING)
        app.audio_recorder.start_recording.reset_mock()

        app.on_hotkey_press()

        assert app.state == AppState.RECORDING
        app.audio_recorder.start_recording.assert_not_called()

    def test_on_hotkey_release_transitions_to_processing(self, app: Any) -> None:
        """on_hotkey_release() が PROCESSING 状態に遷移させ、録音を停止する。"""
        from speakdrop.app import AppState

        # RECORDING 状態にする
        app.set_state(AppState.RECORDING)
        mock_audio = MagicMock()
        app.audio_recorder.stop_recording.return_value = mock_audio

        # スレッドが即座に完了しないよう process_audio をパッチ
        with patch.object(app, "process_audio"):
            app.on_hotkey_release()
            # スレッド起動後、set_state(PROCESSING) が呼ばれていること
            app.audio_recorder.stop_recording.assert_called_once()
            assert app.state == AppState.PROCESSING

    def test_on_hotkey_release_ignored_when_not_recording(self, app: Any) -> None:
        """RECORDING 以外の状態では on_hotkey_release() は何もしない。"""
        from speakdrop.app import AppState

        # IDLE 状態のまま
        assert app.state == AppState.IDLE

        app.on_hotkey_release()

        app.audio_recorder.stop_recording.assert_not_called()

    def test_on_hotkey_press_ignored_when_disabled(self, app: Any) -> None:
        """config.enabled が False の場合 on_hotkey_press() は無視される。"""
        from speakdrop.app import AppState

        app.config.enabled = False

        app.on_hotkey_press()

        assert app.state == AppState.IDLE
        app.audio_recorder.start_recording.assert_not_called()


class TestToggleEnabled:
    """toggle_enabled() / _toggle_enabled() のテスト。"""

    def test_toggle_disables_when_enabled(self, app: Any) -> None:
        """enabled=True の状態でトグルすると False になる。"""
        app.config.enabled = True

        app._toggle_enabled(MagicMock())

        assert app.config.enabled is False
        app.config.save.assert_called()

    def test_toggle_enables_when_disabled(self, app: Any) -> None:
        """enabled=False の状態でトグルすると True になる。"""
        app.config.enabled = False

        app._toggle_enabled(MagicMock())

        assert app.config.enabled is True
        app.config.save.assert_called()

    def test_toggle_updates_menu_title_to_off(self, app: Any) -> None:
        """無効化時にメニュータイトルが '音声入力 OFF' になる。"""
        app.config.enabled = True

        app._toggle_enabled(MagicMock())

        assert "OFF" in app.toggle_item.title

    def test_toggle_updates_menu_title_to_on(self, app: Any) -> None:
        """有効化時にメニュータイトルが '音声入力 ON' になる。"""
        app.config.enabled = False

        app._toggle_enabled(MagicMock())

        assert "ON" in app.toggle_item.title

    def test_toggle_starts_hotkey_listener_when_enabled(self, app: Any) -> None:
        """無効->有効に切り替えると _start_hotkey_listener() が呼ばれる。"""
        app.config.enabled = False

        with patch.object(app, "_start_hotkey_listener") as mock_start:
            app._toggle_enabled(MagicMock())

        mock_start.assert_called_once()

    def test_toggle_stops_hotkey_listener_when_disabled(self, app: Any) -> None:
        """有効->無効に切り替えると hotkey_listener.stop() が呼ばれる。"""
        app.config.enabled = True
        mock_listener = MagicMock()
        app.hotkey_listener = mock_listener

        app._toggle_enabled(MagicMock())

        mock_listener.stop.assert_called_once()


class TestProcessAudio:
    """process_audio() のテスト。"""

    def test_process_audio_calls_transcribe_and_insert(self, app: Any) -> None:
        """process_audio() が transcribe → text_processor.process → insert の順に呼ぶ。"""
        from speakdrop.app import AppState

        mock_audio = MagicMock()
        app.transcriber.transcribe.return_value = "テストテキスト"
        app.text_processor.process.return_value = "処理済みテキスト"
        app.state = AppState.PROCESSING

        app.process_audio(mock_audio)

        app.transcriber.transcribe.assert_called_once_with(mock_audio)
        app.text_processor.process.assert_called_once_with("テストテキスト")
        app.clipboard_inserter.insert.assert_called_once_with("処理済みテキスト")

    def test_process_audio_returns_to_idle(self, app: Any) -> None:
        """process_audio() 完了後に IDLE 状態に戻る。"""
        from speakdrop.app import AppState

        app.transcriber.transcribe.return_value = "テキスト"
        app.text_processor.process.return_value = "テキスト"
        app.state = AppState.PROCESSING

        app.process_audio(MagicMock())

        assert app.state == AppState.IDLE

    def test_process_audio_returns_to_idle_on_error(self, app: Any) -> None:
        """process_audio() でエラーが発生しても IDLE 状態に戻る。"""
        from speakdrop.app import AppState

        app.transcriber.transcribe.side_effect = RuntimeError("エラー")
        app.state = AppState.PROCESSING

        app.process_audio(MagicMock())

        assert app.state == AppState.IDLE

    def test_process_audio_skips_empty_text(self, app: Any) -> None:
        """空白のみのテキストは text_processor.process と insert を呼ばない。"""
        from speakdrop.app import AppState

        app.transcriber.transcribe.return_value = "   "
        app.state = AppState.PROCESSING

        app.process_audio(MagicMock())

        app.text_processor.process.assert_not_called()
        app.clipboard_inserter.insert.assert_not_called()
        assert app.state == AppState.IDLE


class TestOpenSettings:
    """open_settings() ダイアログのテスト。"""

    def test_whisper_model_change_saves_and_reloads(self, app: Any) -> None:
        """Whisper モデル変更時に設定が保存されトランスクライバーがリロードされること。"""
        # 1/3: Whisper モデル変更（large-v3）、2/3: ホットキーキャンセル → 終了
        with patch("speakdrop.app.rumps.Window") as mock_window_cls:
            mock_window_cls.side_effect = _window_sequence(
                (1, "large-v3"),
                (0, ""),
            )
            app.open_settings(MagicMock())

        app.config.save.assert_called_once()
        app.transcriber.reload_model.assert_called_once_with("large-v3")

    def test_hotkey_change_restarts_listener(self, app: Any) -> None:
        """ホットキー変更時にリスナーが再起動されること。"""
        mock_listener = MagicMock()
        app.hotkey_listener = mock_listener

        with patch("speakdrop.app.rumps.Window") as mock_window_cls:
            mock_window_cls.side_effect = _window_sequence(
                (1, app.config.model),  # Whisper OK（変更なし）
                (1, "alt_l"),  # ホットキー OK
                (0, ""),  # Ollama キャンセル → 終了
            )
            with patch.object(app, "_start_hotkey_listener") as mock_start:
                with patch.object(app, "_is_valid_hotkey", return_value=True):
                    app.open_settings(MagicMock())

        mock_listener.stop.assert_called_once()
        mock_start.assert_called_once()
        assert app.config.hotkey == "alt_l"
        app.config.save.assert_called_once()

    def test_ollama_model_change_recreates_text_processor(self, app: Any) -> None:
        """Ollama モデル変更時に TextProcessor が再生成されること。"""
        with patch("speakdrop.app.rumps.Window") as mock_window_cls:
            mock_window_cls.side_effect = _window_sequence(
                (1, app.config.model),  # Whisper OK（変更なし）
                (1, app.config.hotkey),  # ホットキー OK（変更なし）
                (1, "gemma3:4b"),  # Ollama OK
            )
            with patch("speakdrop.app.TextProcessor") as mock_tp_cls:
                mock_tp_cls.return_value = MagicMock()
                app.open_settings(MagicMock())

        mock_tp_cls.assert_called_once_with(model="gemma3:4b")
        assert app.config.ollama_model == "gemma3:4b"
        app.config.save.assert_called_once()
        assert app.text_processor is mock_tp_cls.return_value

    def test_ollama_model_without_tag_is_accepted(self, app: Any) -> None:
        """タグ省略の Ollama モデル名（例: llama3.2）も受け入れられること。"""
        with (
            patch("speakdrop.app.rumps.Window") as mock_window_cls,
            patch("speakdrop.app.TextProcessor") as mock_tp_cls,
        ):
            mock_tp_cls.return_value = MagicMock()
            mock_window_cls.side_effect = _window_sequence(
                (1, app.config.model),  # Whisper OK（変更なし）
                (1, app.config.hotkey),  # ホットキー OK（変更なし）
                (1, "llama3.2"),  # Ollama: タグなし
            )
            app.open_settings(MagicMock())

        mock_tp_cls.assert_called_once_with(model="llama3.2")
        assert app.config.ollama_model == "llama3.2"
        app.config.save.assert_called_once()
        assert app.text_processor is mock_tp_cls.return_value

    def test_all_cancel_changes_nothing(self, app: Any) -> None:
        """最初のダイアログでキャンセルした場合に設定が変更されないこと。"""
        original_hotkey = app.config.hotkey
        original_model = app.config.model
        original_ollama_model = app.config.ollama_model

        with patch("speakdrop.app.rumps.Window") as mock_window_cls:
            mock_window_cls.side_effect = _window_sequence(
                (0, ""),  # Whisper キャンセル → 終了
            )
            app.open_settings(MagicMock())

        assert app.config.hotkey == original_hotkey
        assert app.config.model == original_model
        assert app.config.ollama_model == original_ollama_model
        app.config.save.assert_not_called()
        app.transcriber.reload_model.assert_not_called()

    def test_whisper_model_invalid_value_ignored(self, app: Any) -> None:
        """Whisper モデルに不正な値が入力された場合は無視され通知が表示されること。"""
        original_model = app.config.model

        with patch("speakdrop.app.rumps.Window") as mock_window_cls:
            mock_window_cls.side_effect = _window_sequence(
                (1, "invalid-model"),  # 不正値: OK → 無視
                (0, ""),  # ホットキー キャンセル → 終了
            )
            with patch("speakdrop.app.rumps.notification") as mock_notification:
                app.open_settings(MagicMock())

        assert app.config.model == original_model
        app.transcriber.reload_model.assert_not_called()
        app.config.save.assert_not_called()
        mock_notification.assert_called_once()

    def test_whisper_empty_value_shows_notification_and_does_not_save(self, app: Any) -> None:
        """Whisper に空入力で OK の場合は保存せず通知のみ行うこと。"""
        original_model = app.config.model

        with patch("speakdrop.app.rumps.Window") as mock_window_cls:
            mock_window_cls.side_effect = _window_sequence(
                (1, ""),  # Whisper: 空入力で OK
                (0, ""),  # Hotkey: キャンセル → 終了
            )
            with patch("speakdrop.app.rumps.notification") as mock_notification:
                app.open_settings(MagicMock())

        assert app.config.model == original_model
        app.config.save.assert_not_called()
        app.transcriber.reload_model.assert_not_called()
        mock_notification.assert_called_once()

    def test_hotkey_change_does_not_start_listener_when_disabled(self, app: Any) -> None:
        """音声入力が無効な場合はホットキー変更後にリスナーを起動しないこと。"""
        app.config.enabled = False
        mock_listener = MagicMock()
        app.hotkey_listener = mock_listener

        with patch("speakdrop.app.rumps.Window") as mock_window_cls:
            mock_window_cls.side_effect = _window_sequence(
                (1, app.config.model),  # Whisper OK（変更なし）
                (1, "alt_l"),  # ホットキー OK
                (0, ""),  # Ollama キャンセル → 終了
            )
            with patch.object(app, "_start_hotkey_listener") as mock_start:
                with patch.object(app, "_is_valid_hotkey", return_value=True):
                    app.open_settings(MagicMock())

        mock_listener.stop.assert_called_once()
        mock_start.assert_not_called()
        assert app.config.hotkey == "alt_l"
        app.config.save.assert_called_once()

    def test_hotkey_change_invalid_value_shows_notification(self, app: Any) -> None:
        """無効なホットキーを入力した場合は通知が表示されリスナーが再起動されないこと。"""
        mock_listener = MagicMock()
        app.hotkey_listener = mock_listener
        original_hotkey = app.config.hotkey

        with (
            patch("speakdrop.app.rumps.Window") as mock_window_cls,
            patch.object(app, "_is_valid_hotkey", return_value=False),
            patch("speakdrop.app.rumps.notification") as mock_notification,
            patch.object(app, "_start_hotkey_listener") as mock_start,
        ):
            mock_window_cls.side_effect = _window_sequence(
                (1, app.config.model),  # Whisper OK（変更なし）
                (1, "xyz_invalid"),  # ホットキー 無効値
                (0, ""),  # Ollama キャンセル → 終了
            )
            app.open_settings(MagicMock())

        mock_notification.assert_called_once()
        mock_start.assert_not_called()
        assert app.config.hotkey == original_hotkey
        app.config.save.assert_not_called()

    def test_all_three_settings_changed(self, app: Any) -> None:
        """3ステップ全て変更した場合に各コンポーネントが更新されること。"""
        mock_listener = MagicMock()
        app.hotkey_listener = mock_listener

        with (
            patch("speakdrop.app.rumps.Window") as mock_window_cls,
            patch("speakdrop.app.TextProcessor") as mock_tp_cls,
            patch.object(app, "_start_hotkey_listener") as mock_start,
            patch.object(app, "_is_valid_hotkey", return_value=True),
        ):
            mock_tp_cls.return_value = MagicMock()
            mock_window_cls.side_effect = _window_sequence(
                (1, "large-v3"),  # Whisper 変更
                (1, "alt_l"),  # ホットキー 変更
                (1, "gemma3:4b"),  # Ollama 変更
            )
            app.open_settings(MagicMock())

        app.transcriber.reload_model.assert_called_once_with("large-v3")
        mock_listener.stop.assert_called_once()
        mock_start.assert_called_once()
        mock_tp_cls.assert_called_once_with(model="gemma3:4b")
        assert app.text_processor is mock_tp_cls.return_value
        assert app.config.model == "large-v3"
        assert app.config.hotkey == "alt_l"
        assert app.config.ollama_model == "gemma3:4b"
        assert app.config.save.call_count == 3
