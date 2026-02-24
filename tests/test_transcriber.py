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
