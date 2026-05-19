"""Jerarquía base de excepciones de aplicación."""
from typing import Any

class AppError(Exception):
    """Excepción base con metadatos para respuestas HTTP."""

    def __init__(self, message: str, *, code: str='app_error', status_code: int=400, details: Any | None=None) -> None:
        """Inicializa la instancia."""
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details

class NotFoundError(AppError):
    """Recurso no encontrado."""

    def __init__(self, message: str='Recurso no encontrado.', details: Any | None=None) -> None:
        """Inicializa la instancia."""
        super().__init__(message, code='not_found', status_code=404, details=details)

class ValidationError(AppError):
    """Error de validación de negocio."""

    def __init__(self, message: str='Datos no válidos.', details: Any | None=None) -> None:
        """Inicializa la instancia."""
        super().__init__(message, code='validation_error', status_code=422, details=details)
