"""Factory de componentes de machine learning."""

from asistente_voz.application.services.model_registry import IntentModelRegistry
from asistente_voz.application.use_cases.classify_intent import ClassifyIntentUseCase
from asistente_voz.core.config.settings import Settings


class MlFactory:
    """Construye dependencias del subsistema de IA."""

    def __init__(self, settings: Settings, registry: IntentModelRegistry) -> None:
        self._settings = settings
        self._registry = registry

    def create_intents_repository(self):
        from asistente_voz.infrastructure.persistence.json.base_repository import JsonFileRepository
        from asistente_voz.infrastructure.persistence.json.intents_repository import (
            IntentsRepository,
        )

        json_repo = JsonFileRepository(self._settings.intents_dataset_path)
        return IntentsRepository(json_repo)

    def create_model_loader(self):
        from asistente_voz.infrastructure.ml.tensorflow.model_loader import IntentModelLoader

        return IntentModelLoader(self._settings)

    def create_trainer(self):
        from asistente_voz.infrastructure.ml.tensorflow.artifacts.artifact_store import (
            ArtifactStore,
        )
        from asistente_voz.infrastructure.ml.tensorflow.training.trainer import IntentModelTrainer

        return IntentModelTrainer(
            settings=self._settings,
            intents_repository=self.create_intents_repository(),
            artifact_store=ArtifactStore(self._settings),
        )

    def create_classifier(self):
        from asistente_voz.infrastructure.ml.tensorflow.intent_classifier import (
            TensorFlowIntentClassifier,
        )

        return TensorFlowIntentClassifier(self._registry.predictor)

    def create_classify_use_case(self) -> ClassifyIntentUseCase:
        return ClassifyIntentUseCase(self._registry.predictor)
