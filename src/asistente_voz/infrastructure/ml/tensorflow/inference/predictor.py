"""Predicción de intenciones con score de confianza."""

import numpy as np
from tensorflow import keras

from asistente_voz.domain.entities.prediction_result import PredictionResult
from asistente_voz.infrastructure.ml.tensorflow.nlp.pipeline import NlpPipeline


class IntentPredictor:
    """Ejecuta inferencia sobre el modelo cargado."""

    def __init__(
        self,
        model: keras.Model,
        pipeline: NlpPipeline,
        confidence_threshold: float,
        fallback_intent: str,
    ) -> None:
        self._model = model
        self._pipeline = pipeline
        self._confidence_threshold = confidence_threshold
        self._fallback_intent = fallback_intent

    def predict(self, text: str) -> PredictionResult:
        cleaned = self._pipeline.clean(text)
        features = self._pipeline.transform_texts([cleaned])
        probabilities = self._model.predict(features, verbose=0)[0]
        best_index = int(np.argmax(probabilities))
        confidence = float(probabilities[best_index])
        intent = self._pipeline.label_encoder.decode(best_index)
        above_threshold = confidence >= self._confidence_threshold

        if not above_threshold:
            intent = self._fallback_intent

        probability_map = {
            self._pipeline.label_encoder.decode(index): float(score)
            for index, score in enumerate(probabilities)
        }

        return PredictionResult(
            intent=intent,
            confidence=confidence,
            raw_text=text,
            cleaned_text=cleaned,
            above_threshold=above_threshold,
            probabilities=probability_map,
        )
