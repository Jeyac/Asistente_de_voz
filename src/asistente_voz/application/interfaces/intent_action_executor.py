"""Contrato para ejecutar acciones según la intención detectada."""

from abc import ABC, abstractmethod

from asistente_voz.domain.entities.intent_action import IntentActionResult


class IIntentActionExecutor(ABC):
    """Abre URLs/apps o indica al cliente qué abrir."""

    @abstractmethod
    async def execute(self, intent: str, transcript: str) -> IntentActionResult | None:
        """Ejecuta la acción asociada a la intención, si existe."""
