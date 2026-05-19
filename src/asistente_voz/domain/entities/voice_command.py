"""Entidad de comando de voz procesado."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VoiceCommand:
    """Comando de voz con texto transcrito."""

    transcript: str
    language: str
