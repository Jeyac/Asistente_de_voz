"""Construcción de tensores de entrenamiento."""

import numpy as np

from asistente_voz.infrastructure.ml.tensorflow.nlp.pipeline import NlpPipeline


class TrainingDatasetBuilder:
    """Prepara features y etiquetas para Keras."""

    def __init__(self, pipeline: NlpPipeline) -> None:
        self._pipeline = pipeline

    def build(self, texts: list[str], labels: list[str]) -> tuple[np.ndarray, np.ndarray]:
        self._pipeline.fit(texts, labels)
        features = self._pipeline.transform_texts(texts)
        encoded_labels = np.array(self._pipeline.transform_labels(labels), dtype=np.int32)
        return features, encoded_labels
