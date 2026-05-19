"""Evento de activación por palabra clave."""
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True, slots=True)
class WakeWordActivation:
    """Registro de una activación detectada."""
    keyword: str
    engine: str
    confidence: float
    detected_at: datetime
    latency_ms: float | None = None

    @staticmethod
    def now(keyword: str, engine: str, confidence: float, latency_ms: float | None=None) -> 'WakeWordActivation':
        """Función now."""
        return WakeWordActivation(keyword=keyword, engine=engine, confidence=confidence, detected_at=datetime.now(timezone.utc), latency_ms=latency_ms)
