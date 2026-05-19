"""Fixtures de machine learning."""

import pytest

from asistente_voz.application.factories.ml_factory import MlFactory
from asistente_voz.application.services.model_registry import get_model_registry
from asistente_voz.core.config.settings import Settings


@pytest.fixture(scope="session")
def trained_model_registry() -> None:
    """Entrena el modelo una vez por sesión de tests."""
    get_model_registry().clear()
    settings = Settings(_env_file=None, tf_epochs=40)
    factory = MlFactory(settings, get_model_registry())
    if not factory.create_model_loader().is_available:
        factory.create_trainer().train()
        loaded = factory.create_model_loader().load()
        get_model_registry().register(loaded)
    else:
        loaded = factory.create_model_loader().load()
        get_model_registry().register(loaded)
    yield
    get_model_registry().clear()
