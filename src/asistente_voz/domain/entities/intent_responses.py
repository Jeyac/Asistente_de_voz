"""Entidades del catálogo de respuestas por intención."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IntentResponses:
    """Variantes de respuesta asociadas a una intención."""

    intent: str
    variants: tuple[str, ...]
    enabled: bool = True

    @property
    def count(self) -> int:
        return len(self.variants)


@dataclass(frozen=True, slots=True)
class ResponseCatalog:
    """Catálogo completo cargado desde JSON."""

    version: str
    default_intent: str
    intents: tuple[IntentResponses, ...]

    def get(self, intent_name: str) -> IntentResponses | None:
        for item in self.intents:
            if item.intent == intent_name:
                return item
        return None

    def intent_names(self) -> list[str]:
        return [item.intent for item in self.intents if item.enabled]
