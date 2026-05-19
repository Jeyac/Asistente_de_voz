"""Definición de intención con ejemplos de entrenamiento."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IntentDefinition:
    """Intención del dataset con frases de ejemplo."""

    name: str
    examples: tuple[str, ...]
