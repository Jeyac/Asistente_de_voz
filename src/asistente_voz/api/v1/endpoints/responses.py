"""Endpoints REST de respuestas inteligentes."""
from fastapi import APIRouter, status
from asistente_voz.api.dependencies import GenerateSmartResponseUseCaseDep, RespondToIntentUseCaseDep, ResponseServiceDep
from asistente_voz.domain.entities.smart_response import SmartResponse
from asistente_voz.schemas.response import GenerateResponseRequest, GenerateResponseResult, IntentCatalogItem, ResponseCatalogSchema, SmartResponseSchema
router = APIRouter()

def _to_schema(smart: SmartResponse) -> SmartResponseSchema:
    """Método interno: to schema."""
    return SmartResponseSchema(intent=smart.intent, message=smart.message, confidence=round(smart.confidence, 4), above_threshold=smart.above_threshold, variants_available=smart.variants_available, used_fallback=smart.used_fallback)

@router.post('/generate', response_model=GenerateResponseResult, status_code=status.HTTP_200_OK, summary='Clasificar y responder', description='Clasifica el texto con TensorFlow y devuelve una respuesta aleatoria del catálogo JSON.')
async def generate_response(payload: GenerateResponseRequest, use_case: RespondToIntentUseCaseDep) -> GenerateResponseResult:
    """Función generate response."""
    result = await use_case.execute(payload.text)
    return GenerateResponseResult(transcript=result.transcript, intent=result.response.intent, confidence=round(result.confidence, 4), above_threshold=result.above_threshold, cleaned_text=result.cleaned_text, probabilities={k: round(v, 4) for k, v in result.probabilities.items()}, response=_to_schema(result.response))

@router.get('/catalog', response_model=ResponseCatalogSchema, summary='Catálogo de respuestas')
async def get_catalog(service: ResponseServiceDep) -> ResponseCatalogSchema:
    """Obtiene catalog."""
    catalog = await service.get_catalog()
    return ResponseCatalogSchema(version=catalog.version, default_intent=catalog.default_intent, intents=[IntentCatalogItem(intent=item.intent, variants_count=item.count, enabled=item.enabled) for item in catalog.intents])

@router.get('/{intent_name}', response_model=SmartResponseSchema, summary='Respuesta aleatoria por intención')
async def get_response_for_intent(intent_name: str, use_case: GenerateSmartResponseUseCaseDep) -> SmartResponseSchema:
    """Obtiene response for intent."""
    smart = await use_case.execute_for_intent(intent_name)
    return _to_schema(smart)
