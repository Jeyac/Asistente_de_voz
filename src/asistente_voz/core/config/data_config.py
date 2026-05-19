"""Rutas de datos locales y modelos."""

from pathlib import Path

from pydantic import Field, field_validator

from asistente_voz.core.config.base import resolve_project_path


class DataConfig:
    """Rutas de archivos JSON y almacenamiento de modelos."""

    data_dir: Path = Field(default=Path("data"), alias="DATA_DIR")
    intents_dataset_path: Path = Field(
        default=Path("data/intents/intents_dataset.json"),
        alias="INTENTS_DATASET_PATH",
    )
    responses_data_path: Path = Field(
        default=Path("data/responses/responses.json"),
        alias="RESPONSES_DATA_PATH",
    )
    tensorflow_models_dir: Path = Field(
        default=Path("models/tensorflow"),
        alias="TENSORFLOW_MODELS_DIR",
    )
    tf_model_filename: str = Field(
        default="intent_classifier.keras",
        alias="TF_MODEL_FILENAME",
    )

    @field_validator(
        "data_dir",
        "intents_dataset_path",
        "responses_data_path",
        "tensorflow_models_dir",
        mode="before",
    )
    @classmethod
    def _resolve_paths(cls, value: str | Path) -> Path:
        return resolve_project_path(value)

    @property
    def tensorflow_model_path(self) -> Path:
        """Ruta completa al modelo de clasificación de intenciones."""
        return self.tensorflow_models_dir / self.tf_model_filename
