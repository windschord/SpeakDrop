"""メインアプリケーションモジュール。

rumps.App を継承した SpeakDropApp クラスで全モジュールを統合する。
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from enum import Enum, auto

import numpy as np
import rumps
from PyObjCTools import AppHelper

from speakdrop.audio_recorder import AudioRecorder
from speakdrop.clipboard_inserter import ClipboardInserter
from speakdrop.config import Config
from speakdrop.hotkey_listener import HotkeyListener
from speakdrop.icons import get_icon_title
from speakdrop.permissions import PermissionChecker
from speakdrop.text_processor import TextProcessor
from speakdrop.transcriber import Transcriber


class AppState(Enum):
    """アプリケーションの状態を表す列挙型。"""

    IDLE = auto()  # 待機中（ホットキー監視中）
    RECORDING = auto()  # 録音中（ホットキー押下中）
    PROCESSING = auto()  # 処理中（認識・後処理・挿入中）


class SpeakDropApp(rumps.App):  # type: ignore[misc]
    """SpeakDrop メニューバーアプリケーション。"""

    def __init__(self) -> None:
        """SpeakDropApp を初期化する。"""
        super().__init__("SpeakDrop", quit_button=None)

        # 設定読み込み（REQ-017）
        self.config = Config().load()

        # コンポーネント初期化
        self.audio_recorder = AudioRecorder()
        self.transcriber = Transcriber(model_id=self.config.model)
        self.text_processor = TextProcessor(model=self.config.ollama_model)
        self.clipboard_inserter = ClipboardInserter()
        self.permission_checker = PermissionChecker()

        # 状態管理
        self.state = AppState.IDLE

        # メニュー構成（REQ-012）
        self.status_item = rumps.MenuItem("待機中", callback=None)
        self.status_item.set_callback(None)  # クリック不可

        self.toggle_item = rumps.MenuItem(
            "音声入力 ON" if self.config.enabled else "音声入力 OFF",
            callback=self._toggle_enabled,
        )

        self.menu = [
            self.status_item,
            None,  # セパレーター
            self.toggle_item,
            rumps.MenuItem("設定...", callback=self.open_settings),
            None,  # セパレーター
            rumps.MenuItem("終了", callback=self._quit),
        ]

        # メニューバーアイコン（絵文字タイトル）
        self.title = get_icon_title(self.state)

        # 権限確認（REQ-021, REQ-022）
        mic_ok = self.permission_checker.check_microphone()
        ax_ok = self.permission_checker.check_accessibility()

        if not mic_ok or not ax_ok:
            self.config.enabled = False
            self.toggle_item.title = "音声入力 OFF（権限エラー）"

        # HotkeyListener を非同期スレッドで起動
        if self.config.enabled:
            self._start_hotkey_listener()

    def check_permissions(self) -> bool:
        """マイク・アクセシビリティ権限を確認する（REQ-021, REQ-022）。

        Returns:
            すべての権限が許可されている場合は True、そうでない場合は False
        """
        mic_ok = self.permission_checker.check_microphone()
        ax_ok = self.permission_checker.check_accessibility()
        return mic_ok and ax_ok

    def _start_hotkey_listener(self) -> None:
        """HotkeyListener を起動する。"""
        self.hotkey_listener = HotkeyListener(
            hotkey_key=self.config.hotkey,
            on_press=self.on_hotkey_press,
            on_release=self.on_hotkey_release,
        )
        self.hotkey_listener.start()

    def _apply_state_ui(self, state: AppState) -> None:
        """状態に応じてUIを更新する（メインスレッドで実行される）。"""
        self.title = get_icon_title(state)
        state_labels = {
            AppState.IDLE: "待機中",
            AppState.RECORDING: "録音中...",
            AppState.PROCESSING: "処理中...",
        }
        self.status_item.title = state_labels[state]

    def set_state(self, state: AppState) -> None:
        """状態を遷移し、UIをメインスレッドで更新する（NFR-007: 200ms以内）。"""
        self.state = state
        AppHelper.callAfter(self._apply_state_ui, state)

    def on_hotkey_press(self) -> None:
        """ホットキー押下コールバック（REQ-001）。"""
        if not self.config.enabled:
            return
        if self.state != AppState.IDLE:
            return
        self.set_state(AppState.RECORDING)
        self.audio_recorder.start_recording()

    def on_hotkey_release(self) -> None:
        """ホットキー離放コールバック（REQ-002）。"""
        if self.state != AppState.RECORDING:
            return
        audio = self.audio_recorder.stop_recording()
        self.set_state(AppState.PROCESSING)
        thread = threading.Thread(
            target=self.process_audio,
            args=(audio,),
            daemon=True,
        )
        thread.start()

    def process_audio(self, audio: np.ndarray) -> None:
        """音声認識→テキスト後処理を実行する（別スレッドで動作）。

        Args:
            audio: 録音音声データ
        """
        try:
            text = self.transcriber.transcribe(audio)
            if not text.strip():
                self.set_state(AppState.IDLE)
                return

            processed = self.text_processor.process(text)
            AppHelper.callAfter(self._finish_processing, processed)
        except Exception as e:
            AppHelper.callAfter(
                rumps.notification,
                title="SpeakDrop エラー",
                subtitle="音声処理に失敗しました",
                message=str(e),
            )
            self.set_state(AppState.IDLE)

    def _finish_processing(self, text: str) -> None:
        """クリップボード挿入と状態リセットをメインスレッドで実行する。

        Args:
            text: 挿入するテキスト
        """
        try:
            self.clipboard_inserter.insert(text)
        except Exception as e:
            rumps.notification(
                title="SpeakDrop エラー",
                subtitle="音声処理に失敗しました",
                message=str(e),
            )
        finally:
            self.set_state(AppState.IDLE)

    def _toggle_enabled(self, sender: rumps.MenuItem) -> None:
        """音声入力の有効/無効を切り替える（REQ-012）。"""
        if not self.config.enabled and not self.check_permissions():
            rumps.notification(
                title="SpeakDrop",
                subtitle="権限が必要です",
                message="マイクとアクセシビリティの権限を許可してください",
            )
            return

        self.config.enabled = not self.config.enabled
        self.config.save()

        if self.config.enabled:
            self._start_hotkey_listener()
            self.toggle_item.title = "音声入力 ON"
        else:
            if hasattr(self, "hotkey_listener"):
                self.hotkey_listener.stop()
            self.toggle_item.title = "音声入力 OFF"

    def _show_setting_dialog(
        self,
        *,
        message: str,
        title: str,
        default_text: str,
        validator: Callable[[str], bool] | None = None,
        on_save: Callable[[str], None],
        on_invalid: Callable[[], None] | None = None,
    ) -> bool:
        """共通設定ダイアログ表示ヘルパー。

        Returns:
            True: OK を押した場合
            False: キャンセルした場合
        """
        response = rumps.Window(
            message=message,
            title=title,
            default_text=default_text,
            ok="OK",
            cancel="キャンセル",
        ).run()
        if not response.clicked:
            return False
        new_value = response.text.strip() if response.text else ""
        if new_value:
            if validator is None or validator(new_value):
                on_save(new_value)
            elif on_invalid is not None:
                on_invalid()
        elif on_invalid is not None:
            on_invalid()
        return True

    def _settings_whisper(self) -> bool:
        """Whisper モデル設定ダイアログを表示する。キャンセル時は False を返す。"""
        whisper_options = [
            "kotoba-tech/kotoba-whisper-v1.0",
            "large-v3",
            "medium",
            "small",
        ]
        return self._show_setting_dialog(
            message=(
                "Whisper モデルを選択してください:\n" + "\n".join(f"  {o}" for o in whisper_options)
            ),
            title="SpeakDrop 設定 (1/3)",
            default_text=self.config.model,
            validator=lambda v: v in whisper_options,
            on_save=self._apply_whisper_model,
            on_invalid=lambda: rumps.notification(
                title="SpeakDrop",
                subtitle="無効なWhisperモデルです",
                message="候補一覧から選択してください",
            ),
        )

    def _apply_whisper_model(self, model: str) -> None:
        """Whisper モデルを適用する。"""
        if model != self.config.model:
            self.config.model = model
            self.config.save()
            rumps.notification(
                title="SpeakDrop",
                subtitle="モデルを変更しています",
                message=f"{model} を読み込みます（初回使用時にダウンロード）",
            )
            self.transcriber.reload_model(model)

    def _is_valid_hotkey(self, key: str) -> bool:
        """ホットキー文字列が pynput.keyboard.Key に存在するか確認する。"""
        try:
            from pynput.keyboard import Key  # noqa: PLC0415

            return key in Key.__members__
        except ImportError:
            return False

    def _settings_hotkey(self) -> bool:
        """ホットキー設定ダイアログを表示する。キャンセル時は False を返す。"""
        current_hotkey = self.config.hotkey
        return self._show_setting_dialog(
            message=(
                "ホットキーを入力してください:\n"
                "例: alt_r=右Option, alt_l=左Option, ctrl_r=右Control, ctrl_l=左Control"
            ),
            title="SpeakDrop 設定 (2/3)",
            default_text=current_hotkey,
            validator=lambda v: v == current_hotkey or self._is_valid_hotkey(v),
            on_save=self._apply_hotkey,
            on_invalid=lambda: rumps.notification(
                title="SpeakDrop",
                subtitle="無効なホットキーです",
                message="有効なキー名を入力してください（例: alt_r, ctrl_l）",
            ),
        )

    def _apply_hotkey(self, hotkey: str) -> None:
        """ホットキーを適用する。"""
        if hotkey != self.config.hotkey:
            self.config.hotkey = hotkey
            self.config.save()
            if hasattr(self, "hotkey_listener"):
                self.hotkey_listener.stop()
            if self.config.enabled:
                self._start_hotkey_listener()

    def _settings_ollama(self) -> bool:
        """Ollama モデル設定ダイアログを表示する。キャンセル時は False を返す。"""
        return self._show_setting_dialog(
            message=(
                "Ollama モデルを入力してください:\n"
                "例: qwen2.5:7b, qwen2.5:3b, gemma3:4b, llama3.2:3b"
            ),
            title="SpeakDrop 設定 (3/3)",
            default_text=self.config.ollama_model,
            on_save=self._apply_ollama_model,
        )

    def _apply_ollama_model(self, model: str) -> None:
        """Ollama モデルを適用する。"""
        if model != self.config.ollama_model:
            self.config.ollama_model = model
            self.config.save()
            self.text_processor = TextProcessor(model=model)
            rumps.notification(
                title="SpeakDrop",
                subtitle="Ollama モデルを変更しました",
                message=f"{model} を使用します",
            )

    def open_settings(self, _: rumps.MenuItem) -> None:
        """設定ダイアログを表示する（REQ-013）。

        3つのダイアログをシーケンシャルに表示する:
        1. Whisper モデル選択
        2. ホットキー設定
        3. Ollama モデル設定
        """
        if not self._settings_whisper():
            return
        if not self._settings_hotkey():
            return
        self._settings_ollama()

    def _quit(self, _: rumps.MenuItem) -> None:
        """アプリケーションを終了する。"""
        if hasattr(self, "hotkey_listener"):
            self.hotkey_listener.stop()
        rumps.quit_application()
