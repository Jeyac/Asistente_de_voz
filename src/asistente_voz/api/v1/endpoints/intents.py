"""Endpoints REST de clasificación de intenciones."""
from fastapi import APIRouter, status
from asistente_voz.api.dependencies import ClassifyIntentUseCaseDep, SettingsDep
from asistente_voz.application.services.model_registry import get_model_registry
from asistente_voz.infrastructure.ml.tensorflow.artifacts.artifact_paths import ArtifactPaths
from asistente_voz.domain.entities.prediction_result import PredictionResult
from asistente_voz.schemas.intent import IntentPredictRequest, IntentPredictResponse, ModelStatusResponse
router = APIRouter()

def _to_response(result: PredictionResult) -> IntentPredictResponse:
    """Método interno: to response."""
    return IntentPredictResponse(intent=result.intent, confidence=round(result.confidence, 4), raw_text=result.raw_text, cleaned_text=result.cleaned_text, above_threshold=result.above_threshold, probabilities={key: round(value, 4) for key, value in result.probabilities.items()})

@router.post('/predict', response_model=IntentPredictResponse, status_code=status.HTTP_200_OK, summary='Predecir intención', description='Clasifica el texto del usuario usando el modelo TensorFlow entrenado.')
async def predict_intent(payload: IntentPredictRequest, use_case: ClassifyIntentUseCaseDep) -> IntentPredictResponse:
    """Función predict intent."""
    result = await use_case.execute(payload.text)
    return _to_response(result)

@router.get('/model/status', response_model=ModelStatusResponse, summary='Estado del modelo')
async def model_status(settings: SettingsDep) -> ModelStatusResponse:
    """Función model status."""
    registry = get_model_registry()
    paths = ArtifactPaths.from_settings(settings)
    metadata = registry.metadata or {}
    return ModelStatusResponse(loaded=registry.is_loaded, labels=metadata.get('labels'), model_path=str(paths.model_file) if registry.is_loaded else None)
