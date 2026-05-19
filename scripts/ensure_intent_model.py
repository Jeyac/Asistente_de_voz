#!/usr/bin/env python
"""Entrena el modelo de intenciones (siempre o si el dataset cambió)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def _always_retrain() -> bool:
    value = os.getenv("RETRAIN_INTENTS_ALWAYS", "false").strip().lower()
    return value in {"1", "true", "yes", "on"}


def _dataset_newer_than_model(dataset: Path, model_file: Path) -> bool:
    if not model_file.is_file():
        return True
    return dataset.stat().st_mtime > model_file.stat().st_mtime


def main() -> int:
    from asistente_voz.application.factories.ml_factory import MlFactory
    from asistente_voz.application.services.model_registry import get_model_registry
    from asistente_voz.core.config.settings import get_settings
    from asistente_voz.core.logging.setup import configure_logging, get_logger
    from asistente_voz.infrastructure.ml.tensorflow.artifacts.artifact_store import ArtifactStore

    settings = get_settings()
    configure_logging(settings)
    logger = get_logger(__name__)

    store = ArtifactStore(settings)
    dataset = settings.intents_dataset_path.resolve()
    model_file = store.paths.model_file.resolve()

    if not dataset.is_file():
        logger.error("Dataset no encontrado: %s", dataset)
        return 1

    must_train = _always_retrain() or _dataset_newer_than_model(dataset, model_file)
    if not must_train:
        logger.info("Modelo actualizado; omitiendo reentrenamiento.")
        return 0

    reason = "RETRAIN_INTENTS_ALWAYS=true" if _always_retrain() else "dataset más reciente que el modelo"
    logger.info("Reentrenando modelo de intenciones | motivo=%s | dataset=%s", reason, dataset)

    factory = MlFactory(settings, get_model_registry())
    metrics = factory.create_trainer().train()
    logger.info(
        "Entrenamiento OK | accuracy=%.4f | val_accuracy=%.4f | epochs=%s",
        metrics.accuracy,
        metrics.val_accuracy,
        metrics.epochs_trained,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
