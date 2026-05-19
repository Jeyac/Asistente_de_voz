"""Configuración de acciones del sistema (abrir apps, URLs)."""

from pydantic import Field


class ActionsConfig:
    """Parámetros para ejecutar acciones reales en el equipo del usuario."""

    enable_system_actions: bool = Field(default=True, alias="ENABLE_SYSTEM_ACTIONS")
    creator_name: str = Field(default="Jéraldyn", alias="CREATOR_NAME")
    creator_display_title: str = Field(
        default="la hermosa, inteligente, capaz, independiente, empoderada y maravillosa",
        alias="CREATOR_DISPLAY_TITLE",
    )
    partner_name: str = Field(default="Kevin Estrada", alias="PARTNER_NAME")
    partner_display_title: str = Field(
        default="su guapo, precioso, hermoso, maravilloso e increíble novio",
        alias="PARTNER_DISPLAY_TITLE",
    )
