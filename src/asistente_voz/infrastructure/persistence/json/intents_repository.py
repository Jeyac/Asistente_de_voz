"""Repositorio del dataset de intenciones."""
from asistente_voz.domain.entities.intent_definition import IntentDefinition
from asistente_voz.domain.exceptions.base import ValidationError
from asistente_voz.infrastructure.persistence.json.base_repository import JsonFileRepository

class IntentsRepository:
    """Carga intenciones y ejemplos desde el dataset JSON."""

    def __init__(self, json_repository: JsonFileRepository) -> None:
        """Inicializa la instancia."""
        self._json = json_repository

    def load_definitions(self) -> list[IntentDefinition]:
        """Función load definitions."""
        payload = self._json.read()
        raw_intents = payload.get('intents')
        if not isinstance(raw_intents, list) or not raw_intents:
            raise ValidationError(message='El dataset debe incluir al menos una intención.')
        definitions: list[IntentDefinition] = []
        for item in raw_intents:
            if not isinstance(item, dict):
                raise ValidationError(message='Cada intención debe ser un objeto JSON.')
            name = item.get('name')
            examples = item.get('examples')
            if not isinstance(name, str) or not name.strip():
                raise ValidationError(message='Cada intención requiere un nombre válido.')
            if not isinstance(examples, list) or not examples:
                raise ValidationError(message=f"La intención '{name}' requiere ejemplos.")
            cleaned_examples = tuple((str(example).strip() for example in examples if str(example).strip()))
            if not cleaned_examples:
                raise ValidationError(message=f"La intención '{name}' no tiene ejemplos válidos.")
            definitions.append(IntentDefinition(name=name.strip(), examples=cleaned_examples))
        return definitions

    def load_training_pairs(self) -> tuple[list[str], list[str]]:
        """Expande el dataset a pares (texto, etiqueta)."""
        texts: list[str] = []
        labels: list[str] = []
        for definition in self.load_definitions():
            texts.extend(definition.examples)
            labels.extend([definition.name] * len(definition.examples))
        return (texts, labels)
