"""Factory de la aplicación FastAPI."""

from fastapi import FastAPI

from asistente_voz.api.router import api_router
from asistente_voz.core.bootstrap import register_app_routes
from asistente_voz.core.config.openapi import OPENAPI_TAGS, build_openapi_metadata
from asistente_voz.core.config.settings import Settings
from asistente_voz.core.errors.handlers import register_exception_handlers
from asistente_voz.core.lifespan import create_lifespan
from asistente_voz.core.logging.setup import configure_logging
from asistente_voz.core.middleware.registry import register_middleware


def create_app(settings: Settings) -> FastAPI:
    """Construye y configura la instancia de FastAPI."""
    configure_logging(settings)
    openapi_meta = build_openapi_metadata(settings)

    app = FastAPI(
        **openapi_meta,
        debug=settings.debug,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
        openapi_tags=OPENAPI_TAGS,
        lifespan=create_lifespan(settings),
    )

    register_middleware(app, settings)
    register_exception_handlers(app, settings)
    app.include_router(api_router, prefix=settings.api_prefix)
    register_app_routes(app, settings)

    return app
