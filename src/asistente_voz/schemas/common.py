"""Esquemas compartidos de la API."""

from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Respuesta del endpoint de salud."""

    status: str = Field(..., examples=["ok"])
    service: str
    version: str
    environment: str
    timestamp: datetime
    request_id: str


class ServiceInfoResponse(BaseModel):
    """Metadatos del servicio expuestos en la raíz de la API."""

    service: str
    version: str
    environment: str
    api_prefix: str
    docs_url: str | None
    health_url: str


class ErrorResponse(BaseModel):
    """Formato estándar de error."""

    error: str
    message: str
    details: dict | list | None = None
