"""Fixtures compartidas para pruebas."""

import pytest
from fastapi.testclient import TestClient

from asistente_voz.core.app_factory import create_app
from asistente_voz.core.bootstrap.ml_bootstrap import bootstrap_intent_model
from asistente_voz.core.config.settings import Settings, get_settings


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> None:
    """Evita estado compartido entre tests."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def test_settings() -> Settings:
    """Configuración aislada para tests."""
    return Settings(
        _env_file=None,
        app_env="development",
        debug=True,
        enable_docs=True,
    )


@pytest.fixture
def client(test_settings: Settings) -> TestClient:
    """Cliente HTTP de prueba."""
    app = create_app(test_settings)
    app.dependency_overrides[get_settings] = lambda: test_settings
    bootstrap_intent_model(test_settings)
    return TestClient(app)
