"""Constantes y utilidades compartidas de configuración."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]


def resolve_project_path(value: str | Path) -> Path:
    """Resuelve rutas relativas respecto a la raíz del proyecto."""
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path
