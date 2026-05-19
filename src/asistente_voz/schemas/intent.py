"""Esquemas REST del clasificador de intenciones."""

from pydantic import BaseModel, Field


class IntentPredictRequest(BaseModel):
    """Petición de predicción de intención."""

    text: str = Field(..., min_length=1, max_length=500, description="Texto del usuario")


class IntentPredictResponse(BaseModel):
    """Respuesta con intención predicha y confianza."""

    intent: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    raw_text: str
    cleaned_text: str
    above_threshold: bool
    probabilities: dict[str, float]


class ModelStatusResponse(BaseModel):
    """Estado de carga del modelo."""

    loaded: bool
    labels: list[str] | None = None
    model_path: str | None = None
