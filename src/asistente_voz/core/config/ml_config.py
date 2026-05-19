"""Configuración de servicios de voz, NLP y machine learning."""

from pydantic import Field


class MlConfig:
    """Parámetros de SpeechRecognition, spaCy y TensorFlow."""

    speech_recognition_language: str = Field(
        default="es-ES",
        alias="SPEECH_RECOGNITION_LANGUAGE",
    )
    speech_recognition_timeout: int = Field(
        default=5,
        alias="SPEECH_RECOGNITION_TIMEOUT",
    )
    speech_recognition_phrase_limit: int = Field(
        default=10,
        alias="SPEECH_RECOGNITION_PHRASE_LIMIT",
    )
    speech_ambient_noise_duration: float = Field(
        default=0.5,
        alias="SPEECH_AMBIENT_NOISE_DURATION",
    )
    speech_post_wakeword_pause: float = Field(
        default=1.0,
        alias="SPEECH_POST_WAKEWORD_PAUSE",
    )
    speech_post_wakeword_timeout: int = Field(
        default=8,
        alias="SPEECH_POST_WAKEWORD_TIMEOUT",
    )
    speech_post_wakeword_phrase_limit: int = Field(
        default=12,
        alias="SPEECH_POST_WAKEWORD_PHRASE_LIMIT",
    )
    speech_post_wakeword_ambient_duration: float = Field(
        default=1.2,
        alias="SPEECH_POST_WAKEWORD_AMBIENT_DURATION",
    )
    speech_max_audio_bytes: int = Field(
        default=5_242_880,
        alias="SPEECH_MAX_AUDIO_BYTES",
    )
    speech_allowed_formats: str = Field(
        default="wav,wave",
        alias="SPEECH_ALLOWED_FORMATS",
    )
    spacy_model: str = Field(default="es_core_news_sm", alias="SPACY_MODEL")
    tf_confidence_threshold: float = Field(
        default=0.75,
        alias="TF_CONFIDENCE_THRESHOLD",
    )
    tf_fallback_intent: str = Field(default="desconocido", alias="TF_FALLBACK_INTENT")
    tf_max_vocab_size: int = Field(default=2000, alias="TF_MAX_VOCAB_SIZE")
    tf_sequence_length: int = Field(default=20, alias="TF_SEQUENCE_LENGTH")
    tf_embedding_dim: int = Field(default=64, alias="TF_EMBEDDING_DIM")
    tf_epochs: int = Field(default=80, alias="TF_EPOCHS")
    tf_batch_size: int = Field(default=8, alias="TF_BATCH_SIZE")
    tf_validation_split: float = Field(default=0.2, alias="TF_VALIDATION_SPLIT")
    tf_learning_rate: float = Field(default=0.001, alias="TF_LEARNING_RATE")
    tf_tokenizer_filename: str = Field(default="tokenizer.json", alias="TF_TOKENIZER_FILENAME")
    tf_labels_filename: str = Field(default="labels.json", alias="TF_LABELS_FILENAME")
    tf_metadata_filename: str = Field(
        default="training_metadata.json",
        alias="TF_METADATA_FILENAME",
    )
