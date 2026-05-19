"""Resultado de una acción ejecutada (o delegada al cliente)."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IntentActionResult:
    """Describe si se abrió una URL/app y dónde."""

    performed: bool
    url: str | None = None
    detail: str | None = None
