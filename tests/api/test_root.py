"""Pruebas de información del servicio."""

from fastapi.testclient import TestClient


def test_service_info(client: TestClient) -> None:
    """El endpoint raíz de la API devuelve metadatos."""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"]
    assert payload["health_url"] == "/api/v1/health"
    assert payload["docs_url"] == "/docs"
