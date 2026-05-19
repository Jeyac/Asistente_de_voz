"""Orquestador: palabra clave → escucha de comando."""
import asyncio
from asistente_voz.application.interfaces.speech_service import ISpeechService
from asistente_voz.core.config.settings import Settings
from asistente_voz.application.interfaces.wake_word_detector import IWakeWordDetector
from asistente_voz.core.logging.setup import get_logger
from asistente_voz.domain.entities.voice_command import VoiceCommand
from asistente_voz.domain.entities.wake_word_activation import WakeWordActivation
logger = get_logger(__name__)

class ActivationListenerService:
    """
    Gestiona el ciclo de activación:
    1. Espera la palabra clave (bajo consumo, chunks pequeños).
    2. Tras detectarla, abre SpeechRecognition solo para el comando.
  """

    def __init__(self, wake_word_detector: IWakeWordDetector, speech_service: ISpeechService, settings: Settings) -> None:
        """Inicializa la instancia."""
        self._detector = wake_word_detector
        self._speech = speech_service
        self._settings = settings

    async def wait_for_wake_word(self, timeout: float | None=None) -> WakeWordActivation:
        """Fase 1: solo escucha la palabra clave."""
        return await self._detector.wait_for_activation(timeout=timeout)

    async def listen_command(self) -> VoiceCommand:
        """Fase 2: transcribe el comando tras la activación."""
        pause = self._settings.speech_post_wakeword_pause
        if pause > 0:
            logger.info('Pausa post-activación | %.1fs antes de escuchar el comando', pause)
            await asyncio.sleep(pause)
        logger.info('Palabra clave confirmada — escuchando comando del usuario')
        return await self._speech.listen_command_after_activation()

    def release(self) -> None:
        """Libera micrófono y modelos."""
        self._detector.release()
