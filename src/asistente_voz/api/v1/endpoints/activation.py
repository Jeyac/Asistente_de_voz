"""Endpoints de activación por palabra clave."""

import asyncio

from fastapi import APIRouter, Header, Request, status

from asistente_voz.api.dependencies import (
    ActivateAndListenUseCaseDep,
    SettingsDep,
    WakeWordChunkScorerDep,
)
from asistente_voz.application.use_cases.activate_and_listen import ActivationListenResult
from asistente_voz.core.logging.setup import get_logger
from asistente_voz.domain.entities.voice_process_result import VoiceProcessResult
from asistente_voz.schemas.activation import (
    ActivationConfigResponse,
    ActivationListenRequest,
    ActivationListenResponse,
    WakeWordActivationSchema,
    WakeWordChunkScoreResponse,
)
from asistente_voz.schemas.voice import VoiceProcessResponse

router = APIRouter()
logger = get_logger(__name__)


def _voice_response(result: VoiceProcessResult) -> VoiceProcessResponse:
    return VoiceProcessResponse(
        transcript=result.transcript,
        language=result.language,
        intent=result.intent,
        confidence=round(result.confidence, 4),
        above_threshold=result.above_threshold,
        cleaned_text=result.cleaned_text,
        response=result.response,
        probabilities={k: round(v, 4) for k, v in result.probabilities.items()},
        action_performed=result.action_performed,
        action_url=result.action_url,
    )


def _activation_response(payload: ActivationListenResult) -> ActivationListenResponse:
    activation = payload.activation
    return ActivationListenResponse(
        activation=WakeWordActivationSchema(
            keyword=activation.keyword,
            engine=activation.engine,
            confidence=round(activation.confidence, 4),
            detected_at=activation.detected_at,
            latency_ms=activation.latency_ms,
        ),
        result=_voice_response(payload.voice_result),
    )


@router.get(
    "/config",
    response_model=ActivationConfigResponse,
    summary="Configuración de palabra clave",
)
async def activation_config(settings: SettingsDep) -> ActivationConfigResponse:
    return ActivationConfigResponse(
        enabled=settings.wakeword_enabled,
        phrase=settings.wakeword_phrase,
        engine=settings.wakeword_engine,
        threshold=settings.wakeword_threshold,
        listen_timeout=settings.wakeword_listen_timeout,
    )


@router.post(
    "/score-chunk",
    response_model=WakeWordChunkScoreResponse,
    summary="Puntuar fragmento de audio (micrófono del navegador)",
    description=(
        "Recibe PCM int16 mono 16 kHz (1280 muestras, 2560 bytes). "
        "Requiere cabecera X-Wake-Session para mantener el estado del modelo. "
        "Funciona en producción (Render): el micrófono está en el cliente."
    ),
)
async def score_wake_chunk(
    request: Request,
    scorer: WakeWordChunkScorerDep,
    x_wake_session: str | None = Header(default=None, alias="X-Wake-Session"),
) -> WakeWordChunkScoreResponse:
    from asistente_voz.domain.exceptions.base import ValidationError

    if not x_wake_session:
        raise ValidationError(message="Falta la cabecera X-Wake-Session.")
    body = await request.body()
    result = await asyncio.to_thread(scorer.score_chunk, x_wake_session, body)
    safe_score = max(0.0, float(result.score))
    return WakeWordChunkScoreResponse(
        score=round(safe_score, 4),
        activated=result.activated,
        phrase=result.phrase,
        threshold=result.threshold,
    )


@router.post(
    "/score-chunks",
    response_model=WakeWordChunkScoreResponse,
    summary="Puntuar varios fragmentos PCM en una petición",
    description=(
        "PCM int16 mono 16 kHz concatenado (múltiplos de 2560 bytes). "
        "Reduce latencia de red frente a /score-chunk repetido."
    ),
)
async def score_wake_chunks(
    request: Request,
    scorer: WakeWordChunkScorerDep,
    x_wake_session: str | None = Header(default=None, alias="X-Wake-Session"),
) -> WakeWordChunkScoreResponse:
    from asistente_voz.domain.exceptions.base import ValidationError

    if not x_wake_session:
        raise ValidationError(message="Falta la cabecera X-Wake-Session.")
    body = await request.body()
    result = await asyncio.to_thread(scorer.score_chunks, x_wake_session, body)
    safe_score = max(0.0, float(result.score))
    return WakeWordChunkScoreResponse(
        score=round(safe_score, 4),
        activated=result.activated,
        phrase=result.phrase,
        threshold=result.threshold,
    )


@router.delete(
    "/session",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cerrar sesión de escucha wake word",
)
async def end_wake_session(
    scorer: WakeWordChunkScorerDep,
    x_wake_session: str | None = Header(default=None, alias="X-Wake-Session"),
) -> None:
    from asistente_voz.domain.exceptions.base import ValidationError

    if not x_wake_session:
        raise ValidationError(message="Falta la cabecera X-Wake-Session.")
    await asyncio.to_thread(scorer.end_session, x_wake_session)


@router.post(
    "/listen",
    response_model=ActivationListenResponse,
    status_code=status.HTTP_200_OK,
    summary="Activar con 'oye sistema' y procesar comando",
    description=(
        "Fase 1: detecta la palabra clave. Fase 2: escucha el comando con SpeechRecognition. "
        "Fase 3: clasifica con TensorFlow y responde. Solo disponible en entorno local."
    ),
)
async def activate_and_listen(
    use_case: ActivateAndListenUseCaseDep,
    settings: SettingsDep,
    payload: ActivationListenRequest | None = None,
) -> ActivationListenResponse:
    if settings.is_production:
        from asistente_voz.domain.exceptions.base import ValidationError

        raise ValidationError(
            message="La activación por micrófono no está disponible en producción.",
            details={"hint": "Use /voice/process o /voice/process-audio."},
        )
    timeout = payload.wakeword_timeout if payload else None
    logger.info("Iniciando flujo de activación | phrase='%s'", settings.wakeword_phrase)
    result = await use_case.execute(wakeword_timeout=timeout)
    return _activation_response(result)
