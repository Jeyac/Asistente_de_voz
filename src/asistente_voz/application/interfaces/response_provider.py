"""Contrato para respuestas dinámicas."""

from abc import ABC, abstractmethod

from asistente_voz.domain.entities.prediction_result import PredictionResult
from asistente_voz.domain.entities.intent_responses import ResponseCatalog
from asistente_voz.domain.entities.smart_response import SmartResponse


class IResponseProvider(ABC):
    """Puerto de obtención de respuestas según intención."""

    @abstractmethod
    async def get_response(self, intent_name: str) -> str:
        """Devuelve una respuesta dinámica para la intención dada."""

    @abstractmethod
    async def generate_from_prediction(self, prediction: PredictionResult) -> SmartResponse:
        """Genera respuesta inteligente a partir de la predicción TensorFlow."""

    @abstractmethod
    async def get_catalog(self) -> ResponseCatalog:
        """Obtiene el catálogo completo de respuestas."""

    @abstractmethod
    async def generate_for_intent(
        self,
        intent_name: str,
        *,
        confidence: float = 1.0,
        above_threshold: bool = True,
        used_fallback: bool = False,
    ) -> SmartResponse:
        """Genera respuesta para una intención conocida."""
