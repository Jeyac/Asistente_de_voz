"""
Agregador de configuración modular desde variables de entorno.

Combina App, Server, ML, WakeWord, Actions, etc. en un único objeto Settings.
Se carga desde .env y variables del sistema (p. ej. Render).
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from asistente_voz.core.config.actions_config import ActionsConfig
from asistente_voz.core.config.app_config import AppConfig
from asistente_voz.core.config.base import PROJECT_ROOT
from asistente_voz.core.config.data_config import DataConfig
from asistente_voz.core.config.logging_config import LoggingConfig
from asistente_voz.core.config.ml_config import MlConfig
from asistente_voz.core.config.server_config import ServerConfig
from asistente_voz.core.config.wakeword_config import WakeWordConfig


class Settings(
    AppConfig,
    ServerConfig,
    LoggingConfig,
    DataConfig,
    MlConfig,
    WakeWordConfig,
    ActionsConfig,
    BaseSettings,
):
    """Configuración unificada cargada desde entorno y archivo `.env`."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Singleton de configuración (cacheado)."""
    return Settings()
