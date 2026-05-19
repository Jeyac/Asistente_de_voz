"""Pruebas del validador de audio."""

import pytest

from asistente_voz.core.config.settings import Settings
from asistente_voz.domain.exceptions.base import ValidationError
from asistente_voz.domain.exceptions.speech_exceptions import InvalidAudioError
from asistente_voz.infrastructure.speech.audio_validator import AudioValidator


@pytest.fixture
def validator() -> AudioValidator:
    settings = Settings(_env_file=None)
    return AudioValidator(settings)


def test_rejects_empty_audio(validator: AudioValidator) -> None:
    with pytest.raises(InvalidAudioError):
        validator.validate_upload("test.wav", "audio/wav", b"")


def test_rejects_invalid_wav_header(validator: AudioValidator) -> None:
    with pytest.raises(InvalidAudioError):
        validator.validate_upload("test.wav", "audio/wav", b"not-a-wav-file" * 10)


def test_accepts_valid_wav_header(validator: AudioValidator) -> None:
    content = b"RIFF" + b"\x00" * 100
    validator.validate_upload("sample.wav", "audio/wav", content)


def test_rejects_oversized_file(validator: AudioValidator) -> None:
    settings = Settings(_env_file=None).model_copy(update={"speech_max_audio_bytes": 100})
    small_validator = AudioValidator(settings)
    with pytest.raises(ValidationError):
        small_validator.validate_upload("big.wav", "audio/wav", b"RIFF" + b"\x00" * 200)
