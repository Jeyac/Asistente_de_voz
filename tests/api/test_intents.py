"""Pruebas del endpoint de predicción de intenciones."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.usefixtures("trained_model_registry")
def test_predict_intent_saludo(client: TestClient) -> None:
    response = client.post(
        "/api/v1/intents/predict",
        json={"text": "hola buenos días"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == "saludo"
    assert payload["confidence"] > 0.5
    assert payload["above_threshold"] is True


@pytest.mark.usefixtures("trained_model_registry")
def test_predict_intent_youtube(client: TestClient) -> None:
    response = client.post(
        "/api/v1/intents/predict",
        json={"text": "abre youtube por favor"},
    )
    assert response.status_code == 200
    assert response.json()["intent"] == "abrir_youtube"


@pytest.mark.usefixtures("trained_model_registry")
def test_model_status_loaded(client: TestClient) -> None:
    response = client.get("/api/v1/intents/model/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["loaded"] is True
    assert "saludo" in (payload["labels"] or [])
