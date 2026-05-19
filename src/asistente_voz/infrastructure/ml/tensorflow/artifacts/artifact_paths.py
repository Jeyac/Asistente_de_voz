"""Rutas de artefactos del modelo TensorFlow."""
from dataclasses import dataclass
from pathlib import Path
from asistente_voz.core.config.settings import Settings

@dataclass(frozen=True, slots=True)
class ArtifactPaths:
    """Ubicaciones de modelo, tokenizer y metadatos."""
    models_dir: Path
    model_file: Path
    tokenizer_file: Path
    labels_file: Path
    metadata_file: Path

    @classmethod
    def from_settings(cls, settings: Settings) -> 'ArtifactPaths':
        """Función from settings."""
        models_dir = settings.tensorflow_models_dir
        return cls(models_dir=models_dir, model_file=settings.tensorflow_model_path, tokenizer_file=models_dir / settings.tf_tokenizer_filename, labels_file=models_dir / settings.tf_labels_filename, metadata_file=models_dir / settings.tf_metadata_filename)

    def all_exist(self) -> bool:
        """Función all exist."""
        return all((path.is_file() for path in (self.model_file, self.tokenizer_file, self.labels_file, self.metadata_file)))
