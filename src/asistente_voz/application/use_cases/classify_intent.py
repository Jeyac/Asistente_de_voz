"""Caso de uso: clasificar intención a partir de texto."""

import asyncio
from typing import Any

from asistente_voz.domain.entities.prediction_result import PredictionResult
from asistente_voz.domain.exceptions.ml_exceptions import ModelNotLoadedError


class ClassifyIntentUseCase:
    """Orquesta la predicción de intenciones."""

    def __init__(self, predictor: Any | None) -> None:
        self._predictor = predictor

    async def execute(self, text: str) -> PredictionResult:
        if self._predictor is None:
            raise ModelNotLoadedError()

        raw_result = await asyncio.to_thread(self._predictor.predict, text)
        return PredictionResult(
            intent=raw_result.intent,
            confidence=raw_result.confidence,
            raw_text=raw_result.raw_text,
            cleaned_text=raw_result.cleaned_text,
            above_threshold=raw_result.above_threshold,
            probabilities=raw_result.probabilities,
        )
