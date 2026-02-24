# TASK-010: SpeakDropApp（app.py）

> **サブエージェント実行指示**
> このドキュメントは、タスク実行エージェントがサブエージェントにそのまま渡すことを想定しています。
> 以下の内容に従って実装を完了してください。

---

## あなたのタスク

**SpeakDropApp メインアプリケーション** を実装してください。

### 実装の目標

`rumps.App` を継承した `SpeakDropApp` クラスに、全モジュールを統合します。
AppState enum の定義、状態管理、メニューバーUI（状態表示・ON/OFF・設定・終了）、設定ダイアログを実装します。
ホットキー押下からテキスト挿入までのメインフローを非同期スレッドで実装します。

### 作成/変更するファイル

| 操作 | ファイルパス | 説明 |
|------|-------------|------|
| 変更 | `speakdrop/app.py` | SpeakDropApp メインアプリ実装 |

---

## 技術的コンテキスト

### 使用技術

- 言語: Python 3.11+
- メニューバーUI: rumps
- スレッド管理: threading
- 状態管理: enum.Enum

### 参照すべきファイル

全モジュール（TASK-002〜009で実装済み）:
- `@speakdrop/config.py` - Config クラス
- `@speakdrop/audio_recorder.py` - AudioRecorder クラス
- `@speakdrop/transcriber.py` - Transcriber クラス
- `@speakdrop/text_processor.py` - TextProcessor クラス
- `@speakdrop/clipboard_inserter.py` - ClipboardInserter クラス
- `@speakdrop/hotkey_listener.py` - HotkeyListener クラス
- `@speakdrop/permissions.py` - PermissionChecker クラス
- `@speakdrop/icons.py` - get_icon_title 関数

### 関連する設計書

- `@docs/sdd/design/design.md` の「SpeakDropApp」セクション（行170-216）
- `@docs/sdd/design/design.md` の「AppState」セクション（行146-166）
- `@docs/sdd/design/design.md` の「状態管理とスレッド設計」セクション（行507-521）
- `@docs/sdd/design/design.md` の「エラー処理戦略」セクション（行524-535）

### 関連する要件

- `@docs/sdd/requirements/stories/US-001.md` - プッシュトークによる音声入力
- `@docs/sdd/requirements/stories/US-003.md` - メニューバー常駐と設定
- `@docs/sdd/requirements/stories/US-004.md` - ホットキーの設定
- `@docs/sdd/requirements/stories/US-005.md` - 音声認識モデルの設定

---

## 受入基準

以下のすべての基準を満たしたら、このタスクは完了です：

- [ ] `speakdrop/app.py` が実装されている
- [ ] `AppState` enum が IDLE/RECORDING/PROCESSING を定義している
- [ ] `SpeakDropApp` が `rumps.App` を継承している
- [ ] メニューバーに「状態表示」「音声入力 ON/OFF」「設定...」「終了」が含まれる（REQ-012）
- [ ] `set_state()` でアイコンタイトルとメニュー状態を更新する（REQ-003, REQ-004, NFR-007）
- [ ] `on_hotkey_press()` が録音を開始する（REQ-001）
- [ ] `on_hotkey_release()` が録音停止・処理を開始する（REQ-002）
- [ ] `process_audio()` が別スレッドで認識→後処理→挿入を実行する
- [ ] `open_settings()` が設定ダイアログを表示する（REQ-013）
- [ ] 設定ダイアログでホットキー変更・モデル変更ができる（REQ-014, REQ-018）
- [ ] `uv run ruff check speakdrop/app.py` でエラー0件
- [ ] `uv run mypy speakdrop/app.py` でエラー0件

---

## 実装手順

### ステップ1: AppState enum と SpeakDropApp を実装

`speakdrop/app.py` を実装してください：

```python
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

    IDLE = auto()       # 待機中（ホットキー監視中）
    RECORDING = auto()  # 録音中（ホットキー押下中）
    PROCESSING = auto() # 処理中（認識・後処理・挿入中）


class SpeakDropApp(rumps.App):
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
        # モデル選択ダイアログ（REQ-018）
        model_options = [
            "kotoba-tech/kotoba-whisper-v1.0",
            "large-v3",
            "medium",
            "small",
        ]
        model_display = [
            "Kotoba Whisper (large-v3-ja, 推奨)",
            "large-v3",
            "medium",
            "small",
        ]
        current_idx = model_options.index(self.config.model) if self.config.model in model_options else 0
        model_menu_items = [
            rumps.MenuItem(f"{'* ' if i == current_idx else '  '}{name}")
            for i, name in enumerate(model_display)
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
                # モデル再読込（REQ-019）
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
```

### ステップ2: 品質チェック

```bash
cd <project-root>
uv run ruff check speakdrop/app.py
uv run mypy speakdrop/app.py
```

### ステップ3: コミット

```
feat: app.py - SpeakDropApp メインアプリ実装（全モジュール統合、AppState状態管理）
```

---

## 実装の詳細仕様

### AppState enum

```python
class AppState(Enum):
    IDLE = auto()       # 待機中
    RECORDING = auto()  # 録音中
    PROCESSING = auto() # 処理中
```

**状態遷移**:
```
IDLE ──[ホットキー押下]──> RECORDING
RECORDING ──[ホットキー離放]──> PROCESSING
PROCESSING ──[テキスト挿入完了]──> IDLE
PROCESSING ──[エラー発生]──> IDLE
```

### メニュー構成（REQ-012）

| メニュー項目 | 動作 |
|------------|------|
| 状態表示（"待機中"等） | 非クリック（状態表示のみ） |
| 音声入力 ON/OFF | HotkeyListenerの有効/無効切替 |
| 設定... | 設定ダイアログを表示（REQ-013） |
| 終了 | アプリ終了 |

### スレッド設計（設計書行507-521）

| スレッド | 役割 |
|---------|------|
| メインスレッド | rumps event loop、UI更新 |
| HotkeyListener | daemon thread、キーボードイベント監視 |
| process_audio | worker thread、音声認識・後処理・挿入 |

---

## 注意事項

- `set_state()` はメインスレッドから呼ぶこと（rumpsの制約）
- `process_audio()` は別スレッドで実行し、完了後に `set_state(AppState.IDLE)` を呼ぶこと
- エラー発生時も `finally` ブロックで `set_state(AppState.IDLE)` を必ず実行すること
- 設定ダイアログは `rumps.Window` を使用すること
- `quit_button=None` で rumps のデフォルト終了ボタンを無効化し、独自の「終了」を使うこと

---

## 基本情報（メタデータ）

| 項目 | 値 |
|------|-----|
| **タスクID** | TASK-010 |
| **ステータス** | `DONE` |
| **推定工数** | 60分 |
| **依存関係** | TASK-002〜009 すべて完了後 |
| **対応要件** | REQ-003, REQ-004, REQ-010, REQ-011, REQ-012, REQ-013, REQ-014, REQ-018, REQ-019 |
| **対応設計** | SpeakDropApp セクション（設計書行170-216）, AppState（行146-166） |

---

## 情報の明確性チェック

### 明示された情報

- [x] 継承クラス: rumps.App
- [x] AppState: IDLE/RECORDING/PROCESSING（Enum）
- [x] メニュー構成: 状態表示・ON/OFF・設定・終了（REQ-012）
- [x] 状態遷移: IDLE→RECORDING→PROCESSING→IDLE
- [x] スレッド: プロセス処理は別スレッド
- [x] 設定ダイアログ: rumps.Window を使用

### 未確認/要確認の情報

| 項目 | 現状の理解 | 確認状況 |
|------|-----------|----------|
| rumps.Window の使い方 | モデル名を直接入力する形式を採用 | [x] rumps のドキュメントで確認が必要 |
| set_state()のスレッド安全性 | rumpsはメインスレッドから呼ぶ必要あり | [x] process_audioからset_stateを呼ぶため、rumps.Timerまたは直接呼び出しで検証が必要 |

---

## 作業ログ（実装時に記入）

### 2026-02-24
- **作業内容**: SpeakDropApp（app.py）の実装と tests/test_app.py の作成（TDD）
- **発生した問題**: (1) mypy が rumps.App サブクラス化で misc エラー。(2) icons.py の _HasName Protocol の name が read-only で arg-type エラー
- **解決方法**: (1) type: ignore[misc] を付与。(2) icons.py の _HasName.name をプロパティ形式の Protocol に修正
- **コミットハッシュ**: 33e87f8
