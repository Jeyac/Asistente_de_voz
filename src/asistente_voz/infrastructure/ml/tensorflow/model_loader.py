"""Carga automática de modelo y artefactos TensorFlow."""
from dataclasses import dataclass
from tensorflow import keras
from asistente_voz.core.config.settings import Settings
from asistente_voz.core.logging.setup import get_logger
from asistente_voz.infrastructure.ml.tensorflow.artifacts.artifact_paths import ArtifactPaths
from asistente_voz.infrastructure.ml.tensorflow.artifacts.artifact_store import ArtifactStore
from asistente_voz.infrastructure.ml.tensorflow.inference.predictor import IntentPredictor
from asistente_voz.infrastructure.ml.tensorflow.nlp.label_encoder import LabelEncoder
from asistente_voz.infrastructure.ml.tensorflow.nlp.pipeline import NlpPipeline
from asistente_voz.infrastructure.ml.tensorflow.nlp.text_cleaner import TextCleaner
from asistente_voz.infrastructure.ml.tensorflow.nlp.text_vectorizer import TextVectorizer
logger = get_logger(__name__)

@dataclass(slots=True)
class LoadedIntentModel:
    """Contenedor de componentes cargados para inferencia."""
    predictor: IntentPredictor
    paths: ArtifactPaths
    metadata: dict

class IntentModelLoader:
    """Carga modelo Keras, tokenizer y etiquetas desde disco."""

    def __init__(self, settings: Settings) -> None:
        """Inicializa la instancia."""
        self._settings = settings
        self._artifact_store = ArtifactStore(settings)
        self._paths = self._artifact_store.paths

    @property
    def is_available(self) -> bool:
        """Indica si available."""
        return self._paths.all_exist()

    def load(self) -> LoadedIntentModel:
        """Carga datos o artefactos desde disco."""
        if not self.is_available:
            missing = [str(path) for path in (self._paths.model_file, self._paths.tokenizer_file, self._paths.labels_file, self._paths.metadata_file) if not path.is_file()]
            raise FileNotFoundError(f'Artefactos incompletos. Archivos faltantes: {missing}')
        metadata = self._artifact_store.load_metadata()
        model = keras.models.load_model(self._paths.model_file)
        vectorizer = TextVectorizer.load(self._paths.tokenizer_file)
        label_encoder = LabelEncoder.load(self._paths.labels_file)
        pipeline = NlpPipeline(cleaner=TextCleaner(), vectorizer=vectorizer, label_encoder=label_encoder)
        predictor = IntentPredictor(model=model, pipeline=pipeline, confidence_threshold=float(metadata.get('confidence_threshold', self._settings.tf_confidence_threshold)), fallback_intent=str(metadata.get('fallback_intent', self._settings.tf_fallback_intent)))
        logger.info('Modelo cargado | clases=%s | path=%s', label_encoder.labels, self._paths.model_file)
        return LoadedIntentModel(predictor=predictor, paths=self._paths, metadata=metadata)
