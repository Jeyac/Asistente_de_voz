"""Excepciones del subsistema de machine learning."""
from typing import Any
from asistente_voz.domain.exceptions.base import AppError

class ModelNotLoadedError(AppError):
    """El modelo o artefactos no están disponibles."""

    def __init__(self, message: str='El modelo de intenciones no está cargado. Ejecute el entrenamiento.', details: Any | None=None) -> None:
        """Inicializa la instancia."""
        super().__init__(message, code='model_not_loaded', status_code=503, details=details)
