"""Adaptador TensorFlow del puerto IIntentClassifier."""

import asyncio

from asistente_voz.application.interfaces.intent_classifier import IIntentClassifier
from asistente_voz.domain.entities.intent import Intent
from asistente_voz.domain.exceptions.ml_exceptions import ModelNotLoadedError
from asistente_voz.infrastructure.ml.tensorflow.inference.predictor import IntentPredictor


class TensorFlowIntentClassifier(IIntentClassifier):
    """Clasifica intenciones usando el modelo Keras cargado."""

    def __init__(self, predictor: IntentPredictor | None) -> None:
        self._predictor = predictor

    @property
    def is_ready(self) -> bool:
        return self._predictor is not None

    async def classify(self, text: str) -> Intent:
        if self._predictor is None:
            raise ModelNotLoadedError()
        result = await asyncio.to_thread(self._predictor.predict, text)
        return Intent(
            name=result.intent,
            confidence=result.confidence,
            raw_text=result.raw_text,
        )
