"""Vectorización de texto con TextVectorization de Keras."""

import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import TextVectorization


class TextVectorizer:
    """Tokeniza, vectoriza y persiste el vocabulario del modelo."""

    def __init__(
        self,
        max_tokens: int,
        sequence_length: int,
    ) -> None:
        self._max_tokens = max_tokens
        self._sequence_length = sequence_length
        self._layer = TextVectorization(
            max_tokens=max_tokens,
            output_mode="int",
            output_sequence_length=sequence_length,
        )
        self._is_adapted = False

    @property
    def vocab_size(self) -> int:
        return min(self._max_tokens, len(self.get_vocabulary()))

    def get_vocabulary(self) -> list[str]:
        return self._layer.get_vocabulary()

    def adapt(self, texts: list[str]) -> None:
        self._layer.adapt(texts)
        self._is_adapted = True

    def transform(self, texts: list[str]) -> np.ndarray:
        if not self._is_adapted:
            raise RuntimeError("El vectorizador debe adaptarse antes de transformar.")
        return self._layer(np.array(texts)).numpy()

    def transform_one(self, text: str) -> np.ndarray:
        return self.transform([text])[0]

    def save(self, path: Path) -> None:
        payload = {
            "max_tokens": self._max_tokens,
            "sequence_length": self._sequence_length,
            "vocabulary": self.get_vocabulary(),
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "TextVectorizer":
        payload = json.loads(path.read_text(encoding="utf-8"))
        vectorizer = cls(
            max_tokens=int(payload["max_tokens"]),
            sequence_length=int(payload["sequence_length"]),
        )
        vectorizer._layer.set_vocabulary(payload["vocabulary"])
        vectorizer._is_adapted = True
        return vectorizer
