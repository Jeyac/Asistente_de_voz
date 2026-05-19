"""Factory del motor de palabra clave."""

from asistente_voz.application.interfaces.wake_word_detector import IWakeWordDetector
from asistente_voz.core.config.settings import Settings
from asistente_voz.domain.exceptions.wakeword_exceptions import WakeWordEngineError


class WakeWordDetectorFactory:
    """Selecciona el motor configurado."""

    @staticmethod
    def create(settings: Settings) -> IWakeWordDetector:
        if not settings.wakeword_enabled:
            raise WakeWordEngineError(message="La activación por palabra clave está deshabilitada.")

        engine = settings.wakeword_engine
        if engine == "openwakeword":
            from asistente_voz.infrastructure.wakeword.openwakeword_detector import (
                OpenWakeWordDetector,
            )

            return OpenWakeWordDetector(settings)
        if engine == "porcupine":
            from asistente_voz.infrastructure.wakeword.porcupine_detector import (
                PorcupineDetector,
            )

            return PorcupineDetector(settings)

        raise WakeWordEngineError(
            message=f"Motor de palabra clave no soportado: {engine}",
            details={"supported": ["openwakeword", "porcupine"]},
        )
