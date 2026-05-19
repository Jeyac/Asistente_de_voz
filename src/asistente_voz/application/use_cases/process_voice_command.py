"""Caso de uso: procesar comando de voz de extremo a extremo."""

from asistente_voz.application.interfaces.intent_action_executor import IIntentActionExecutor
from asistente_voz.application.interfaces.response_provider import IResponseProvider
from asistente_voz.application.interfaces.speech_service import ISpeechService
from asistente_voz.application.use_cases.classify_intent import ClassifyIntentUseCase
from asistente_voz.core.logging.setup import get_logger
from asistente_voz.domain.entities.voice_command import VoiceCommand
from asistente_voz.domain.entities.voice_process_result import VoiceProcessResult

logger = get_logger(__name__)


class ProcessVoiceCommandUseCase:
    """Orquesta transcripción, clasificación TensorFlow y respuesta dinámica."""

    def __init__(
        self,
        speech_service: ISpeechService,
        classify_intent: ClassifyIntentUseCase,
        response_provider: IResponseProvider,
        action_executor: IIntentActionExecutor,
    ) -> None:
        self._speech_service = speech_service
        self._classify_intent = classify_intent
        self._response_provider = response_provider
        self._action_executor = action_executor

    async def execute_from_text(self, text: str) -> VoiceProcessResult:
        command = await self._speech_service.transcribe_from_text(text)
        return await self._process_command(command)

    async def execute_from_audio(self, audio_bytes: bytes) -> VoiceProcessResult:
        command = await self._speech_service.transcribe_from_audio(audio_bytes)
        return await self._process_command(command)

    async def execute_from_microphone(self) -> VoiceProcessResult:
        command = await self._speech_service.listen_from_microphone()
        return await self._process_command(command)

    async def transcribe_only(self, audio_bytes: bytes) -> VoiceCommand:
        """Solo transcribe audio sin clasificar intención."""
        return await self._speech_service.transcribe_from_audio(audio_bytes)

    async def process_command(self, command: VoiceCommand) -> VoiceProcessResult:
        """Procesa un comando ya transcrito (tras activación por palabra clave)."""
        return await self._process_command(command)

    async def _process_command(self, command: VoiceCommand) -> VoiceProcessResult:
        logger.info("Procesando comando | transcript=%s", command.transcript)
        prediction = await self._classify_intent.execute(command.transcript)
        smart_response = await self._response_provider.generate_from_prediction(prediction)
        message = smart_response.message
        action_performed = False
        action_url: str | None = None

        if smart_response.above_threshold and not smart_response.used_fallback:
            action = await self._action_executor.execute(
                smart_response.intent,
                command.transcript,
            )
            if action and action.url:
                action_url = action.url
                action_performed = action.performed
                message = f"{message} Te lo abro en una nueva pestaña."

        logger.info(
            "Comando procesado | intent=%s | confidence=%.4f | action=%s",
            smart_response.intent,
            smart_response.confidence,
            action_performed,
        )
        return VoiceProcessResult(
            transcript=command.transcript,
            language=command.language,
            intent=smart_response.intent,
            confidence=smart_response.confidence,
            above_threshold=smart_response.above_threshold,
            response=message,
            cleaned_text=prediction.cleaned_text,
            probabilities=prediction.probabilities,
            action_performed=action_performed,
            action_url=action_url,
        )
