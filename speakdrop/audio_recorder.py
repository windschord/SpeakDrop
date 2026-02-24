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
