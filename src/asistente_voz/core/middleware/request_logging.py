"""Middleware de logging estructurado por petición HTTP."""
import time
import uuid
from collections.abc import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from asistente_voz.core.config.settings import Settings
from asistente_voz.core.logging.setup import get_logger
logger = get_logger(__name__)
REQUEST_ID_HEADER = 'X-Request-ID'

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Registra cada petición con duración, estado y correlación."""

    def __init__(self, app, settings: Settings) -> None:
        """Inicializa la instancia."""
        super().__init__(app)
        self._settings = settings

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        """Función dispatch."""
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()
        client_host = request.client.host if request.client else 'unknown'
        logger.info('Petición entrante | id=%s | method=%s | path=%s | client=%s', request_id, request.method, request.url.path, client_host)
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.exception('Petición fallida | id=%s | method=%s | path=%s | duration_ms=%.2f', request_id, request.method, request.url.path, duration_ms)
            raise
        duration_ms = (time.perf_counter() - start) * 1000
        log_fn = logger.warning if duration_ms >= self._settings.log_slow_request_ms else logger.info
        log_fn('Petición completada | id=%s | method=%s | path=%s | status=%s | duration_ms=%.2f', request_id, request.method, request.url.path, response.status_code, duration_ms)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
