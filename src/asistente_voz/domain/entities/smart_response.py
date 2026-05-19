"""Resultado de una respuesta inteligente generada."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SmartResponse:
    """Respuesta seleccionada tras clasificar la intención."""

    intent: str
    message: str
    confidence: float
    above_threshold: bool
    variants_available: int
    used_fallback: bool
