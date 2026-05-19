"""Carga y validación del catálogo de respuestas JSON."""
from typing import Any
from asistente_voz.domain.entities.intent_responses import IntentResponses, ResponseCatalog
from asistente_voz.domain.exceptions.base import ValidationError
from asistente_voz.infrastructure.persistence.json.base_repository import JsonFileRepository

class ResponseLoader:
    """Parsea el JSON de respuestas soportando formatos simple y extendido."""

    def __init__(self, json_repository: JsonFileRepository) -> None:
        """Inicializa la instancia."""
        self._json = json_repository

    def load(self) -> ResponseCatalog:
        """Carga datos o artefactos desde disco."""
        payload = self._json.read()
        version = str(payload.get('version', '1.0.0'))
        default_intent = str(payload.get('default_intent', 'desconocido'))
        raw_responses = payload.get('responses')
        if not isinstance(raw_responses, dict) or not raw_responses:
            raise ValidationError(message='El catálogo debe incluir respuestas por intención.')
        intents: list[IntentResponses] = []
        for intent_name, intent_payload in raw_responses.items():
            intents.append(self._parse_intent(str(intent_name), intent_payload))
        return ResponseCatalog(version=version, default_intent=default_intent, intents=tuple(intents))

    def _parse_intent(self, intent_name: str, payload: Any) -> IntentResponses:
        """Método interno: parse intent."""
        if isinstance(payload, list):
            variants = tuple((str(item).strip() for item in payload if str(item).strip()))
            return IntentResponses(intent=intent_name, variants=variants, enabled=True)
        if isinstance(payload, dict):
            raw_variants = payload.get('variants', payload.get('responses', []))
            enabled = bool(payload.get('enabled', True))
            if not isinstance(raw_variants, list):
                raise ValidationError(message=f"Formato inválido para la intención '{intent_name}'.")
            variants = tuple((str(item).strip() for item in raw_variants if str(item).strip()))
            return IntentResponses(intent=intent_name, variants=variants, enabled=enabled)
        raise ValidationError(message=f"La intención '{intent_name}' debe ser una lista o un objeto con variantes.")
