"""Métricas de evaluación del clasificador."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TrainingMetrics:
    """Resultados agregados del entrenamiento."""

    accuracy: float
    loss: float
    val_accuracy: float
    val_loss: float
    epochs_trained: int
    num_samples: int
    num_classes: int
