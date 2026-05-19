"""Configuración del sistema de logging."""
from pathlib import Path
from typing import Literal
from pydantic import Field, field_validator
from asistente_voz.core.config.base import resolve_project_path

class LoggingConfig:
    """Parámetros de logs y middleware de peticiones."""
    log_level: str = Field(default='INFO', alias='LOG_LEVEL')
    log_format: Literal['json', 'text'] = Field(default='json', alias='LOG_FORMAT')
    log_file_path: Path = Field(default=Path('logs/app.log'), alias='LOG_FILE_PATH')
    log_slow_request_ms: int = Field(default=1000, alias='LOG_SLOW_REQUEST_MS')
    log_request_body: bool = Field(default=False, alias='LOG_REQUEST_BODY')
    log_to_file: bool = Field(default=True, alias='LOG_TO_FILE')

    @field_validator('log_file_path', mode='before')
    @classmethod
    def _resolve_log_path(cls, value: str | Path) -> Path:
        """Método interno: resolve log path."""
        return resolve_project_path(value)
