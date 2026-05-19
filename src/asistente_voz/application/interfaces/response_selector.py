"""Contrato para estrategias de selección de respuesta."""

from abc import ABC, abstractmethod
from typing import Sequence


class IResponseSelector(ABC):
    """Selecciona una variante entre las disponibles."""

    @abstractmethod
    def select(self, variants: Sequence[str]) -> str:
        """Devuelve una respuesta del conjunto de variantes."""
