"""Esquemas REST del sistema de respuestas."""

from pydantic import BaseModel, Field


class SmartResponseSchema(BaseModel):
    """Respuesta inteligente seleccionada."""

    intent: str
    message: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    above_threshold: bool
    variants_available: int
    used_fallback: bool


class GenerateResponseRequest(BaseModel):
    """Texto de entrada para clasificar y responder."""

    text: str = Field(..., min_length=1, max_length=500, examples=["hola"])


class GenerateResponseResult(BaseModel):
    """Clasificación TensorFlow + respuesta del catálogo."""

    transcript: str
    intent: str
    confidence: float
    above_threshold: bool
    cleaned_text: str
    probabilities: dict[str, float]
    response: SmartResponseSchema


class IntentCatalogItem(BaseModel):
    """Metadatos de una intención en el catálogo."""

    intent: str
    variants_count: int
    enabled: bool


class ResponseCatalogSchema(BaseModel):
    """Catálogo completo de respuestas."""

    version: str
    default_intent: str
    intents: list[IntentCatalogItem]
