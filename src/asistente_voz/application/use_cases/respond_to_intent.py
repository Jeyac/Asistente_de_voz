"""Caso de uso: clasificar texto y responder automáticamente."""

from dataclasses import dataclass

from asistente_voz.application.interfaces.response_provider import IResponseProvider
from asistente_voz.application.use_cases.classify_intent import ClassifyIntentUseCase
from asistente_voz.core.logging.setup import get_logger
from asistente_voz.domain.entities.smart_response import SmartResponse

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class IntentReply:
    """Resultado integrado clasificación + respuesta."""

    transcript: str
    prediction_intent: str
    confidence: float
    above_threshold: bool
    cleaned_text: str
    probabilities: dict[str, float]
    response: SmartResponse


class RespondToIntentUseCase:
    """Orquesta TensorFlow y el catálogo de respuestas JSON."""

    def __init__(
        self,
        classify_intent: ClassifyIntentUseCase,
        response_provider: IResponseProvider,
    ) -> None:
        self._classify_intent = classify_intent
        self._response_provider = response_provider

    async def execute(self, text: str) -> IntentReply:
        prediction = await self._classify_intent.execute(text)
        smart_response = await self._response_provider.generate_from_prediction(prediction)
        logger.info(
            "Respuesta inteligente | intent=%s | message=%s",
            smart_response.intent,
            smart_response.message[:50],
        )
        return IntentReply(
            transcript=text,
            prediction_intent=prediction.intent,
            confidence=prediction.confidence,
            above_threshold=prediction.above_threshold,
            cleaned_text=prediction.cleaned_text,
            probabilities=prediction.probabilities,
            response=smart_response,
        )
