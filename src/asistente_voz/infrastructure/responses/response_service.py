"""Servicio de respuestas inteligentes basado en catálogo JSON."""
import asyncio
from datetime import datetime
from asistente_voz.application.interfaces.response_provider import IResponseProvider
from asistente_voz.application.interfaces.response_selector import IResponseSelector
from asistente_voz.core.config.settings import Settings
from asistente_voz.core.logging.setup import get_logger
from asistente_voz.domain.entities.intent_responses import IntentResponses, ResponseCatalog
from asistente_voz.domain.entities.prediction_result import PredictionResult
from asistente_voz.domain.entities.smart_response import SmartResponse
from asistente_voz.domain.exceptions.base import ValidationError
from asistente_voz.infrastructure.responses.response_loader import ResponseLoader
logger = get_logger(__name__)

class SmartResponseService(IResponseProvider):
    """Resuelve respuestas según intención con selección aleatoria."""

    def __init__(self, loader: ResponseLoader, selector: IResponseSelector, settings: Settings) -> None:
        """Inicializa la instancia."""
        self._loader = loader
        self._selector = selector
        self._settings = settings
        self._catalog_cache: ResponseCatalog | None = None

    async def get_catalog(self) -> ResponseCatalog:
        """Obtiene catalog."""
        return await asyncio.to_thread(self._load_catalog)

    async def get_response(self, intent_name: str) -> str:
        """Obtiene response."""
        smart = await self.generate_for_intent(intent_name, confidence=1.0, above_threshold=True)
        return smart.message

    async def generate_from_prediction(self, prediction: PredictionResult) -> SmartResponse:
        """Función generate from prediction."""
        intent_name = prediction.intent
        if not prediction.above_threshold:
            intent_name = self._resolve_fallback_intent()
        return await self.generate_for_intent(intent_name=intent_name, confidence=prediction.confidence, above_threshold=prediction.above_threshold, used_fallback=not prediction.above_threshold)

    async def generate_for_intent(self, intent_name: str, *, confidence: float=1.0, above_threshold: bool=True, used_fallback: bool=False) -> SmartResponse:
        """Función generate for intent."""
        catalog = await self.get_catalog()
        intent_responses = self._resolve_intent(catalog, intent_name)
        message = self._build_message(intent_responses.intent, intent_responses.variants)
        logger.info('Respuesta generada | intent=%s | variants=%s | fallback=%s', intent_responses.intent, intent_responses.count, used_fallback)
        return SmartResponse(intent=intent_responses.intent, message=message, confidence=confidence, above_threshold=above_threshold, variants_available=intent_responses.count, used_fallback=used_fallback)

    def _load_catalog(self) -> ResponseCatalog:
        """Método interno: load catalog."""
        if self._catalog_cache is None:
            self._catalog_cache = self._loader.load()
            self._validate_catalog(self._catalog_cache)
        return self._catalog_cache

    def reload_catalog(self) -> ResponseCatalog:
        """Recarga el JSON (útil tras editar respuestas sin reiniciar)."""
        self._catalog_cache = None
        return self._load_catalog()

    def _resolve_fallback_intent(self) -> str:
        """Método interno: resolve fallback intent."""
        catalog = self._load_catalog()
        return catalog.default_intent or self._settings.tf_fallback_intent

    def _resolve_intent(self, catalog: ResponseCatalog, intent_name: str) -> IntentResponses:
        """Método interno: resolve intent."""
        intent_responses = catalog.get(intent_name)
        if intent_responses and intent_responses.enabled and intent_responses.variants:
            return intent_responses
        fallback_name = catalog.default_intent or self._settings.tf_fallback_intent
        fallback = catalog.get(fallback_name)
        if fallback and fallback.variants:
            return fallback
        raise ValidationError(message=f"No hay respuestas para '{intent_name}' ni para el fallback '{fallback_name}'.")

    def _build_message(self, intent_name: str, variants: list[str]) -> str:
        """Selecciona variante y enriquece respuestas dinámicas (p. ej. hora actual)."""
        if intent_name == 'hora':
            now = datetime.now().strftime('%H:%M')
            return f'Son las {now}.'
        if intent_name == 'creador':
            name = self._settings.creator_name
            title = self._settings.creator_display_title
            return self._selector.select(variants).format(nombre=name, titulo=title)
        if intent_name == 'relacion_creador':
            partner = self._settings.partner_name
            title = self._settings.partner_display_title
            creadora = self._settings.creator_name
            return self._selector.select(variants).format(pareja=partner, titulo=title, creadora=creadora)
        return self._selector.select(variants)

    @staticmethod
    def _validate_catalog(catalog: ResponseCatalog) -> None:
        """Método interno: validate catalog."""
        if not catalog.intents:
            raise ValidationError(message='El catálogo de respuestas está vacío.')
        for intent in catalog.intents:
            if intent.enabled and (not intent.variants):
                raise ValidationError(message=f"La intención '{intent.intent}' no tiene variantes configuradas.")
