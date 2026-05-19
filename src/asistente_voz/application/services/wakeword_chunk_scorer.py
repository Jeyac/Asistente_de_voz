"""
Puntúa fragmentos de audio del navegador con openWakeWord.

Mantiene un detector por cabecera X-Wake-Session para conservar el estado
temporal del modelo entre peticiones HTTP (necesario en Render).
"""
from __future__ import annotations
import threading
import time
from dataclasses import dataclass
import numpy as np
from asistente_voz.core.config.settings import Settings
from asistente_voz.core.logging.setup import get_logger
from asistente_voz.domain.exceptions.base import ValidationError
from asistente_voz.infrastructure.wakeword.openwakeword_detector import CHUNK_SAMPLES, OpenWakeWordDetector
logger = get_logger(__name__)
SESSION_TTL_SECONDS = 600.0
EXPECTED_CHUNK_BYTES = CHUNK_SAMPLES * 2

@dataclass(frozen=True)
class WakeWordChunkScore:
    """Clase WakeWordChunkScore."""
    score: float
    activated: bool
    phrase: str
    threshold: float

@dataclass
class _SessionEntry:
    """Clase  SessionEntry."""
    detector: OpenWakeWordDetector
    last_access: float

class WakeWordChunkScorer:
    """Mantiene un detector openWakeWord por sesión de cliente (micrófono en el navegador)."""

    def __init__(self, settings: Settings) -> None:
        """Inicializa la instancia."""
        self._settings = settings
        self._sessions: dict[str, _SessionEntry] = {}
        self._lock = threading.Lock()

    def score_chunk(self, session_id: str, pcm_bytes: bytes) -> WakeWordChunkScore:
        """Función score chunk."""
        if not self._settings.wakeword_enabled:
            raise ValidationError(message='La palabra clave está desactivada en el servidor.', details={'hint': 'Configure WAKEWORD_ENABLED=true'})
        if self._settings.wakeword_engine != 'openwakeword':
            raise ValidationError(message='El puntaje por fragmentos solo está disponible con openWakeWord.', details={'engine': self._settings.wakeword_engine})
        if len(pcm_bytes) != EXPECTED_CHUNK_BYTES:
            raise ValidationError(message='Tamaño de fragmento de audio inválido.', details={'expected_bytes': EXPECTED_CHUNK_BYTES, 'received_bytes': len(pcm_bytes)})
        session_id = session_id.strip()
        if not session_id or len(session_id) > 128:
            raise ValidationError(message='Cabecera X-Wake-Session inválida.')
        pcm = np.frombuffer(pcm_bytes, dtype=np.int16).copy()
        detector = self._get_detector(session_id)
        try:
            score = detector.score_int16_chunk(pcm)
        except Exception as exc:
            logger.warning('Error al puntuar fragmento wake word | session=%s | %s', session_id[:8], exc)
            raise
        threshold = self._settings.wakeword_threshold
        activated = score >= threshold
        if activated:
            logger.info("Palabra clave detectada (chunk) | phrase='%s' | score=%.3f", self._settings.wakeword_phrase, score)
        return WakeWordChunkScore(score=float(score), activated=activated, phrase=self._settings.wakeword_phrase, threshold=threshold)

    def score_chunks(self, session_id: str, pcm_bytes: bytes) -> WakeWordChunkScore:
        """Puntúa varios fragmentos consecutivos en una sola petición (menos latencia en Render)."""
        if not self._settings.wakeword_enabled:
            raise ValidationError(message='La palabra clave está desactivada en el servidor.', details={'hint': 'Configure WAKEWORD_ENABLED=true'})
        if self._settings.wakeword_engine != 'openwakeword':
            raise ValidationError(message='El puntaje por fragmentos solo está disponible con openWakeWord.', details={'engine': self._settings.wakeword_engine})
        if not pcm_bytes:
            raise ValidationError(message='Cuerpo de audio vacío.', details={'expected_multiple_of': EXPECTED_CHUNK_BYTES})
        if len(pcm_bytes) % EXPECTED_CHUNK_BYTES != 0:
            raise ValidationError(message='Tamaño de audio inválido (debe ser múltiplo del fragmento).', details={'chunk_bytes': EXPECTED_CHUNK_BYTES, 'received_bytes': len(pcm_bytes)})
        session_id = session_id.strip()
        if not session_id or len(session_id) > 128:
            raise ValidationError(message='Cabecera X-Wake-Session inválida.')
        detector = self._get_detector(session_id)
        threshold = self._settings.wakeword_threshold
        max_score = 0.0
        activated = False
        for offset in range(0, len(pcm_bytes), EXPECTED_CHUNK_BYTES):
            chunk_bytes = pcm_bytes[offset:offset + EXPECTED_CHUNK_BYTES]
            pcm = np.frombuffer(chunk_bytes, dtype=np.int16).copy()
            score = detector.score_int16_chunk(pcm)
            max_score = max(max_score, float(score))
            if score >= threshold:
                activated = True
                logger.info("Palabra clave detectada (lote) | phrase='%s' | score=%.3f", self._settings.wakeword_phrase, score)
                break
        return WakeWordChunkScore(score=max_score, activated=activated, phrase=self._settings.wakeword_phrase, threshold=threshold)

    def end_session(self, session_id: str) -> None:
        """Función end session."""
        with self._lock:
            entry = self._sessions.pop(session_id.strip(), None)
        if entry:
            entry.detector.release()

    def _get_detector(self, session_id: str) -> OpenWakeWordDetector:
        """Método interno: get detector."""
        now = time.monotonic()
        with self._lock:
            self._purge_expired(now)
            entry = self._sessions.get(session_id)
            if entry is None:
                entry = _SessionEntry(detector=OpenWakeWordDetector(self._settings), last_access=now)
                self._sessions[session_id] = entry
            else:
                entry.last_access = now
            return entry.detector

    def _purge_expired(self, now: float) -> None:
        """Método interno: purge expired."""
        expired = [sid for sid, entry in self._sessions.items() if now - entry.last_access > SESSION_TTL_SECONDS]
        for sid in expired:
            entry = self._sessions.pop(sid)
            entry.detector.release()
            logger.debug('Sesión wake word expirada | session=%s', sid[:8])
