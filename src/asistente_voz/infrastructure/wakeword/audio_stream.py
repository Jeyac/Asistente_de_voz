"""Captura de audio en chunks para detección eficiente."""

import struct
import time
from collections.abc import Iterator

from asistente_voz.core.logging.setup import get_logger

logger = get_logger(__name__)

SAMPLE_RATE = 16_000
CHANNELS = 1
FORMAT_WIDTH = 2  # paInt16


class MicrophoneChunkStream:
    """Stream de micrófono optimizado para inferencia por fragmentos."""

    def __init__(self, chunk_size: int) -> None:
        self._chunk_size = chunk_size
        self._pyaudio = None
        self._stream = None

    def __enter__(self) -> "MicrophoneChunkStream":
        import pyaudio

        self._pyaudio = pyaudio.PyAudio()
        self._stream = self._pyaudio.open(
            format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=self._chunk_size,
        )
        logger.debug("Stream de micrófono abierto | chunk_size=%s", self._chunk_size)
        return self

    def __exit__(self, *_args) -> None:
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
        if self._pyaudio is not None:
            self._pyaudio.terminate()
        logger.debug("Stream de micrófono cerrado")

    def iter_chunks(self, timeout: float | None = None) -> Iterator[bytes]:
        """Genera chunks PCM hasta timeout opcional."""
        deadline = time.perf_counter() + timeout if timeout else None
        while deadline is None or time.perf_counter() < deadline:
            raw = self._stream.read(self._chunk_size, exception_on_overflow=False)
            yield raw

    @staticmethod
    def chunk_to_int16(chunk: bytes):
        """Convierte bytes PCM a numpy int16."""
        import numpy as np

        return np.frombuffer(chunk, dtype=np.int16)
