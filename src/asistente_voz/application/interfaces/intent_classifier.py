"""Contrato para clasificación de intenciones."""

from abc import ABC, abstractmethod

from asistente_voz.domain.entities.intent import Intent


class IIntentClassifier(ABC):
    """Puerto de clasificación de intenciones (TensorFlow)."""

    @abstractmethod
    async def classify(self, text: str) -> Intent:
        """Clasifica el texto y devuelve la intención más probable."""
