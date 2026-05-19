"""Validación de archivos de audio subidos por la API."""

from pathlib import Path

from asistente_voz.core.config.settings import Settings
from asistente_voz.domain.exceptions.base import ValidationError
from asistente_voz.domain.exceptions.speech_exceptions import InvalidAudioError

WAV_MAGIC = b"RIFF"


class AudioValidator:
    """Valida tamaño, extensión y cabecera WAV."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._allowed = {
            ext.strip().lower().lstrip(".")
            for ext in settings.speech_allowed_formats.split(",")
            if ext.strip()
        }

    def validate_upload(
        self,
        filename: str | None,
        content_type: str | None,
        content: bytes,
    ) -> None:
        if not content:
            raise InvalidAudioError(message="El archivo de audio está vacío.")

        max_bytes = self._settings.speech_max_audio_bytes
        if len(content) > max_bytes:
            raise ValidationError(
                message=f"El audio supera el tamaño máximo permitido ({max_bytes} bytes).",
                details={"size": len(content), "max_bytes": max_bytes},
            )

        extension = Path(filename or "").suffix.lower().lstrip(".")
        if extension and extension not in self._allowed:
            raise InvalidAudioError(
                message="Formato de audio no permitido.",
                details={"allowed": sorted(self._allowed), "received": extension},
            )

        if extension in {"wav", "wave"} or (content_type or "").endswith("wav"):
            if not content.startswith(WAV_MAGIC):
                raise InvalidAudioError(
                    message="El archivo WAV no tiene una cabecera válida.",
                )
