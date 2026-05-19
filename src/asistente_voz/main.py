"""
Punto de entrada de la aplicación FastAPI.

Uso local: python -m asistente_voz.main  o  uvicorn asistente_voz.main:app
Requiere PYTHONPATH=src (o instalar el paquete en editable).
"""

from asistente_voz.core.app_factory import create_app
from asistente_voz.core.config.settings import get_settings

settings = get_settings()
app = create_app(settings)


def run() -> None:
    """Arranque local con uvicorn (desarrollo)."""
    import uvicorn

    uvicorn.run(
        "asistente_voz.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug and not settings.is_production,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    run()
