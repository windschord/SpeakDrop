# TASK-003: AudioRecorder モジュール（TDD）

> **サブエージェント実行指示**
> このドキュメントは、タスク実行エージェントがサブエージェントにそのまま渡すことを想定しています。
> 以下の内容に従って実装を完了してください。

---

## あなたのタスク

**AudioRecorder モジュール** をTDD方式で実装してください。

### 実装の目標

`sounddevice` を使って16kHz/Mono/16bit PCM形式でマイク録音を行うモジュールを実装します。
TDD原則に従い、まずテストを作成・コミットし、その後テストをパスする実装を行います。
`sounddevice` はpytest-mockでモックし、macOS環境なしでテストが動作するようにします。

### 作成/変更するファイル

| 操作 | ファイルパス | 説明 |
|------|-------------|------|
| 作成 | `tests/test_audio_recorder.py` | テストファイル（先行作成） |
| 変更 | `speakdrop/audio_recorder.py` | AudioRecorder モジュール本実装 |

---

## 技術的コンテキスト

### 使用技術

- 言語: Python 3.11+
- テストフレームワーク: pytest + pytest-mock
- 音声録音ライブラリ: sounddevice
- 数値計算: numpy

### 参照すべきファイル

- `@speakdrop/audio_recorder.py` - 現在のスタブ

### 関連する設計書

- `@docs/sdd/design/design.md` の「AudioRecorder」セクション（行219-244）

### 関連する要件

- `@docs/sdd/requirements/stories/US-001.md` - プッシュトークによる音声入力

---

## 受入基準

以下のすべての基準を満たしたら、このタスクは完了です：

- [ ] `tests/test_audio_recorder.py` が作成されている（テストが6件以上）
- [ ] `speakdrop/audio_recorder.py` が実装されている
- [ ] `AudioRecorder.SAMPLE_RATE == 16000`（NFR-004）
- [ ] `AudioRecorder.CHANNELS == 1`（NFR-004）
- [ ] `AudioRecorder.DTYPE == "int16"`（NFR-004）
- [ ] `start_recording()` が sounddevice.InputStream を開始する
- [ ] `stop_recording()` が録音データを `np.ndarray` で返す
- [ ] `stop_recording()` 後にバッファがクリアされる（NFR-006）
- [ ] `sounddevice` のモックによりテストがmacOS環境なしで動作する
- [ ] `uv run pytest tests/test_audio_recorder.py -v` で全テストパス
- [ ] `uv run ruff check speakdrop/audio_recorder.py tests/test_audio_recorder.py` でエラー0件
- [ ] `uv run mypy speakdrop/audio_recorder.py` でエラー0件

---

## 実装手順

### ステップ1: テストを先に作成（TDD）

`tests/test_audio_recorder.py` を作成してください：

```python
"""AudioRecorder モジュールのテスト。"""
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from speakdrop.audio_recorder import AudioRecorder


class TestAudioRecorderConstants:
    """AudioRecorder の定数テスト（NFR-004）。"""

    def test_sample_rate(self) -> None:
        """サンプルレートが16kHzであること。"""
        assert AudioRecorder.SAMPLE_RATE == 16000

    def test_channels(self) -> None:
        """チャンネル数がモノラル（1）であること。"""
        assert AudioRecorder.CHANNELS == 1

    def test_dtype(self) -> None:
        """データ型が int16 であること。"""
        assert AudioRecorder.DTYPE == "int16"


class TestAudioRecorderRecording:
    """録音開始・停止のテスト。"""

    @patch("speakdrop.audio_recorder.sd")
    def test_start_recording_opens_stream(self, mock_sd: MagicMock) -> None:
        """start_recording() が sounddevice.InputStream を開始すること。"""
        mock_stream = MagicMock()
        mock_sd.InputStream.return_value.__enter__ = MagicMock(return_value=mock_stream)
        mock_sd.InputStream.return_value.__exit__ = MagicMock(return_value=False)

        recorder = AudioRecorder()
        recorder.start_recording()

        mock_sd.InputStream.assert_called_once()
        call_kwargs = mock_sd.InputStream.call_args.kwargs
        assert call_kwargs["samplerate"] == 16000
        assert call_kwargs["channels"] == 1
        assert call_kwargs["dtype"] == "int16"

    @patch("speakdrop.audio_recorder.sd")
    def test_stop_recording_returns_ndarray(self, mock_sd: MagicMock) -> None:
        """stop_recording() が np.ndarray を返すこと。"""
        mock_sd.InputStream.return_value = MagicMock()

        recorder = AudioRecorder()
        recorder.start_recording()
        # テスト用の音声データを直接注入
        recorder._frames = [np.zeros(1600, dtype=np.int16)]

        result = recorder.stop_recording()

        assert isinstance(result, np.ndarray)
        assert result.dtype == np.int16

    @patch("speakdrop.audio_recorder.sd")
    def test_stop_recording_clears_buffer(self, mock_sd: MagicMock) -> None:
        """stop_recording() 後にバッファがクリアされること（NFR-006）。"""
        mock_sd.InputStream.return_value = MagicMock()

        recorder = AudioRecorder()
        recorder.start_recording()
        recorder._frames = [np.zeros(1600, dtype=np.int16)]
        recorder.stop_recording()

        assert len(recorder._frames) == 0

    @patch("speakdrop.audio_recorder.sd")
    def test_stop_recording_concatenates_frames(self, mock_sd: MagicMock) -> None:
        """stop_recording() が複数フレームを結合して返すこと。"""
        mock_sd.InputStream.return_value = MagicMock()

        recorder = AudioRecorder()
        recorder.start_recording()
        # 2フレーム分のデータ
        frame1 = np.zeros(1600, dtype=np.int16)
        frame2 = np.ones(1600, dtype=np.int16)
        recorder._frames = [frame1, frame2]

        result = recorder.stop_recording()

        assert len(result) == 3200

    @patch("speakdrop.audio_recorder.sd")
    def test_audio_callback_appends_frame(self, mock_sd: MagicMock) -> None:
        """音声コールバックがフレームをバッファに追加すること。"""
        mock_sd.InputStream.return_value = MagicMock()

        recorder = AudioRecorder()
        recorder.start_recording()

        # コールバックを直接呼び出す
        indata = np.zeros((1600, 1), dtype=np.int16)
        recorder._audio_callback(indata, 1600, None, None)

        assert len(recorder._frames) == 1

    @patch("speakdrop.audio_recorder.sd")
    def test_stop_without_start_returns_empty(self, mock_sd: MagicMock) -> None:
        """start_recording() なしで stop_recording() を呼んだ場合、空の配列を返すこと。"""
        recorder = AudioRecorder()
        result = recorder.stop_recording()

        assert isinstance(result, np.ndarray)
        assert len(result) == 0
```

テストを実行して失敗を確認：

```bash
cd <project-root>
uv run pytest tests/test_audio_recorder.py -v
```

コミット：

```
test: test_audio_recorder.py - AudioRecorder モジュールのTDDテスト追加
```

### ステップ2: AudioRecorder モジュールを実装

`speakdrop/audio_recorder.py` を実装してください：

```python
"""音声録音モジュール。

sounddevice を使って16kHz/Mono/16bit PCM形式でマイク録音を行う。
録音データはメモリ上にのみ保持し、stop_recording() 後に破棄する（NFR-006）。
"""
import threading
from typing import Any

import numpy as np
import sounddevice as sd


class AudioRecorder:
    """マイクからの音声録音クラス（NFR-004: 16kHz/Mono/16bit）。"""

    SAMPLE_RATE: int = 16000
    CHANNELS: int = 1
    DTYPE: str = "int16"

    def __init__(self) -> None:
        """AudioRecorder を初期化する。"""
        self._frames: list[np.ndarray] = []
        self._lock = threading.Lock()
        self._stream: sd.InputStream | None = None

    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time: Any,
        status: Any,
    ) -> None:
        """sounddevice コールバック関数。

        録音データをバッファに追加する。
        """
        with self._lock:
            self._frames.append(indata.copy().flatten())

    def start_recording(self) -> None:
        """録音を開始する。

        sounddevice.InputStream を開始し、音声コールバックを登録する。
        """
        with self._lock:
            self._frames = []
        self._stream = sd.InputStream(
            samplerate=self.SAMPLE_RATE,
            channels=self.CHANNELS,
            dtype=self.DTYPE,
            callback=self._audio_callback,
        )
        self._stream.start()

    def stop_recording(self) -> np.ndarray:
        """録音を停止し、録音データを返す。

        Returns:
            録音した音声データ（np.ndarray, dtype=int16）

        Note:
            返却後にバッファをクリアする（NFR-006: 非永続化）。
        """
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        with self._lock:
            if not self._frames:
                return np.array([], dtype=np.int16)
            result = np.concatenate(self._frames)
            self._frames = []  # NFR-006: メモリから破棄

        return result
```

### ステップ3: テストがパスすることを確認

```bash
cd <project-root>
uv run pytest tests/test_audio_recorder.py -v
uv run ruff check speakdrop/audio_recorder.py tests/test_audio_recorder.py
uv run mypy speakdrop/audio_recorder.py
```

### ステップ4: コミット

```
feat: audio_recorder.py - AudioRecorder 実装（16kHz/Mono/int16録音、NFR-004/006）
```

---

## 実装の詳細仕様

### AudioRecorder クラス

```python
class AudioRecorder:
    SAMPLE_RATE: int = 16000   # NFR-004: 16kHz
    CHANNELS: int = 1           # NFR-004: モノラル
    DTYPE: str = "int16"        # NFR-004: 16bit PCM

    def start_recording(self) -> None: ...
    def stop_recording(self) -> np.ndarray: ...
    def _audio_callback(self, indata, frames, time, status) -> None: ...
```

### 入出力仕様

**`AudioRecorder.start_recording() -> None`:**
- 入力: なし
- 出力: なし
- 副作用: sounddevice.InputStream を開始、バッファをクリア

**`AudioRecorder.stop_recording() -> np.ndarray`:**
- 入力: なし
- 出力: 録音した音声データ（dtype=int16の1次元配列）
- 副作用: ストリームを停止、バッファをクリア（NFR-006）

### エラー処理

- sounddevice デバイスなし: 例外をそのまま伝播させる（上位で処理）
- start_recording なしで stop_recording: 空の配列を返す

---

## 注意事項

- `sounddevice` は `import sounddevice as sd` でモジュールレベルでインポートすること（モックのため）
- テストでは `@patch("speakdrop.audio_recorder.sd")` でモックすること
- `_frames` へのアクセスは `threading.Lock` で保護すること（スレッドセーフ）
- `stop_recording()` は必ずバッファをクリアして `None` をセットすること（NFR-006）
- コールバック内の `indata` は `.copy()` してから保存すること（元バッファの上書き防止）

---

## 基本情報（メタデータ）

| 項目 | 値 |
|------|-----|
| **タスクID** | TASK-003 |
| **ステータス** | `TODO` |
| **推定工数** | 30分 |
| **依存関係** | [TASK-001](../phase-1/TASK-001.md) @../phase-1/TASK-001.md |
| **対応要件** | REQ-001, REQ-002, NFR-004, NFR-006 |
| **対応設計** | AudioRecorder セクション（設計書行219-244） |

---

## 情報の明確性チェック

### 明示された情報

- [x] 録音フォーマット: 16kHz/Mono/16bit PCM（NFR-004）
- [x] 使用ライブラリ: sounddevice
- [x] データ形式: np.ndarray（dtype=int16）
- [x] バッファクリア: stop_recording() 後（NFR-006）
- [x] スレッド安全性: threading.Lock が必要（設計書行518）

### 未確認/要確認の情報

| 項目 | 現状の理解 | 確認状況 |
|------|-----------|----------|
| デバイスエラー時の挙動 | 例外をそのまま伝播 | [x] 設計書のエラー処理表に記載（「録音デバイスなし → エラーログ、状態をIDLEに戻す」）。ログ出力は app.py で行う方針 |

---

## 作業ログ（実装時に記入）

### YYYY-MM-DD
- **作業内容**:
- **発生した問題**:
- **解決方法**:
- **コミットハッシュ**:
