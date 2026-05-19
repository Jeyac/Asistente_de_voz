"""Pruebas del ejecutor de acciones por intención."""

import asyncio

import pytest

from asistente_voz.core.config.settings import Settings
from asistente_voz.infrastructure.actions.intent_action_executor import IntentActionExecutor


@pytest.fixture
def executor() -> IntentActionExecutor:
    settings = Settings(
        _env_file=None,
        enable_system_actions=True,
        app_env="production",
    )
    return IntentActionExecutor(settings)


def test_resolve_youtube_url(executor: IntentActionExecutor) -> None:
    url = executor._resolve_url("abrir_youtube", "abre youtube")
    assert url == "https://www.youtube.com"


def test_extract_search_query(executor: IntentActionExecutor) -> None:
    query = executor._extract_search_query("busca en internet recetas de pasta")
    assert "recetas" in query


def test_execute_returns_url_for_client_on_render(executor: IntentActionExecutor) -> None:
    result = asyncio.run(executor.execute("abrir_google", "abre google"))
    assert result is not None
    assert result.performed is True
    assert result.url == "https://www.google.com"


def test_creador_has_no_url_action(executor: IntentActionExecutor) -> None:
    result = asyncio.run(executor.execute("creador", "quien te creo"))
    assert result is None


def test_deportes_default_url(executor: IntentActionExecutor) -> None:
    url = executor._resolve_url("deportes", "noticias de deportes")
    assert url is not None
    assert "deportes" in url or "search" in url
