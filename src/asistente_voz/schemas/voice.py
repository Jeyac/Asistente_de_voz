"""Esquemas REST del módulo de voz."""

from pydantic import BaseModel, Field


class VoiceTextRequest(BaseModel):
    """Petición con texto ya transcrito."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Texto del comando de voz",
        examples=["abre youtube"],
    )


class VoiceTranscribeResponse(BaseModel):
    """Resultado de la transcripción."""

    transcript: str
    language: str


class VoiceProcessResponse(BaseModel):
    """Resultado del flujo completo voz → intención → respuesta."""

    transcript: str
    language: str
    intent: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    above_threshold: bool
    cleaned_text: str
    response: str
    probabilities: dict[str, float]
    action_performed: bool = False
    action_url: str | None = None
