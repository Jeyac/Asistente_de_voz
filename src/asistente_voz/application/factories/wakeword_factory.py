"""Factory del subsistema de palabra clave."""
from asistente_voz.application.factories.voice_factory import VoiceFactory
from asistente_voz.application.services.activation_listener import ActivationListenerService
from asistente_voz.application.use_cases.activate_and_listen import ActivateAndListenUseCase
from asistente_voz.core.config.settings import Settings
from asistente_voz.infrastructure.wakeword.detector_factory import WakeWordDetectorFactory

class WakeWordFactory:
    """Construye dependencias de activación por palabra clave."""

    def __init__(self, settings: Settings, voice_factory: VoiceFactory) -> None:
        """Inicializa la instancia."""
        self._settings = settings
        self._voice_factory = voice_factory

    def create_activation_listener(self) -> ActivationListenerService:
        """Función create activation listener."""
        detector = WakeWordDetectorFactory.create(self._settings)
        speech = self._voice_factory.create_speech_service()
        return ActivationListenerService(detector, speech, self._settings)

    def create_activate_and_listen_use_case(self) -> ActivateAndListenUseCase:
        """Función create activate and listen use case."""
        return ActivateAndListenUseCase(activation_listener=self.create_activation_listener(), process_voice=self._voice_factory.create_process_voice_use_case())
