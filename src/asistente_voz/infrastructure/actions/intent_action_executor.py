"""Ejecutor de acciones: resuelve URLs para el cliente (local y Render)."""

import re
import urllib.parse

from asistente_voz.application.interfaces.intent_action_executor import IIntentActionExecutor
from asistente_voz.core.config.settings import Settings
from asistente_voz.core.logging.setup import get_logger
from asistente_voz.domain.entities.intent_action import IntentActionResult

logger = get_logger(__name__)

_SEARCH_PREFIXES = (
    "busca en internet",
    "buscar en internet",
    "busca en la web",
    "buscar en la web",
    "búscame información sobre",
    "búscame información de",
    "búscame información",
    "busca información sobre",
    "busca información de",
    "busca información",
    "haz una búsqueda web de",
    "haz una búsqueda web sobre",
    "haz una búsqueda web",
    "busca esto en internet",
    "busca en la red",
    "busca online",
    "investiga en internet sobre",
    "investiga en internet",
    "investiga en la web",
    "búscalo online",
    "busca en google",
    "googlea",
    "busca",
)

# Intenciones informativas (sin URL)
_INFO_INTENTS = frozenset({"creador", "relacion_creador", "saludo", "despedida", "hora"})

# Temas: si el usuario añade detalle ("noticias de fútbol"), se busca en Google
_SEARCHABLE_TOPIC_INTENTS = frozenset({
    "buscar_web",
    "deportes",
    "noticias",
    "historia",
    "tecnologia",
    "ciencia",
    "cultura",
    "entretenimiento",
    "salud",
    "viajes",
})


class IntentActionExecutor(IIntentActionExecutor):
    """
    Devuelve URLs para que el navegador del usuario las abra.
    Funciona en local y en Render (el frontend ejecuta window.open).
    """

    _URL_BY_INTENT: dict[str, str] = {
        "abrir_youtube": "https://www.youtube.com",
        "abrir_google": "https://www.google.com",
        "musica": "https://music.youtube.com",
        "clima": "https://www.google.com/search?q=clima+tiempo+hoy",
        "deportes": "https://www.google.com/search?q=noticias+deportes+hoy",
        "noticias": "https://news.google.com",
        "historia": "https://www.google.com/search?q=historia+mundo+actualidad",
        "tecnologia": "https://www.google.com/search?q=noticias+tecnologia",
        "ciencia": "https://www.google.com/search?q=noticias+ciencia",
        "cultura": "https://www.google.com/search?q=cultura+arte+actualidad",
        "entretenimiento": "https://www.youtube.com/feed/trending",
        "salud": "https://www.google.com/search?q=salud+bienestar+consejos",
        "viajes": "https://www.google.com/search?q=viajes+destinos+turismo",
    }

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def execute(self, intent: str, transcript: str) -> IntentActionResult | None:
        if intent in _INFO_INTENTS:
            return None

        url = self._resolve_url(intent, transcript)
        if not url:
            return None

        if not self._settings.enable_system_actions:
            return IntentActionResult(
                performed=False,
                url=None,
                detail="Acciones deshabilitadas.",
            )

        logger.info("Acción delegada al cliente | intent=%s | url=%s", intent, url)
        return IntentActionResult(
            performed=True,
            url=url,
            detail="El cliente abrirá la URL en el navegador.",
        )

    def _resolve_url(self, intent: str, transcript: str) -> str | None:
        if intent in _SEARCHABLE_TOPIC_INTENTS:
            query = self._extract_search_query(transcript)
            if query:
                encoded = urllib.parse.quote_plus(query)
                return f"https://www.google.com/search?q={encoded}"
        if intent == "buscar_web":
            return "https://www.google.com"
        return self._URL_BY_INTENT.get(intent)

    @staticmethod
    def _extract_search_query(transcript: str) -> str:
        text = transcript.lower().strip()
        for prefix in sorted(_SEARCH_PREFIXES, key=len, reverse=True):
            if text.startswith(prefix):
                text = text[len(prefix) :].strip()
                break
        text = re.sub(r"^(sobre|de|acerca de|en)\s+", "", text).strip()
        return text
