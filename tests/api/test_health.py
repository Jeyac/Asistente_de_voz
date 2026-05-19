"""Pruebas del endpoint de salud."""

from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    """El servicio responde con estado operativo."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"]
    assert payload["version"]
    assert payload["environment"] == "development"
    assert "timestamp" in payload
    assert payload["request_id"]
    assert response.headers.get("x-request-id") == payload["request_id"]


def test_health_includes_request_id_header(client: TestClient) -> None:
    """Cada respuesta incluye cabecera de correlación."""
    response = client.get("/api/v1/health")
    assert response.headers.get("X-Request-ID")


def test_openapi_docs_available_in_development(client: TestClient) -> None:
    """Swagger está disponible cuando la documentación está habilitada."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"]
    assert "/api/v1/health" in schema["paths"]
