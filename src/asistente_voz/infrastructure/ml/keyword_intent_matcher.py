"""Clasificación por frases del dataset cuando el modelo TF no incluye intenciones nuevas."""
from __future__ import annotations
import re
import unicodedata
from asistente_voz.domain.entities.intent_definition import IntentDefinition
_MIN_PHRASE_LEN = 4

def _normalize(text: str) -> str:
    """Método interno: normalize."""
    lowered = text.lower().strip()
    normalized = unicodedata.normalize('NFD', lowered)
    return ''.join((char for char in normalized if unicodedata.category(char) != 'Mn'))

class KeywordIntentMatcher:
    """Empareja el texto del usuario con ejemplos del dataset JSON."""

    def __init__(self, definitions: list[IntentDefinition]) -> None:
        """Inicializa la instancia."""
        self._phrases: list[tuple[str, str]] = []
        for definition in definitions:
            for example in definition.examples:
                phrase = _normalize(example)
                if len(phrase) >= _MIN_PHRASE_LEN:
                    self._phrases.append((phrase, definition.name))
        self._phrases.sort(key=lambda item: len(item[0]), reverse=True)

    def match(self, text: str) -> tuple[str, float] | None:
        """Función match."""
        normalized = _normalize(text)
        if not normalized:
            return None
        for phrase, intent in self._phrases:
            if phrase in normalized or normalized in phrase:
                ratio = min(len(phrase), len(normalized)) / max(len(phrase), len(normalized))
                return (intent, round(0.86 + 0.12 * ratio, 4))
        return self._match_by_tokens(normalized)

    def _match_by_tokens(self, normalized: str) -> tuple[str, float] | None:
        """Método interno: match by tokens."""
        words = {w for w in re.split('\\W+', normalized) if len(w) >= 3}
        if not words:
            return None
        best_intent: str | None = None
        best_score = 0.0
        by_intent: dict[str, set[str]] = {}
        for phrase, intent in self._phrases:
            phrase_words = {w for w in re.split('\\W+', phrase) if len(w) >= 3}
            if not phrase_words:
                continue
            by_intent.setdefault(intent, set()).update(phrase_words)
        for intent, intent_words in by_intent.items():
            overlap = len(words & intent_words)
            if overlap == 0:
                continue
            score = overlap / max(len(words), 1)
            if score > best_score:
                best_score = score
                best_intent = intent
        if best_intent and best_score >= 0.35:
            return (best_intent, round(0.78 + 0.2 * best_score, 4))
        return None
