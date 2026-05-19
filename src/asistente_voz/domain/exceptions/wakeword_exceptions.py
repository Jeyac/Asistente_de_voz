"""Excepciones del detector de palabra clave."""

from typing import Any

from asistente_voz.domain.exceptions.base import AppError


class WakeWordModelNotFoundError(AppError):
    """Modelo de palabra clave no encontrado."""

    def __init__(
        self,
        message: str = "Modelo de palabra clave no configurado.",
        details: Any | None = None,
    ) -> None:
        super().__init__(
            message,
            code="wakeword_model_not_found",
            status_code=503,
            details=details,
        )


class WakeWordTimeoutError(AppError):
    """No se detectó la palabra clave en el tiempo límite."""

    def __init__(
        self,
        message: str = "No se detectó la palabra clave a tiempo.",
        details: Any | None = None,
    ) -> None:
        super().__init__(
            message,
            code="wakeword_timeout",
            status_code=408,
            details=details,
        )


class WakeWordEngineError(AppError):
    """Error del motor de detección."""

    def __init__(
        self,
        message: str = "El motor de palabra clave no está disponible.",
        details: Any | None = None,
    ) -> None:
        super().__init__(
            message,
            code="wakeword_engine_error",
            status_code=503,
            details=details,
        )
