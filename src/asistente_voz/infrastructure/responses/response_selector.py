"""Estrategia de selección aleatoria de respuestas."""
import random
from typing import Sequence
from asistente_voz.application.interfaces.response_selector import IResponseSelector
from asistente_voz.domain.exceptions.base import ValidationError

class RandomResponseSelector(IResponseSelector):
    """Selecciona una variante al azar."""

    def select(self, variants: Sequence[str]) -> str:
        """Función select."""
        if not variants:
            raise ValidationError(message='No hay variantes de respuesta disponibles.')
        return random.choice(list(variants))
