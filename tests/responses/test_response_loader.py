"""Pruebas del cargador de respuestas."""

from pathlib import Path

from asistente_voz.infrastructure.persistence.json.base_repository import JsonFileRepository
from asistente_voz.infrastructure.responses.response_loader import ResponseLoader


def test_load_catalog_with_extended_format() -> None:
    path = Path(__file__).resolve().parents[2] / "data" / "responses" / "responses.json"
    loader = ResponseLoader(JsonFileRepository(path))
    catalog = loader.load()
    saludo = catalog.get("saludo")
    assert saludo is not None
    assert saludo.count >= 3
    assert "Hola" in saludo.variants[0]


def test_supports_legacy_list_format(tmp_path: Path) -> None:
    json_file = tmp_path / "responses.json"
    json_file.write_text(
        '{"version":"1.0","default_intent":"desconocido","responses":{"test":["a","b"]}}',
        encoding="utf-8",
    )
    loader = ResponseLoader(JsonFileRepository(json_file))
    catalog = loader.load()
    assert catalog.get("test").count == 2
