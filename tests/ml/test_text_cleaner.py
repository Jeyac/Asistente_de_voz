"""Pruebas del limpiador de texto."""

from asistente_voz.infrastructure.ml.tensorflow.nlp.text_cleaner import TextCleaner


def test_clean_lowercase_and_strip_accents() -> None:
    cleaner = TextCleaner()
    assert cleaner.clean("  ¡Hola, Qué TAL!  ") == "hola que tal"


def test_clean_removes_special_characters() -> None:
    cleaner = TextCleaner()
    assert cleaner.clean("abre @youtube!!!") == "abre youtube"
