"""Configuración de CORS."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from asistente_voz.core.config.settings import Settings


def setup_cors(app: FastAPI, settings: Settings) -> None:
    """Registra el middleware CORS según la configuración."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )
