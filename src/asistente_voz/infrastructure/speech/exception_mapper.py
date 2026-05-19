"""Mapeo de excepciones de SpeechRecognition a excepciones de dominio."""

from typing import Any

import speech_recognition as sr

from asistente_voz.domain.exceptions.speech_exceptions import (
    MicrophoneNotAvailableError,
    SpeechNotUnderstoodError,
    SpeechRecognitionServiceError,
    SpeechTimeoutError,
)


class SpeechExceptionMapper:
    """Traduce errores de la librería sin acoplar el dominio a SpeechRecognition."""

    @staticmethod
    def map_exception(exc: Exception) -> Exception:
        if isinstance(exc, sr.WaitTimeoutError):
            return SpeechTimeoutError(details={"cause": str(exc)})
        if isinstance(exc, sr.UnknownValueError):
            return SpeechNotUnderstoodError(
                message=(
                    "No se pudo entender el audio. Hable en español, claro y cerca del micrófono."
                ),
                details={
                    "cause": str(exc) or "unknown_value",
                    "hints": [
                        "Espere 1 s tras decir 'Hey Jarvis' antes del comando.",
                        "Use frases cortas: 'abre youtube', 'qué hora es'.",
                        "Compruebe conexión a Internet (Google Speech API).",
                    ],
                },
            )
        if isinstance(exc, sr.RequestError):
            return SpeechRecognitionServiceError(
                message="Error al conectar con el motor de reconocimiento.",
                details={"cause": str(exc)},
            )
        if isinstance(exc, OSError):
            return MicrophoneNotAvailableError(details={"cause": str(exc)})
        return exc

    @staticmethod
    def wrap(callable_fn, *args: Any, **kwargs: Any) -> Any:
        try:
            return callable_fn(*args, **kwargs)
        except Exception as exc:
            raise SpeechExceptionMapper.map_exception(exc) from exc
