"""Configuración del servidor HTTP y CORS."""

from pydantic import Field


class ServerConfig:
    """Parámetros de red y seguridad CORS."""

    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    workers: int = Field(default=1, alias="WORKERS")
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="CORS_ORIGINS",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Orígenes CORS parseados desde cadena separada por comas."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
