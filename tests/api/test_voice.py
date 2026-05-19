"""Pruebas del flujo de voz integrado con el clasificador."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from asistente_voz.api.dependencies import get_process_voice_use_case
from asistente_voz.domain.entities.voice_command import VoiceCommand
from asistente_voz.domain.entities.voice_process_result import VoiceProcessResult


@pytest.fixture
def mock_process_use_case():
    use_case = MagicMock()
    use_case.execute_from_text = AsyncMock(
        return_value=VoiceProcessResult(
            transcript="hola",
            language="es-ES",
            intent="saludo",
            confidence=0.91,
            above_threshold=True,
            response="Hola, ¿en qué puedo ayudarte?",
            cleaned_text="hola",
            probabilities={"saludo": 0.91},
        ),
    )
    use_case.transcribe_only = AsyncMock(
        return_value=VoiceCommand(transcript="abre youtube", language="es-ES"),
    )
    return use_case


def test_process_voice_text(client: TestClient, mock_process_use_case) -> None:
    app = client.app
    app.dependency_overrides[get_process_voice_use_case] = lambda: mock_process_use_case
    response = client.post("/api/v1/voice/process", json={"text": "hola"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == "saludo"
    assert payload["response"]
    assert payload["transcript"] == "hola"
    app.dependency_overrides.clear()


def test_transcribe_audio_validates_wav(client: TestClient, mock_process_use_case) -> None:
    app = client.app
    app.dependency_overrides[get_process_voice_use_case] = lambda: mock_process_use_case
    response = client.post(
        "/api/v1/voice/transcribe",
        files={"audio": ("bad.wav", b"invalid", "audio/wav")},
    )
    assert response.status_code == 422
    app.dependency_overrides.clear()
