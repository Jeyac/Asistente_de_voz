"""Pruebas del servicio de respuestas inteligentes."""

import asyncio
from pathlib import Path

import pytest

from asistente_voz.core.config.settings import Settings
from asistente_voz.domain.entities.prediction_result import PredictionResult
from asistente_voz.infrastructure.persistence.json.base_repository import JsonFileRepository
from asistente_voz.infrastructure.responses.response_loader import ResponseLoader
from asistente_voz.infrastructure.responses.response_selector import RandomResponseSelector
from asistente_voz.infrastructure.responses.response_service import SmartResponseService


@pytest.fixture
def service() -> SmartResponseService:
    path = Path(__file__).resolve().parents[2] / "data" / "responses" / "responses.json"
    settings = Settings(_env_file=None)
    return SmartResponseService(
        loader=ResponseLoader(JsonFileRepository(path)),
        selector=RandomResponseSelector(),
        settings=settings,
    )


def test_random_response_for_saludo(service: SmartResponseService) -> None:
    smart = asyncio.run(service.generate_for_intent("saludo"))
    assert smart.intent == "saludo"
    assert smart.message
    assert smart.variants_available >= 3


def test_relacion_creador_mentions_kevin(service: SmartResponseService) -> None:
    smart = asyncio.run(service.generate_for_intent("relacion_creador"))
    assert smart.intent == "relacion_creador"
    assert "Kevin Estrada" in smart.message
    assert "novio" in smart.message.lower() or "increíble" in smart.message


def test_creador_mentions_jeraldyn(service: SmartResponseService) -> None:
    smart = asyncio.run(service.generate_for_intent("creador"))
    assert smart.intent == "creador"
    assert "Jéraldyn" in smart.message
    assert "maravillosa" in smart.message


def test_hora_returns_current_time(service: SmartResponseService) -> None:
    smart = asyncio.run(service.generate_for_intent("hora"))
    assert smart.intent == "hora"
    assert smart.message.startswith("Son las ")
    assert ":" in smart.message


def test_fallback_when_low_confidence(service: SmartResponseService) -> None:
    prediction = PredictionResult(
        intent="saludo",
        confidence=0.2,
        raw_text="xyz",
        cleaned_text="xyz",
        above_threshold=False,
        probabilities={"saludo": 0.2},
    )
    smart = asyncio.run(service.generate_from_prediction(prediction))
    assert smart.used_fallback is True
    assert smart.intent == "desconocido"
