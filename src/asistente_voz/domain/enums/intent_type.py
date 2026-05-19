"""Tipos de intención soportados (extensible vía dataset JSON)."""

from enum import StrEnum


class IntentType(StrEnum):
    """Intenciones base; el dataset JSON puede ampliar el conjunto."""

    SALUDO = "saludo"
    DESPEDIDA = "despedida"
    AYUDA = "ayuda"
    DEFAULT = "default"
