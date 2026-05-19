"""Excepciones del subsistema de reconocimiento de voz."""

from typing import Any

from asistente_voz.domain.exceptions.base import AppError


class SpeechTimeoutError(AppError):
    """Tiempo de espera agotado al capturar o procesar audio."""

    def __init__(
        self,
        message: str = "Tiempo de espera agotado al escuchar el micrófono.",
        details: Any | None = None,
    ) -> None:
        super().__init__(
            message,
            code="speech_timeout",
            status_code=408,
            details=details,
        )


class SpeechNotUnderstoodError(AppError):
    """El audio no pudo transcribirse a texto."""

    def __init__(
        self,
        message: str = "No se pudo entender el audio.",
        details: Any | None = None,
    ) -> None:
        super().__init__(
            message,
            code="speech_not_understood",
            status_code=422,
            details=details,
        )


class SpeechRecognitionServiceError(AppError):
    """Fallo del motor de reconocimiento (p. ej. API externa)."""

    def __init__(
        self,
        message: str = "El servicio de reconocimiento de voz no está disponible.",
        details: Any | None = None,
    ) -> None:
        super().__init__(
            message,
            code="speech_service_unavailable",
            status_code=503,
            details=details,
        )


class MicrophoneNotAvailableError(AppError):
    """No hay micrófono accesible en el sistema."""

    def __init__(
        self,
        message: str = "Micrófono no disponible.",
        details: Any | None = None,
    ) -> None:
        super().__init__(
            message,
            code="microphone_unavailable",
            status_code=503,
            details=details,
        )


class InvalidAudioError(AppError):
    """Formato o contenido de audio inválido."""

    def __init__(
        self,
        message: str = "El archivo de audio no es válido.",
        details: Any | None = None,
    ) -> None:
        super().__init__(
            message,
            code="invalid_audio",
            status_code=422,
            details=details,
        )
