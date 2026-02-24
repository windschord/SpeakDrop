"""AudioRecorder モジュールのテスト。"""
from unittest.mock import MagicMock, patch

import numpy as np

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
