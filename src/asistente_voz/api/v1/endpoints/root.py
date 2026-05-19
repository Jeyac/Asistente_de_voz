"""Información general del servicio."""

from fastapi import APIRouter

from asistente_voz.api.dependencies import SettingsDep
from asistente_voz.schemas.common import ServiceInfoResponse

router = APIRouter()


@router.get(
    "/",
    response_model=ServiceInfoResponse,
    summary="Información del servicio",
    include_in_schema=True,
)
async def service_info(settings: SettingsDep) -> ServiceInfoResponse:
    """Metadatos básicos y enlaces a la documentación."""
    return ServiceInfoResponse(
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
        api_prefix=settings.api_prefix,
        docs_url="/docs" if settings.docs_enabled else None,
        health_url=f"{settings.api_prefix}/health",
    )
