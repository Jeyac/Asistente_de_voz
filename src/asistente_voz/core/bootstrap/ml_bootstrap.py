"""Inicialización del modelo de intenciones en el arranque."""

from asistente_voz.application.factories.ml_factory import MlFactory
from asistente_voz.application.services.model_registry import get_model_registry
from asistente_voz.core.config.settings import Settings
from asistente_voz.core.logging.setup import get_logger

logger = get_logger(__name__)


def bootstrap_intent_model(settings: Settings) -> None:
    """Carga automática del modelo si los artefactos existen."""
    registry = get_model_registry()
    loader = MlFactory(settings, registry).create_model_loader()

    if not loader.is_available:
        logger.warning(
            "Modelo de intenciones no encontrado. Ejecute: "
            "python scripts/train_intent_model.py",
        )
        return

    try:
        loaded = loader.load()
        factory = MlFactory(settings, registry)
        definitions = factory.create_intents_repository().load_definitions()
        from asistente_voz.infrastructure.ml.hybrid_intent_predictor import HybridIntentPredictor
        from asistente_voz.infrastructure.ml.keyword_intent_matcher import KeywordIntentMatcher

        tf_predictor = loaded.predictor
        tf_label_count = len(tf_predictor._pipeline.label_encoder.labels)
        hybrid = HybridIntentPredictor(
            tf_predictor,
            KeywordIntentMatcher(definitions),
            fallback_intent=tf_predictor._fallback_intent,
        )
        loaded.predictor = hybrid  # type: ignore[misc]
        registry.register(loaded)
        logger.info(
            "Clasificador híbrido activo | intenciones_dataset=%s | intenciones_modelo=%s",
            len(definitions),
            tf_label_count,
        )
    except Exception:
        logger.exception("Error al cargar el modelo de intenciones")
        registry.clear()
