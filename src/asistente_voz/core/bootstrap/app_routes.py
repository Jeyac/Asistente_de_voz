"""Registro de rutas a nivel de aplicación (fuera del prefijo API)."""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from asistente_voz.core.config.settings import Settings


def register_app_routes(app: FastAPI, settings: Settings) -> None:
    """Rutas globales para descubrimiento y redirección."""

    @app.get("/", include_in_schema=False)
    async def root_redirect() -> RedirectResponse:
        """Redirige a la documentación o al healthcheck según configuración."""
        target = "/docs" if settings.docs_enabled else f"{settings.api_prefix}/health"
        return RedirectResponse(url=target, status_code=307)
