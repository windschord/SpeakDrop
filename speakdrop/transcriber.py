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
