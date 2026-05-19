"""Configuración de la aplicación y documentación OpenAPI."""

from typing import Literal

from pydantic import Field


class AppConfig:
    """Parámetros generales de la aplicación."""

    app_name: str = Field(default="Asistente de Voz API", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    app_env: Literal["development", "staging", "production"] = Field(
        default="development",
        alias="APP_ENV",
    )
    debug: bool = Field(default=False, alias="DEBUG")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    enable_docs: bool = Field(default=True, alias="ENABLE_DOCS")
    api_description: str = Field(
        default=(
            "API REST del asistente de voz profesional. "
            "Reconocimiento de voz, clasificación de intenciones y respuestas dinámicas."
        ),
        alias="API_DESCRIPTION",
    )

    @property
    def is_production(self) -> bool:
        """Indica si la aplicación corre en entorno de producción."""
        return self.app_env == "production"

    @property
    def docs_enabled(self) -> bool:
        """Determina si Swagger/ReDoc están habilitados."""
        if not self.enable_docs:
            return False
        return self.debug or not self.is_production
