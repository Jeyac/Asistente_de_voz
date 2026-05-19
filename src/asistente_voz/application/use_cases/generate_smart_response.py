"""Caso de uso: generar respuesta inteligente desde predicción."""
from asistente_voz.application.interfaces.response_provider import IResponseProvider
from asistente_voz.domain.entities.prediction_result import PredictionResult
from asistente_voz.domain.entities.smart_response import SmartResponse

class GenerateSmartResponseUseCase:
    """Selecciona respuesta aleatoria según la intención detectada."""

    def __init__(self, response_provider: IResponseProvider) -> None:
        """Inicializa la instancia."""
        self._response_provider = response_provider

    async def execute(self, prediction: PredictionResult) -> SmartResponse:
        """Ejecuta la operación principal."""
        return await self._response_provider.generate_from_prediction(prediction)

    async def execute_for_intent(self, intent_name: str) -> SmartResponse:
        """Función execute for intent."""
        return await self._response_provider.generate_for_intent(intent_name=intent_name, confidence=1.0, above_threshold=True)
