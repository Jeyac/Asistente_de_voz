"""Entrenamiento del clasificador de intenciones."""
from tensorflow import keras
from tensorflow.keras import callbacks
from asistente_voz.core.config.settings import Settings
from asistente_voz.core.logging.setup import get_logger
from asistente_voz.domain.entities.training_metrics import TrainingMetrics
from asistente_voz.infrastructure.ml.tensorflow.artifacts.artifact_store import ArtifactStore
from asistente_voz.infrastructure.ml.tensorflow.model.architecture import IntentClassifierModelFactory
from asistente_voz.infrastructure.ml.tensorflow.nlp.label_encoder import LabelEncoder
from asistente_voz.infrastructure.ml.tensorflow.nlp.pipeline import NlpPipeline
from asistente_voz.infrastructure.ml.tensorflow.nlp.text_cleaner import TextCleaner
from asistente_voz.infrastructure.ml.tensorflow.nlp.text_vectorizer import TextVectorizer
from asistente_voz.infrastructure.ml.tensorflow.training.dataset_builder import TrainingDatasetBuilder
from asistente_voz.infrastructure.ml.tensorflow.training.evaluator import ModelEvaluator
from asistente_voz.infrastructure.persistence.json.intents_repository import IntentsRepository
logger = get_logger(__name__)

class IntentModelTrainer:
    """Pipeline completo de entrenamiento y persistencia."""

    def __init__(self, settings: Settings, intents_repository: IntentsRepository, artifact_store: ArtifactStore) -> None:
        """Inicializa la instancia."""
        self._settings = settings
        self._intents_repository = intents_repository
        self._artifact_store = artifact_store
        self._model_factory = IntentClassifierModelFactory()
        self._evaluator = ModelEvaluator()

    def train(self) -> TrainingMetrics:
        """Función train."""
        texts, labels = self._intents_repository.load_training_pairs()
        pipeline = self._build_pipeline()
        dataset_builder = TrainingDatasetBuilder(pipeline)
        features, encoded_labels = dataset_builder.build(texts, labels)
        model = self._model_factory.build(vocab_size=len(pipeline.vectorizer.get_vocabulary()), num_classes=pipeline.label_encoder.num_classes, sequence_length=self._settings.tf_sequence_length, embedding_dim=self._settings.tf_embedding_dim)
        model.compile(optimizer=keras.optimizers.Adam(learning_rate=self._settings.tf_learning_rate), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        num_samples = len(texts)
        use_validation = num_samples >= 100 and self._settings.tf_validation_split > 0
        validation_split = self._settings.tf_validation_split if use_validation else 0.0
        fit_callbacks: list[callbacks.Callback] = []
        if use_validation:
            fit_callbacks.append(callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True))
        else:
            logger.info('Dataset pequeño (%s muestras): entrenamiento sin validación ni early stopping', num_samples)
        history = model.fit(features, encoded_labels, epochs=self._settings.tf_epochs, batch_size=min(self._settings.tf_batch_size, max(1, num_samples // 4)), validation_split=validation_split, verbose=1, callbacks=fit_callbacks)
        metrics = self._evaluator.evaluate(model, features, encoded_labels, history)
        classification_report = self._evaluator.classification_report(model, features, encoded_labels, pipeline.label_encoder)
        self._artifact_store.save(model=model, pipeline=pipeline, metrics=metrics, classification_report=classification_report)
        logger.info('Entrenamiento finalizado | accuracy=%.4f | val_accuracy=%.4f', metrics.accuracy, metrics.val_accuracy)
        return metrics

    def _build_pipeline(self) -> NlpPipeline:
        """Método interno: build pipeline."""
        vectorizer = TextVectorizer(max_tokens=self._settings.tf_max_vocab_size, sequence_length=self._settings.tf_sequence_length)
        return NlpPipeline(cleaner=TextCleaner(), vectorizer=vectorizer, label_encoder=LabelEncoder())
