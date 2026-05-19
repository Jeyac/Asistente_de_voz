"""Contrato para detección de palabra clave."""

from abc import ABC, abstractmethod

from asistente_voz.domain.entities.wake_word_activation import WakeWordActivation


class IWakeWordDetector(ABC):
    """Puerto de detección de activación por palabra clave."""

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Nombre del motor (openwakeword, porcupine)."""

    @abstractmethod
    async def wait_for_activation(self, timeout: float | None = None) -> WakeWordActivation:
        """Bloquea hasta detectar la palabra clave o agotar el timeout."""

    @abstractmethod
    def release(self) -> None:
        """Libera recursos (micrófono, modelos en memoria)."""
