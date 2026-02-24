"""メインアプリケーションモジュール。

rumps.App を継承した SpeakDropApp クラスで全モジュールを統合する。
"""
from __future__ import annotations

import threading
from enum import Enum, auto

import numpy as np
import rumps

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

    IDLE = auto()        # 待機中（ホットキー監視中）
    RECORDING = auto()   # 録音中（ホットキー押下中）
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
        self.text_processor = TextProcessor()
        self.clipboard_inserter = ClipboardInserter()
        self.permission_checker = PermissionChecker()

        # 状態管理
        self.state = AppState.IDLE

        # メニュー構成（REQ-012）
        self.status_item = rumps.MenuItem("待機中", callback=None)
        self.status_item.set_callback(None)  # クリック不可

        self.toggle_item = rumps.MenuItem(
            "音声入力 ON",
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

    def set_state(self, state: AppState) -> None:
        """状態を遷移し、アイコンとメニューを更新する（NFR-007: 200ms以内）。

        Args:
            state: 新しいアプリケーション状態
        """
        self.state = state
        self.title = get_icon_title(state)

        state_labels = {
            AppState.IDLE: "待機中",
            AppState.RECORDING: "録音中...",
            AppState.PROCESSING: "処理中...",
        }
        self.status_item.title = state_labels[state]

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
        """音声認識→テキスト後処理→挿入を実行する（別スレッドで動作）。

        Args:
            audio: 録音音声データ
        """
        try:
            text = self.transcriber.transcribe(audio)
            if not text.strip():
                return

            processed = self.text_processor.process(text)
            self.clipboard_inserter.insert(processed)
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
        self.config.enabled = not self.config.enabled
        self.config.save()

        if self.config.enabled:
            self._start_hotkey_listener()
            self.toggle_item.title = "音声入力 ON"
        else:
            if hasattr(self, "hotkey_listener"):
                self.hotkey_listener.stop()
            self.toggle_item.title = "音声入力 OFF"

    def open_settings(self, _: rumps.MenuItem) -> None:
        """設定ダイアログを表示する（REQ-013）。"""
        model_options = [
            "kotoba-tech/kotoba-whisper-v1.0",
            "large-v3",
            "medium",
            "small",
        ]

        response = rumps.Window(
            message="モデルを選択してください:",
            title="SpeakDrop 設定",
            default_text=self.config.model,
            ok="OK",
            cancel="キャンセル",
        ).run()

        if response.clicked and response.text in model_options:
            new_model = response.text
            if new_model != self.config.model:
                self.config.model = new_model
                self.config.save()
                rumps.notification(
                    title="SpeakDrop",
                    subtitle="モデルを変更しています",
                    message=f"{new_model} を読み込みます（初回使用時にダウンロード）",
                )
                self.transcriber.reload_model(new_model)

    def _quit(self, _: rumps.MenuItem) -> None:
        """アプリケーションを終了する。"""
        if hasattr(self, "hotkey_listener"):
            self.hotkey_listener.stop()
        rumps.quit_application()
