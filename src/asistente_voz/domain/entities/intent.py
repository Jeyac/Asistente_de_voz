"""Entidad de intención detectada (contrato de dominio)."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Intent:
    """Representa una intención clasificada del usuario."""

    name: str
    confidence: float
    raw_text: str
