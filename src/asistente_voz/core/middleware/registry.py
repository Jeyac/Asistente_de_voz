"""Registro centralizado de middleware."""

from fastapi import FastAPI

from asistente_voz.core.config.settings import Settings
from asistente_voz.core.middleware.cors import setup_cors
from asistente_voz.core.middleware.request_logging import RequestLoggingMiddleware


def register_middleware(app: FastAPI, settings: Settings) -> None:
    """Aplica todos los middleware en el orden correcto (logging como capa externa)."""
    setup_cors(app, settings)
    app.add_middleware(RequestLoggingMiddleware, settings=settings)
