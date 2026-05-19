"""Registro de manejadores globales de excepciones para FastAPI."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from asistente_voz.core.config.settings import Settings
from asistente_voz.core.logging.setup import get_logger
from asistente_voz.domain.exceptions.base import AppError
from asistente_voz.schemas.common import ErrorResponse

logger = get_logger(__name__)


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def register_exception_handlers(app: FastAPI, settings: Settings) -> None:
    """Registra todos los manejadores de errores en la aplicación."""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            "Error de aplicación | id=%s | code=%s | message=%s",
            _request_id(request),
            exc.code,
            exc.message,
        )
        body = ErrorResponse(error=exc.code, message=exc.message, details=exc.details)
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.warning(
            "Error de validación | id=%s | errors=%s",
            _request_id(request),
            exc.errors(),
        )
        body = ErrorResponse(
            error="validation_error",
            message="Los datos enviados no son válidos.",
            details=exc.errors(),
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=body.model_dump(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        logger.info(
            "Error HTTP | id=%s | status=%s | detail=%s",
            _request_id(request),
            exc.status_code,
            exc.detail,
        )
        body = ErrorResponse(
            error="http_error",
            message=str(exc.detail),
            details=None,
        )
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception(
            "Error no controlado | id=%s | env=%s",
            _request_id(request),
            settings.app_env,
        )
        message = (
            str(exc)
            if settings.debug and not settings.is_production
            else "Ha ocurrido un error interno."
        )
        body = ErrorResponse(
            error="internal_server_error",
            message=message,
            details=None,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=body.model_dump(),
        )
