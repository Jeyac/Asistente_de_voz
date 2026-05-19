"""Repositorio legacy — delega en ResponseLoader."""
from asistente_voz.infrastructure.responses.response_loader import ResponseLoader

class ResponsesRepository:
    """Compatibilidad: acceso al catálogo vía loader."""

    def __init__(self, loader: ResponseLoader) -> None:
        """Inicializa la instancia."""
        self._loader = loader

    def get_response(self, intent_name: str) -> str:
        """Obtiene response."""
        from asistente_voz.infrastructure.responses.response_selector import RandomResponseSelector
        catalog = self._loader.load()
        intent = catalog.get(intent_name) or catalog.get(catalog.default_intent)
        if not intent or not intent.variants:
            from asistente_voz.domain.exceptions.base import ValidationError
            raise ValidationError(message=f"Sin respuestas para '{intent_name}'.")
        return RandomResponseSelector().select(intent.variants)
