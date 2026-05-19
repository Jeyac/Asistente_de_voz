"""Caso de uso: activación por palabra clave y procesamiento completo."""

from dataclasses import dataclass

from asistente_voz.application.services.activation_listener import ActivationListenerService
from asistente_voz.application.use_cases.process_voice_command import ProcessVoiceCommandUseCase
from asistente_voz.core.logging.setup import get_logger
from asistente_voz.domain.entities.voice_process_result import VoiceProcessResult
from asistente_voz.domain.entities.wake_word_activation import WakeWordActivation

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class ActivationListenResult:
    """Resultado del flujo activación + comando + respuesta."""

    activation: WakeWordActivation
    voice_result: VoiceProcessResult


class ActivateAndListenUseCase:
    """Espera 'oye sistema', luego transcribe, clasifica y responde."""

    def __init__(
        self,
        activation_listener: ActivationListenerService,
        process_voice: ProcessVoiceCommandUseCase,
    ) -> None:
        self._listener = activation_listener
        self._process_voice = process_voice

    async def execute(self, wakeword_timeout: float | None = None) -> ActivationListenResult:
        activation: WakeWordActivation | None = None
        try:
            activation = await self._listener.wait_for_wake_word(timeout=wakeword_timeout)
            command = await self._listener.listen_command()
            voice_result = await self._process_voice.process_command(command)
            logger.info(
                "Flujo por activación completado | intent=%s",
                voice_result.intent,
            )
            return ActivationListenResult(activation=activation, voice_result=voice_result)
        finally:
            self._listener.release()
