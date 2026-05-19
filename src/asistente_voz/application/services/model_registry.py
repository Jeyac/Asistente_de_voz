"""Registro global del modelo de intenciones cargado en runtime."""

from typing import Any


class IntentModelRegistry:
    """Singleton en memoria para artefactos cargados."""

    def __init__(self) -> None:
        self._loaded: Any | None = None

    @property
    def is_loaded(self) -> bool:
        return self._loaded is not None

    @property
    def predictor(self) -> Any | None:
        return self._loaded.predictor if self._loaded else None

    @property
    def metadata(self) -> dict | None:
        return self._loaded.metadata if self._loaded else None

    def register(self, loaded_model: Any) -> None:
        self._loaded = loaded_model

    def clear(self) -> None:
        self._loaded = None


_registry = IntentModelRegistry()


def get_model_registry() -> IntentModelRegistry:
    return _registry
