"""Ciclo de vida de la aplicación FastAPI."""
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from asistente_voz.core.bootstrap.ml_bootstrap import bootstrap_intent_model
from asistente_voz.core.config.settings import Settings
from asistente_voz.core.logging.setup import get_logger
logger = get_logger(__name__)

def create_lifespan(settings: Settings):
    """Factory del contexto de vida con configuración inyectada."""

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        """Función lifespan."""
        logger.info('Iniciando servicio | env=%s | version=%s | docs=%s', settings.app_env, settings.app_version, settings.docs_enabled)
        bootstrap_intent_model(settings)
        yield
        logger.info('Servicio detenido correctamente')
    return lifespan
