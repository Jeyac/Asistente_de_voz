"""Detector de palabra clave con Porcupine (Picovoice)."""

import asyncio
import struct
import time

from asistente_voz.application.interfaces.wake_word_detector import IWakeWordDetector
from asistente_voz.core.config.settings import Settings
from asistente_voz.core.logging.setup import get_logger
from asistente_voz.domain.entities.wake_word_activation import WakeWordActivation
from asistente_voz.domain.exceptions.wakeword_exceptions import (
    WakeWordEngineError,
    WakeWordModelNotFoundError,
    WakeWordTimeoutError,
)
from asistente_voz.infrastructure.wakeword.audio_stream import (
    CHANNELS,
    FORMAT_WIDTH,
    SAMPLE_RATE,
    MicrophoneChunkStream,
)

logger = get_logger(__name__)


class PorcupineDetector(IWakeWordDetector):
    """Implementación Porcupine para palabras clave personalizadas."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._porcupine = None

    @property
    def engine_name(self) -> str:
        return "porcupine"

    def _initialize(self):
        if self._porcupine is not None:
            return self._porcupine

        access_key = self._settings.porcupine_access_key.strip()
        keyword_path = self._settings.porcupine_keyword_path

        if not access_key:
            raise WakeWordEngineError(
                message="PORCUPINE_ACCESS_KEY no configurada.",
                details={"hint": "Obtenga una clave en https://console.picovoice.ai/"},
            )
        if not keyword_path.is_file():
            raise WakeWordModelNotFoundError(
                message=f"Archivo .ppn no encontrado: {keyword_path}",
                details={
                    "hint": "Cree la palabra clave 'oye sistema' en la consola de Picovoice.",
                },
            )

        try:
            import pvporcupine
        except ImportError as exc:
            raise WakeWordEngineError(
                message="Porcupine no está instalado.",
                details={"install": "pip install pvporcupine"},
            ) from exc

        self._porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=[str(keyword_path)],
        )
        logger.info("Porcupine inicializado | keyword_path=%s", keyword_path)
        return self._porcupine

    async def wait_for_activation(self, timeout: float | None = None) -> WakeWordActivation:
        effective_timeout = timeout or self._settings.wakeword_listen_timeout
        return await asyncio.to_thread(self._listen_sync, effective_timeout)

    def _listen_sync(self, timeout: float) -> WakeWordActivation:
        porcupine = self._initialize()
        frame_length = porcupine.frame_length
        start = time.perf_counter()

        logger.info(
            "Escuchando palabra clave (Porcupine) | phrase='%s' | timeout=%ss",
            self._settings.wakeword_phrase,
            timeout,
        )

        import pyaudio

        pa = pyaudio.PyAudio()
        stream = pa.open(
            rate=porcupine.sample_rate,
            channels=CHANNELS,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=frame_length,
        )

        try:
            deadline = start + timeout
            while time.perf_counter() < deadline:
                pcm = stream.read(frame_length, exception_on_overflow=False)
                samples = struct.unpack_from("h" * frame_length, pcm)
                keyword_index = porcupine.process(samples)
                if keyword_index >= 0:
                    latency_ms = (time.perf_counter() - start) * 1000
                    activation = WakeWordActivation.now(
                        keyword=self._settings.wakeword_phrase,
                        engine=self.engine_name,
                        confidence=1.0,
                        latency_ms=latency_ms,
                    )
                    logger.info(
                        "¡Palabra clave detectada (Porcupine)! | phrase='%s' | latency_ms=%.0f",
                        activation.keyword,
                        activation.latency_ms or 0,
                    )
                    return activation
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()

        raise WakeWordTimeoutError(
            details={"phrase": self._settings.wakeword_phrase, "timeout_seconds": timeout},
        )

    def release(self) -> None:
        if self._porcupine is not None:
            self._porcupine.delete()
            self._porcupine = None
        logger.debug("Recursos Porcupine liberados")
