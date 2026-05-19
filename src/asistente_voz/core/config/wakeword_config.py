"""Configuración del detector de palabra clave."""

from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator

from asistente_voz.core.config.base import resolve_project_path


class WakeWordConfig:
    """Parámetros de activación por palabra clave."""

    wakeword_enabled: bool = Field(default=True, alias="WAKEWORD_ENABLED")
    wakeword_engine: Literal["openwakeword", "porcupine"] = Field(
        default="openwakeword",
        alias="WAKEWORD_ENGINE",
    )
    wakeword_phrase: str = Field(default="oye sistema", alias="WAKEWORD_PHRASE")
    wakeword_model_path: Path = Field(
        default=Path("models/wakeword/oye_sistema.onnx"),
        alias="WAKEWORD_MODEL_PATH",
    )
    wakeword_threshold: float = Field(default=0.5, alias="WAKEWORD_THRESHOLD")
    wakeword_listen_timeout: float = Field(
        default=60.0,
        alias="WAKEWORD_LISTEN_TIMEOUT",
    )
    wakeword_chunk_duration_ms: int = Field(
        default=80,
        alias="WAKEWORD_CHUNK_DURATION_MS",
    )
    porcupine_access_key: str = Field(default="", alias="PORCUPINE_ACCESS_KEY")
    porcupine_keyword_path: Path = Field(
        default=Path("models/wakeword/oye_sistema_es_windows.ppn"),
        alias="PORCUPINE_KEYWORD_PATH",
    )

    @field_validator("wakeword_model_path", "porcupine_keyword_path", mode="before")
    @classmethod
    def _resolve_paths(cls, value: str | Path) -> Path:
        return resolve_project_path(value)

    @property
    def wakeword_keyword_id(self) -> str:
        """Identificador sanitizado para el modelo (oye_sistema)."""
        return self.wakeword_phrase.strip().lower().replace(" ", "_")
