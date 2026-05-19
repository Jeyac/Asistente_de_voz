"""Metadatos y etiquetas OpenAPI para documentación Swagger."""

from typing import Any

from asistente_voz.core.config.settings import Settings


def build_openapi_metadata(settings: Settings) -> dict[str, Any]:
    """Construye los metadatos de la documentación automática."""
    return {
        "title": settings.app_name,
        "version": settings.app_version,
        "description": settings.api_description,
        "contact": {
            "name": "Asistente de Voz",
            "url": "https://github.com",
        },
        "license_info": {
            "name": "MIT",
        },
    }


OPENAPI_TAGS: list[dict[str, str]] = [
    {
        "name": "Health",
        "description": "Comprobaciones de estado para monitoreo y Render.",
    },
    {
        "name": "Intents",
        "description": "Clasificación de intenciones con TensorFlow.",
    },
    {
        "name": "Responses",
        "description": "Respuestas inteligentes según intención detectada.",
    },
    {
        "name": "Activation",
        "description": "Activación por palabra clave (oye sistema) estilo Alexa.",
    },
    {
        "name": "Voice",
        "description": "Procesamiento de comandos de voz e intenciones.",
    },
    {
        "name": "Root",
        "description": "Información general del servicio.",
    },
]
