"""
Detector de palabra clave con openWakeWord (modelo ONNX).

Usado en servidor local (micrófono PyAudio) y en producción (fragmentos
enviados desde el navegador vía WakeWordChunkScorer).
"""
import asyncio
import time
from typing import Any
import numpy as np
from asistente_voz.application.interfaces.wake_word_detector import IWakeWordDetector
from asistente_voz.core.config.settings import Settings
from asistente_voz.core.logging.setup import get_logger
from asistente_voz.domain.entities.wake_word_activation import WakeWordActivation
from asistente_voz.domain.exceptions.wakeword_exceptions import WakeWordEngineError, WakeWordModelNotFoundError, WakeWordTimeoutError
from asistente_voz.infrastructure.wakeword.audio_stream import MicrophoneChunkStream
logger = get_logger(__name__)
CHUNK_SAMPLES = 1280

class OpenWakeWordDetector(IWakeWordDetector):
    """Implementación openWakeWord con modelo personalizado."""

    def __init__(self, settings: Settings) -> None:
        """Inicializa la instancia."""
        self._settings = settings
        self._keyword_id = settings.wakeword_keyword_id
        self._model_key: str = self._keyword_id
        self._model = None

    @property
    def engine_name(self) -> str:
        """Función engine name."""
        return 'openwakeword'

    def _load_model(self):
        """Método interno: load model."""
        if self._model is not None:
            return self._model
        model_path = self._settings.wakeword_model_path.resolve()
        if not model_path.is_file():
            raise WakeWordModelNotFoundError(message=f"Modelo no encontrado en '{model_path}'. Ejecute: python scripts/download_wakeword_model.py (frase configurada: '{self._settings.wakeword_phrase}').", details={'expected_path': str(model_path), 'docs': 'https://github.com/dscripka/openWakeWord'})
        try:
            from openwakeword.model import Model
        except ImportError as exc:
            raise WakeWordEngineError(message='openWakeWord no está instalado.', details={'install': 'pip install openwakeword'}) from exc
        self._model_key = model_path.stem
        self._model = Model(wakeword_models=[str(model_path)], inference_framework='onnx')
        logger.info("Modelo openWakeWord cargado | model_key=%s | phrase='%s' | path=%s", self._model_key, self._settings.wakeword_phrase, model_path)
        return self._model

    def score_int16_chunk(self, pcm_int16: np.ndarray) -> float:
        """Puntúa un fragmento PCM int16 mono 16 kHz (~80 ms, 1280 muestras)."""
        if pcm_int16.size != CHUNK_SAMPLES:
            raise WakeWordEngineError(message=f'Fragmento inválido: se esperaban {CHUNK_SAMPLES} muestras.', details={'received_samples': int(pcm_int16.size)})
        model = self._load_model()
        scores = model.predict(pcm_int16)
        return self._extract_score(scores)

    async def wait_for_activation(self, timeout: float | None=None) -> WakeWordActivation:
        """Función wait for activation."""
        effective_timeout = timeout or self._settings.wakeword_listen_timeout
        return await asyncio.to_thread(self._listen_sync, effective_timeout)

    def _listen_sync(self, timeout: float) -> WakeWordActivation:
        """Método interno: listen sync."""
        model = self._load_model()
        threshold = self._settings.wakeword_threshold
        start = time.perf_counter()
        logger.info("Escuchando palabra clave | phrase='%s' | threshold=%.2f | timeout=%ss", self._settings.wakeword_phrase, threshold, timeout)
        with MicrophoneChunkStream(CHUNK_SAMPLES) as mic:
            for chunk in mic.iter_chunks(timeout=timeout):
                audio = MicrophoneChunkStream.chunk_to_int16(chunk)
                scores = model.predict(audio)
                score = self._extract_score(scores)
                if score >= threshold:
                    latency_ms = (time.perf_counter() - start) * 1000
                    activation = WakeWordActivation.now(keyword=self._settings.wakeword_phrase, engine=self.engine_name, confidence=float(score), latency_ms=latency_ms)
                    logger.info("¡Palabra clave detectada! | phrase='%s' | confidence=%.3f | latency_ms=%.0f", activation.keyword, activation.confidence, activation.latency_ms or 0)
                    return activation
        raise WakeWordTimeoutError(details={'phrase': self._settings.wakeword_phrase, 'timeout_seconds': timeout})

    @staticmethod
    def _score_to_float(value: Any) -> float:
        """Convierte salida de openWakeWord (escalar, ndarray o secuencia) a float."""
        arr = np.asarray(value)
        if arr.ndim == 0:
            return float(arr.item())
        if arr.size == 0:
            return 0.0
        return float(arr.flat[-1])

    def _extract_score(self, scores: dict) -> float:
        """Método interno: extract score."""
        if not scores:
            return 0.0
        for key in (self._model_key, self._keyword_id):
            if key in scores:
                return self._score_to_float(scores[key])
        return max((self._score_to_float(v) for v in scores.values()))

    def release(self) -> None:
        """Función release."""
        self._model = None
        logger.debug('Recursos openWakeWord liberados')
