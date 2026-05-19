"""Excepciones de dominio."""

from asistente_voz.domain.exceptions.base import AppError, NotFoundError, ValidationError
from asistente_voz.domain.exceptions.ml_exceptions import ModelNotLoadedError
from asistente_voz.domain.exceptions.speech_exceptions import (
    InvalidAudioError,
    MicrophoneNotAvailableError,
    SpeechNotUnderstoodError,
    SpeechRecognitionServiceError,
    SpeechTimeoutError,
)
from asistente_voz.domain.exceptions.wakeword_exceptions import (
    WakeWordEngineError,
    WakeWordModelNotFoundError,
    WakeWordTimeoutError,
)

__all__ = [
    "AppError",
    "NotFoundError",
    "ValidationError",
    "ModelNotLoadedError",
    "SpeechTimeoutError",
    "SpeechNotUnderstoodError",
    "SpeechRecognitionServiceError",
    "MicrophoneNotAvailableError",
    "InvalidAudioError",
    "WakeWordTimeoutError",
    "WakeWordModelNotFoundError",
    "WakeWordEngineError",
]
