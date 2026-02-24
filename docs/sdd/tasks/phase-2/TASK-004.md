# TASK-004: Transcriber モジュール（TDD）

> **サブエージェント実行指示**
> このドキュメントは、タスク実行エージェントがサブエージェントにそのまま渡すことを想定しています。
> 以下の内容に従って実装を完了してください。

---

## あなたのタスク

**Transcriber モジュール** をTDD方式で実装してください。

### 実装の目標

`faster-whisper` を使って日本語音声認識を行うモジュールを実装します。
モデルの遅延ロード、4種類のモデル対応、モデル再読込機能を実装します。
TDD原則に従い、`faster_whisper.WhisperModel` はpytest-mockでモックします。

### 作成/変更するファイル

| 操作 | ファイルパス | 説明 |
|------|-------------|------|
| 作成 | `/Users/tsk/Sync/git/SpeakDrop/tests/test_transcriber.py` | テストファイル（先行作成） |
| 変更 | `/Users/tsk/Sync/git/SpeakDrop/speakdrop/transcriber.py` | Transcriber モジュール本実装 |

---

## 技術的コンテキスト

### 使用技術

- 言語: Python 3.11+
- テストフレームワーク: pytest + pytest-mock
- 音声認識ライブラリ: faster-whisper
- 数値計算: numpy

### 参照すべきファイル

- `@/Users/tsk/Sync/git/SpeakDrop/speakdrop/transcriber.py` - 現在のスタブ

### 関連する設計書

- `@/Users/tsk/Sync/git/SpeakDrop/docs/sdd/design/design.md` の「Transcriber」セクション（行247-284）

### 関連する要件

- `@/Users/tsk/Sync/git/SpeakDrop/docs/sdd/requirements/stories/US-001.md` - プッシュトークによる音声入力
- `@/Users/tsk/Sync/git/SpeakDrop/docs/sdd/requirements/stories/US-005.md` - 音声認識モデルの設定

---

## 受入基準

以下のすべての基準を満たしたら、このタスクは完了です：

- [ ] `tests/test_transcriber.py` が作成されている（テストが7件以上）
- [ ] `speakdrop/transcriber.py` が実装されている
- [ ] デフォルトモデルIDが `"kotoba-tech/kotoba-whisper-v1.0"` である
- [ ] モデルが遅延ロード（初回 `transcribe()` 呼び出し時のみロード）される
- [ ] `transcribe()` が音声データを文字列として返す
- [ ] 認識結果が空文字の場合に空文字を返す
- [ ] `reload_model()` でモデルを再読込できる
- [ ] 4種モデル（kotoba, large-v3, medium, small）への対応
- [ ] `WhisperModel` のモックによりテストが環境なしで動作する
- [ ] `uv run pytest tests/test_transcriber.py -v` で全テストパス
- [ ] `uv run ruff check speakdrop/transcriber.py tests/test_transcriber.py` でエラー0件
- [ ] `uv run mypy speakdrop/transcriber.py` でエラー0件

---

## 実装手順

### ステップ1: テストを先に作成（TDD）

`/Users/tsk/Sync/git/SpeakDrop/tests/test_transcriber.py` を作成してください：

```python
"""Transcriber モジュールのテスト。"""
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from speakdrop.transcriber import Transcriber


class TestTranscriberInit:
    """Transcriber の初期化テスト。"""

    def test_default_model_id(self) -> None:
        """デフォルトモデルIDが 'kotoba-tech/kotoba-whisper-v1.0' であること。"""
        transcriber = Transcriber()
        assert transcriber._model_id == "kotoba-tech/kotoba-whisper-v1.0"

    def test_model_not_loaded_at_init(self) -> None:
        """初期化時にモデルがロードされないこと（遅延ロード）。"""
        transcriber = Transcriber()
        assert transcriber._model is None

    def test_custom_model_id(self) -> None:
        """カスタムモデルIDを指定できること。"""
        transcriber = Transcriber(model_id="small")
        assert transcriber._model_id == "small"


class TestTranscriberTranscribe:
    """Transcriber.transcribe() のテスト。"""

    @patch("speakdrop.transcriber.WhisperModel")
    def test_transcribe_loads_model_on_first_call(
        self, mock_whisper_model: MagicMock
    ) -> None:
        """transcribe() 初回呼び出し時にモデルをロードすること。"""
        mock_model = MagicMock()
        mock_model.transcribe.return_value = (iter([]), MagicMock())
        mock_whisper_model.return_value = mock_model

        transcriber = Transcriber()
        audio = np.zeros(16000, dtype=np.int16)
        transcriber.transcribe(audio)

        mock_whisper_model.assert_called_once()

    @patch("speakdrop.transcriber.WhisperModel")
    def test_transcribe_does_not_reload_model(
        self, mock_whisper_model: MagicMock
    ) -> None:
        """transcribe() 2回目以降はモデルをロードしないこと。"""
        mock_model = MagicMock()
        mock_model.transcribe.return_value = (iter([]), MagicMock())
        mock_whisper_model.return_value = mock_model

        transcriber = Transcriber()
        audio = np.zeros(16000, dtype=np.int16)
        transcriber.transcribe(audio)
        transcriber.transcribe(audio)

        assert mock_whisper_model.call_count == 1

    @patch("speakdrop.transcriber.WhisperModel")
    def test_transcribe_returns_string(self, mock_whisper_model: MagicMock) -> None:
        """transcribe() が文字列を返すこと。"""
        mock_segment = MagicMock()
        mock_segment.text = "こんにちは"
        mock_model = MagicMock()
        mock_model.transcribe.return_value = (iter([mock_segment]), MagicMock())
        mock_whisper_model.return_value = mock_model

        transcriber = Transcriber()
        audio = np.zeros(16000, dtype=np.int16)
        result = transcriber.transcribe(audio)

        assert isinstance(result, str)
        assert result == "こんにちは"

    @patch("speakdrop.transcriber.WhisperModel")
    def test_transcribe_joins_multiple_segments(
        self, mock_whisper_model: MagicMock
    ) -> None:
        """複数セグメントを結合して返すこと。"""
        seg1 = MagicMock()
        seg1.text = "こんにちは、"
        seg2 = MagicMock()
        seg2.text = "世界。"
        mock_model = MagicMock()
        mock_model.transcribe.return_value = (iter([seg1, seg2]), MagicMock())
        mock_whisper_model.return_value = mock_model

        transcriber = Transcriber()
        audio = np.zeros(16000, dtype=np.int16)
        result = transcriber.transcribe(audio)

        assert result == "こんにちは、世界。"

    @patch("speakdrop.transcriber.WhisperModel")
    def test_transcribe_returns_empty_string_for_empty_result(
        self, mock_whisper_model: MagicMock
    ) -> None:
        """認識結果が空の場合、空文字を返すこと。"""
        mock_model = MagicMock()
        mock_model.transcribe.return_value = (iter([]), MagicMock())
        mock_whisper_model.return_value = mock_model

        transcriber = Transcriber()
        audio = np.zeros(16000, dtype=np.int16)
        result = transcriber.transcribe(audio)

        assert result == ""

    @patch("speakdrop.transcriber.WhisperModel")
    def test_transcribe_uses_japanese_language(
        self, mock_whisper_model: MagicMock
    ) -> None:
        """transcribe() が language='ja' を指定すること。"""
        mock_model = MagicMock()
        mock_model.transcribe.return_value = (iter([]), MagicMock())
        mock_whisper_model.return_value = mock_model

        transcriber = Transcriber()
        audio = np.zeros(16000, dtype=np.int16)
        transcriber.transcribe(audio)

        call_kwargs = mock_model.transcribe.call_args.kwargs
        assert call_kwargs.get("language") == "ja"


class TestTranscriberReloadModel:
    """Transcriber.reload_model() のテスト。"""

    @patch("speakdrop.transcriber.WhisperModel")
    def test_reload_model_changes_model_id(
        self, mock_whisper_model: MagicMock
    ) -> None:
        """reload_model() がモデルIDを変更すること。"""
        mock_model = MagicMock()
        mock_whisper_model.return_value = mock_model

        transcriber = Transcriber(model_id="small")
        transcriber.reload_model("medium")

        assert transcriber._model_id == "medium"

    @patch("speakdrop.transcriber.WhisperModel")
    def test_reload_model_resets_model_instance(
        self, mock_whisper_model: MagicMock
    ) -> None:
        """reload_model() が古いモデルインスタンスをリセットすること。"""
        mock_model = MagicMock()
        mock_model.transcribe.return_value = (iter([]), MagicMock())
        mock_whisper_model.return_value = mock_model

        transcriber = Transcriber()
        audio = np.zeros(16000, dtype=np.int16)
        transcriber.transcribe(audio)  # モデルをロード

        assert transcriber._model is not None
        transcriber.reload_model("small")
        assert transcriber._model is None  # リセット済み
```

テストを実行して失敗を確認：

```bash
cd /Users/tsk/Sync/git/SpeakDrop
uv run pytest tests/test_transcriber.py -v
```

コミット：

```
test: test_transcriber.py - Transcriber モジュールのTDDテスト追加
```

### ステップ2: Transcriber モジュールを実装

`/Users/tsk/Sync/git/SpeakDrop/speakdrop/transcriber.py` を実装してください：

```python
"""音声認識モジュール。

faster-whisper を使って日本語音声認識を行う。
モデルは遅延ロード（初回transcribe()呼び出し時）。
"""
import numpy as np
from faster_whisper import WhisperModel


class Transcriber:
    """faster-whisper による音声認識クラス。"""

    DEFAULT_MODEL_ID = "kotoba-tech/kotoba-whisper-v1.0"

    def __init__(self, model_id: str = DEFAULT_MODEL_ID) -> None:
        """Transcriber を初期化する。

        Args:
            model_id: 使用するWhisperモデルのID
        """
        self._model: WhisperModel | None = None
        self._model_id: str = model_id

    def _load_model(self) -> None:
        """モデルを遅延ロードする（NFR-003対応）。"""
        self._model = WhisperModel(
            self._model_id,
            device="auto",
            compute_type="int8",
        )

    def transcribe(self, audio: np.ndarray) -> str:
        """音声データを認識してテキストを返す。

        初回呼び出し時にモデルをロード（遅延ロード）。

        Args:
            audio: 録音音声データ（np.ndarray, dtype=int16, 16kHz）

        Returns:
            認識結果テキスト。認識できない場合は空文字。
        """
        if self._model is None:
            self._load_model()

        assert self._model is not None
        # int16 → float32 に正規化
        audio_float = audio.astype(np.float32) / 32768.0

        segments, _ = self._model.transcribe(
            audio_float,
            language="ja",
            beam_size=1,
        )
        return "".join(segment.text for segment in segments)

    def reload_model(self, model_id: str) -> None:
        """モデルを変更して再読み込みする（REQ-019）。

        Args:
            model_id: 新しいモデルID
        """
        self._model_id = model_id
        self._model = None  # 次回 transcribe() 時に遅延ロード
```

### ステップ3: テストがパスすることを確認

```bash
cd /Users/tsk/Sync/git/SpeakDrop
uv run pytest tests/test_transcriber.py -v
uv run ruff check speakdrop/transcriber.py tests/test_transcriber.py
uv run mypy speakdrop/transcriber.py
```

### ステップ4: コミット

```
feat: transcriber.py - Transcriber 実装（遅延ロード・4種モデル対応、REQ-018/019）
```

---

## 実装の詳細仕様

### 対応モデル一覧（REQ-018）

| モデル識別子 | 表示名 | 目安サイズ | デフォルト |
|------------|--------|----------|-----------|
| `kotoba-tech/kotoba-whisper-v1.0` | large-v3-ja (Kotoba Whisper) | 約4GB | はい |
| `large-v3` | large-v3 | 約4GB | - |
| `medium` | medium | 約2GB | - |
| `small` | small | 約1GB | - |

### 入出力仕様

**`Transcriber.transcribe(audio: np.ndarray) -> str`:**
- 入力: 音声データ（np.ndarray, dtype=int16, 16kHz, モノラル）
- 出力: 認識テキスト（str）。認識失敗 or 無音の場合は空文字

**`Transcriber.reload_model(model_id: str) -> None`:**
- 入力: 新しいモデルID（str）
- 出力: なし
- 副作用: `_model_id` を更新、`_model` を None にリセット

### エラー処理

- モデルダウンロード中の例外: 上位（app.py）で処理
- 認識結果が空: 空文字を返す（app.py でスキップ判定）

---

## 注意事項

- `from faster_whisper import WhisperModel` をモジュールレベルでインポートすること（テストでモック可能にするため）
- テストでは `@patch("speakdrop.transcriber.WhisperModel")` でモックすること
- `audio.astype(np.float32) / 32768.0` で int16 → float32 への正規化が必要
- `device="auto"` でApple Silicon MPS / CPU を自動選択（NFR-008対応）
- `compute_type="int8"` で量子化推論によるメモリ効率化（NFR-001対応）

---

## 基本情報（メタデータ）

| 項目 | 値 |
|------|-----|
| **タスクID** | TASK-004 |
| **ステータス** | `IN_PROGRESS` |
| **推定工数** | 30分 |
| **依存関係** | [TASK-001](../phase-1/TASK-001.md) @../phase-1/TASK-001.md |
| **対応要件** | REQ-002, REQ-018, REQ-019, REQ-020, NFR-001, NFR-003 |
| **対応設計** | Transcriber セクション（設計書行247-284） |

---

## 情報の明確性チェック

### 明示された情報

- [x] 使用ライブラリ: faster-whisper (WhisperModel)
- [x] デフォルトモデル: kotoba-tech/kotoba-whisper-v1.0
- [x] 遅延ロード: 初回transcribe()時にロード
- [x] 言語: "ja"（日本語固定）
- [x] device: "auto"（MPS/CPU自動選択）
- [x] compute_type: "int8"（量子化推論）

### 未確認/要確認の情報

| 項目 | 現状の理解 | 確認状況 |
|------|-----------|----------|
| REQ-020: ダウンロード進捗通知 | reload_model内でrumps.notification()を呼ぶ | [x] app.pyとの統合時に実装（このタスクでは基本機能のみ） |

---

## 作業ログ（実装時に記入）

### YYYY-MM-DD
- **作業内容**:
- **発生した問題**:
- **解決方法**:
- **コミットハッシュ**:
