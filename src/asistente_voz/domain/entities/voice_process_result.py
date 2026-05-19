"""Resultado del procesamiento completo de un comando de voz."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VoiceProcessResult:
    """Transcripción, intención clasificada y respuesta dinámica."""

    transcript: str
    language: str
    intent: str
    confidence: float
    above_threshold: bool
    response: str
    cleaned_text: str
    probabilities: dict[str, float]
    action_performed: bool = False
    action_url: str | None = None
