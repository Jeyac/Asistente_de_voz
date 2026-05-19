"""Resultado de predicción de intención."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PredictionResult:
    """Resultado de inferencia del clasificador."""

    intent: str
    confidence: float
    raw_text: str
    cleaned_text: str
    above_threshold: bool
    probabilities: dict[str, float]
