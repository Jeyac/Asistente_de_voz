"""Limpieza y normalización de texto para NLP."""

import re
import unicodedata


class TextCleaner:
    """Normaliza texto de entrada antes de tokenizar."""

    _NON_ALPHANUMERIC = re.compile(r"[^a-z0-9áéíóúüñ\s]")
    _WHITESPACE = re.compile(r"\s+")

    def clean(self, text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text.lower().strip())
        without_accents = "".join(
            char for char in normalized if not unicodedata.combining(char)
        )
        cleaned = self._NON_ALPHANUMERIC.sub(" ", without_accents)
        return self._WHITESPACE.sub(" ", cleaned).strip()
