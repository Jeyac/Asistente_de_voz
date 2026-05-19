"""Endpoint de salud para monitoreo y Render."""

from datetime import datetime, timezone

from fastapi import APIRouter, status

from asistente_voz.api.dependencies import RequestIdDep, SettingsDep
from asistente_voz.schemas.common import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Healthcheck del servicio",
    description="Comprueba que la API está operativa. Usado por Render y balanceadores.",
    responses={
        200: {"description": "Servicio operativo"},
        503: {"description": "Servicio no disponible"},
    },
)
async def health_check(
    settings: SettingsDep,
    request_id: RequestIdDep,
) -> HealthResponse:
    """Devuelve el estado actual del servicio."""
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
        timestamp=datetime.now(timezone.utc),
        request_id=request_id,
    )
