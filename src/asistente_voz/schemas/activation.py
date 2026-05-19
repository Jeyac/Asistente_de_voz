"""Esquemas REST de activación por palabra clave."""

from datetime import datetime

from pydantic import BaseModel, Field

from asistente_voz.schemas.voice import VoiceProcessResponse


class ActivationConfigResponse(BaseModel):
    """Configuración activa del wake word."""

    enabled: bool
    phrase: str
    engine: str
    threshold: float
    listen_timeout: float


class ActivationListenRequest(BaseModel):
    """Parámetros opcionales de escucha."""

    wakeword_timeout: float | None = Field(
        default=None,
        ge=5.0,
        le=300.0,
        description="Segundos máximos esperando la palabra clave",
    )


class WakeWordActivationSchema(BaseModel):
    """Metadatos de la activación detectada."""

    keyword: str
    engine: str
    confidence: float
    detected_at: datetime
    latency_ms: float | None = None


class ActivationListenResponse(BaseModel):
    """Respuesta del flujo completo con activación."""

    activation: WakeWordActivationSchema
    result: VoiceProcessResponse


class WakeWordChunkScoreResponse(BaseModel):
    """Puntaje de un fragmento de audio enviado desde el navegador."""

    score: float = Field(ge=0.0, description="Puntaje openWakeWord (puede superar 1.0)")
    activated: bool
    phrase: str
    threshold: float
