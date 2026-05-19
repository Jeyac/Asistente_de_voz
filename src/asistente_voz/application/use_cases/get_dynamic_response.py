"""Caso de uso: obtener respuesta dinámica según intención."""
from asistente_voz.application.interfaces.response_provider import IResponseProvider
from asistente_voz.domain.entities.prediction_result import PredictionResult
from asistente_voz.domain.entities.smart_response import SmartResponse

class GetDynamicResponseUseCase:
    """Selecciona una respuesta para la intención detectada."""

    def __init__(self, response_provider: IResponseProvider) -> None:
        """Inicializa la instancia."""
        self._response_provider = response_provider

    async def execute(self, intent_name: str) -> str:
        """Ejecuta la operación principal."""
        return await self._response_provider.get_response(intent_name)

    async def execute_from_prediction(self, prediction: PredictionResult) -> SmartResponse:
        """Función execute from prediction."""
        return await self._response_provider.generate_from_prediction(prediction)
