"""Operaciones genéricas de lectura/escritura JSON."""

import json
from pathlib import Path
from typing import Any

from asistente_voz.domain.exceptions.base import NotFoundError, ValidationError


class JsonFileRepository:
    """Acceso a archivos JSON con validación básica."""

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path

    @property
    def file_path(self) -> Path:
        return self._file_path

    def exists(self) -> bool:
        return self._file_path.is_file()

    def read(self) -> dict[str, Any]:
        if not self.exists():
            raise NotFoundError(
                message=f"Archivo no encontrado: {self._file_path}",
                details={"path": str(self._file_path)},
            )
        try:
            with self._file_path.open(encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            raise ValidationError(
                message=f"JSON inválido en {self._file_path}",
                details={"error": str(exc)},
            ) from exc
        if not isinstance(data, dict):
            raise ValidationError(message="El JSON raíz debe ser un objeto.")
        return data

    def write(self, data: dict[str, Any]) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        with self._file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
