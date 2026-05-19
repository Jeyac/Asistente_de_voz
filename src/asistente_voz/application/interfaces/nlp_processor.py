"""Contrato para procesamiento lingüístico (spaCy)."""

from abc import ABC, abstractmethod


class INlpProcessor(ABC):
    """Puerto de análisis y preprocesamiento de lenguaje natural."""

    @abstractmethod
    async def preprocess(self, text: str) -> str:
        """Preprocesa el texto antes de la clasificación."""
