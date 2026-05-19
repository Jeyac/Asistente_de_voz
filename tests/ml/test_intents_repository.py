"""Pruebas del repositorio de intenciones."""

from pathlib import Path

from asistente_voz.infrastructure.persistence.json.base_repository import JsonFileRepository
from asistente_voz.infrastructure.persistence.json.intents_repository import IntentsRepository


def test_load_training_pairs_from_dataset() -> None:
    dataset_path = Path(__file__).resolve().parents[2] / "data" / "intents" / "intents_dataset.json"
    repository = IntentsRepository(JsonFileRepository(dataset_path))
    texts, labels = repository.load_training_pairs()
    assert len(texts) == len(labels) > 0
    assert "saludo" in labels
    assert "abrir_youtube" in labels
