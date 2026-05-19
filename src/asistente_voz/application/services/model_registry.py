"""Registro global del modelo de intenciones cargado en runtime."""
from typing import Any

class IntentModelRegistry:
    """Singleton en memoria para artefactos cargados."""

    def __init__(self) -> None:
        """Inicializa la instancia."""
        self._loaded: Any | None = None

    @property
    def is_loaded(self) -> bool:
        """Indica si loaded."""
        return self._loaded is not None

    @property
    def predictor(self) -> Any | None:
        """Función predictor."""
        return self._loaded.predictor if self._loaded else None

    @property
    def metadata(self) -> dict | None:
        """Función metadata."""
        return self._loaded.metadata if self._loaded else None

    def register(self, loaded_model: Any) -> None:
        """Registra el elemento en el sistema."""
        self._loaded = loaded_model

    def clear(self) -> None:
        """Función clear."""
        self._loaded = None
_registry = IntentModelRegistry()

def get_model_registry() -> IntentModelRegistry:
    """Obtiene model registry."""
    return _registry
