"""Evaluación del modelo entrenado."""
from dataclasses import asdict
from typing import Any
import numpy as np
from tensorflow import keras
from asistente_voz.domain.entities.training_metrics import TrainingMetrics
from asistente_voz.infrastructure.ml.tensorflow.nlp.label_encoder import LabelEncoder

class ModelEvaluator:
    """Calcula métricas de rendimiento sobre el conjunto de validación."""

    def evaluate(self, model: keras.Model, features: np.ndarray, labels: np.ndarray, history: keras.callbacks.History) -> TrainingMetrics:
        """Función evaluate."""
        loss, accuracy = model.evaluate(features, labels, verbose=0)
        val_accuracy = float(history.history.get('val_accuracy', [0.0])[-1])
        val_loss = float(history.history.get('val_loss', [0.0])[-1])
        return TrainingMetrics(accuracy=float(accuracy), loss=float(loss), val_accuracy=val_accuracy, val_loss=val_loss, epochs_trained=len(history.history.get('loss', [])), num_samples=int(features.shape[0]), num_classes=int(labels.max()) + 1 if labels.size else 0)

    def classification_report(self, model: keras.Model, features: np.ndarray, labels: np.ndarray, label_encoder: LabelEncoder) -> dict[str, Any]:
        """Función classification report."""
        probabilities = model.predict(features, verbose=0)
        predictions = np.argmax(probabilities, axis=1)
        report: dict[str, Any] = {'per_class': {}, 'confusion': []}
        for index, label in enumerate(label_encoder.labels):
            mask = labels == index
            total = int(mask.sum())
            if total == 0:
                continue
            correct = int((predictions[mask] == index).sum())
            report['per_class'][label] = {'support': total, 'recall': round(correct / total, 4)}
        report['confusion'] = self._build_confusion_matrix(labels, predictions, num_classes=len(label_encoder.labels))
        return report

    @staticmethod
    def _build_confusion_matrix(labels: np.ndarray, predictions: np.ndarray, num_classes: int) -> list[list[int]]:
        """Método interno: build confusion matrix."""
        matrix = np.zeros((num_classes, num_classes), dtype=int)
        for true_label, predicted_label in zip(labels, predictions, strict=True):
            matrix[int(true_label), int(predicted_label)] += 1
        return matrix.tolist()
