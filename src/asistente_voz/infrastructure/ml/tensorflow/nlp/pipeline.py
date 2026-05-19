"""Pipeline NLP: limpieza + vectorización."""
from asistente_voz.infrastructure.ml.tensorflow.nlp.label_encoder import LabelEncoder
from asistente_voz.infrastructure.ml.tensorflow.nlp.text_cleaner import TextCleaner
from asistente_voz.infrastructure.ml.tensorflow.nlp.text_vectorizer import TextVectorizer

class NlpPipeline:
    """Orquesta preprocesamiento de texto para entrenamiento e inferencia."""

    def __init__(self, cleaner: TextCleaner, vectorizer: TextVectorizer, label_encoder: LabelEncoder) -> None:
        """Inicializa la instancia."""
        self._cleaner = cleaner
        self._vectorizer = vectorizer
        self._label_encoder = label_encoder

    @property
    def cleaner(self) -> TextCleaner:
        """Función cleaner."""
        return self._cleaner

    @property
    def vectorizer(self) -> TextVectorizer:
        """Función vectorizer."""
        return self._vectorizer

    @property
    def label_encoder(self) -> LabelEncoder:
        """Función label encoder."""
        return self._label_encoder

    def clean(self, text: str) -> str:
        """Función clean."""
        return self._cleaner.clean(text)

    def clean_batch(self, texts: list[str]) -> list[str]:
        """Función clean batch."""
        return [self.clean(text) for text in texts]

    def fit(self, texts: list[str], labels: list[str]) -> None:
        """Función fit."""
        cleaned_texts = self.clean_batch(texts)
        self._vectorizer.adapt(cleaned_texts)
        self._label_encoder.fit(labels)

    def transform_texts(self, texts: list[str]):
        """Función transform texts."""
        cleaned = self.clean_batch(texts)
        return self._vectorizer.transform(cleaned)

    def transform_labels(self, labels: list[str]) -> list[int]:
        """Función transform labels."""
        return self._label_encoder.encode(labels)
