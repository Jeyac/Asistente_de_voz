"""Persistencia y carga de artefactos del modelo."""

import json
from dataclasses import asdict
from typing import Any

from tensorflow import keras

from asistente_voz.core.config.settings import Settings
from asistente_voz.core.logging.setup import get_logger
from asistente_voz.domain.entities.training_metrics import TrainingMetrics
from asistente_voz.infrastructure.ml.tensorflow.artifacts.artifact_paths import ArtifactPaths
from asistente_voz.infrastructure.ml.tensorflow.nlp.pipeline import NlpPipeline

logger = get_logger(__name__)


class ArtifactStore:
    """Guarda y recupera modelo, tokenizer, etiquetas y métricas."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._paths = ArtifactPaths.from_settings(settings)

    @property
    def paths(self) -> ArtifactPaths:
        return self._paths

    def save(
        self,
        model: keras.Model,
        pipeline: NlpPipeline,
        metrics: TrainingMetrics,
        classification_report: dict[str, Any],
    ) -> None:
        self._paths.models_dir.mkdir(parents=True, exist_ok=True)
        model.save(self._paths.model_file)
        pipeline.vectorizer.save(self._paths.tokenizer_file)
        pipeline.label_encoder.save(self._paths.labels_file)

        metadata = {
            "metrics": asdict(metrics),
            "classification_report": classification_report,
            "confidence_threshold": self._settings.tf_confidence_threshold,
            "fallback_intent": self._settings.tf_fallback_intent,
            "labels": pipeline.label_encoder.labels,
        }
        self._paths.metadata_file.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("Artefactos guardados en %s", self._paths.models_dir)

    def load_metadata(self) -> dict[str, Any]:
        return json.loads(self._paths.metadata_file.read_text(encoding="utf-8"))
