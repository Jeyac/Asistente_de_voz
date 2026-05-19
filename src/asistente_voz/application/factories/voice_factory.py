"""Factory del flujo de voz e intenciones."""

from asistente_voz.application.factories.ml_factory import MlFactory
from asistente_voz.application.factories.response_factory import ResponseFactory
from asistente_voz.application.interfaces.speech_service import ISpeechService
from asistente_voz.application.use_cases.classify_intent import ClassifyIntentUseCase
from asistente_voz.application.use_cases.process_voice_command import ProcessVoiceCommandUseCase
from asistente_voz.core.config.settings import Settings
from asistente_voz.infrastructure.speech.audio_validator import AudioValidator


class VoiceFactory:
    """Construye dependencias del pipeline de voz."""

    def __init__(self, settings: Settings, ml_factory: MlFactory) -> None:
        self._settings = settings
        self._ml_factory = ml_factory
        self._response_factory = ResponseFactory(settings)
        self._speech_service: ISpeechService | None = None

    def create_speech_service(self) -> ISpeechService:
        if self._speech_service is None:
            from asistente_voz.infrastructure.speech.speech_service import SpeechRecognitionService

            self._speech_service = SpeechRecognitionService(self._settings)
        return self._speech_service

    def create_audio_validator(self) -> AudioValidator:
        return AudioValidator(self._settings)

    def create_classify_intent_use_case(self) -> ClassifyIntentUseCase:
        return self._ml_factory.create_classify_use_case()

    def create_action_executor(self):
        from asistente_voz.infrastructure.actions.intent_action_executor import (
            IntentActionExecutor,
        )

        return IntentActionExecutor(self._settings)

    def create_process_voice_use_case(self) -> ProcessVoiceCommandUseCase:
        return ProcessVoiceCommandUseCase(
            speech_service=self.create_speech_service(),
            classify_intent=self.create_classify_intent_use_case(),
            response_provider=self._response_factory.create_response_provider(),
            action_executor=self.create_action_executor(),
        )
