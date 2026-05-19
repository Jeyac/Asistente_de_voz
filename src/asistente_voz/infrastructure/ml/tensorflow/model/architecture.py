"""Arquitectura Keras del clasificador de intenciones."""
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

class IntentClassifierModelFactory:
    """Construye el modelo de clasificación multiclase."""

    def build(self, vocab_size: int, num_classes: int, sequence_length: int, embedding_dim: int) -> keras.Model:
        """Función build."""
        model = keras.Sequential([layers.Input(shape=(sequence_length,), dtype=tf.int32, name='input_tokens'), layers.Embedding(input_dim=vocab_size, output_dim=embedding_dim, mask_zero=True, name='embedding'), layers.GlobalAveragePooling1D(name='global_pool'), layers.Dense(64, activation='relu', name='dense_hidden'), layers.Dropout(0.3, name='dropout'), layers.Dense(num_classes, activation='softmax', name='output_intent')], name='intent_classifier')
        return model
