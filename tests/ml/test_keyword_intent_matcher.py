"""Pruebas del matcher por palabras clave."""

from asistente_voz.domain.entities.intent_definition import IntentDefinition
from asistente_voz.infrastructure.ml.keyword_intent_matcher import KeywordIntentMatcher


def _matcher() -> KeywordIntentMatcher:
    definitions = [
        IntentDefinition(name="deportes", examples=("noticias de deportes", "fútbol hoy")),
        IntentDefinition(name="noticias", examples=("últimas noticias", "noticias de hoy")),
        IntentDefinition(name="historia", examples=("historia del mundo",)),
    ]
    return KeywordIntentMatcher(definitions)


def test_match_deportes() -> None:
    result = _matcher().match("quiero noticias de deportes")
    assert result is not None
    assert result[0] == "deportes"


def test_match_noticias() -> None:
    result = _matcher().match("dime las últimas noticias")
    assert result is not None
    assert result[0] == "noticias"
