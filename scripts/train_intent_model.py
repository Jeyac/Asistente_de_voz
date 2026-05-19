#!/usr/bin/env python
"""Script CLI para entrenar el clasificador de intenciones."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from asistente_voz.application.factories.ml_factory import MlFactory
from asistente_voz.application.services.model_registry import get_model_registry
from asistente_voz.core.config.settings import get_settings
from asistente_voz.core.logging.setup import configure_logging, get_logger

logger = get_logger(__name__)


def main() -> int:
    settings = get_settings()
    configure_logging(settings)
    factory = MlFactory(settings, get_model_registry())
    trainer = factory.create_trainer()

    logger.info("Iniciando entrenamiento del modelo de intenciones...")
    metrics = trainer.train()
    logger.info(
        "Entrenamiento completado | accuracy=%.4f | val_accuracy=%.4f | epochs=%s",
        metrics.accuracy,
        metrics.val_accuracy,
        metrics.epochs_trained,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
