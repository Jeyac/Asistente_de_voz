"""Arranque de subsistemas y rutas globales."""

from asistente_voz.core.bootstrap.app_routes import register_app_routes
from asistente_voz.core.bootstrap.ml_bootstrap import bootstrap_intent_model

__all__ = ["bootstrap_intent_model", "register_app_routes"]
