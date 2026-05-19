"""Inyección de dependencias para la capa API."""

from typing import Annotated

from fastapi import Depends, Request

from asistente_voz.application.factories.ml_factory import MlFactory
from asistente_voz.application.factories.response_factory import ResponseFactory
from asistente_voz.application.factories.voice_factory import VoiceFactory
from asistente_voz.application.factories.wakeword_factory import WakeWordFactory
from asistente_voz.application.services.wakeword_chunk_scorer import WakeWordChunkScorer
from asistente_voz.application.use_cases.activate_and_listen import ActivateAndListenUseCase
from asistente_voz.application.services.model_registry import get_model_registry
from asistente_voz.application.use_cases.classify_intent import ClassifyIntentUseCase
from asistente_voz.application.use_cases.generate_smart_response import GenerateSmartResponseUseCase
from asistente_voz.application.use_cases.process_voice_command import ProcessVoiceCommandUseCase
from asistente_voz.application.use_cases.respond_to_intent import RespondToIntentUseCase
from asistente_voz.core.config.settings import Settings, get_settings
from asistente_voz.infrastructure.responses.response_service import SmartResponseService
from asistente_voz.infrastructure.speech.audio_validator import AudioValidator

SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_request_id(request: Request) -> str:
    """Obtiene el identificador de correlación de la petición."""
    return getattr(request.state, "request_id", "unknown")


RequestIdDep = Annotated[str, Depends(get_request_id)]


def get_ml_factory(settings: SettingsDep) -> MlFactory:
    return MlFactory(settings, get_model_registry())


MlFactoryDep = Annotated[MlFactory, Depends(get_ml_factory)]


def get_response_factory(settings: SettingsDep) -> ResponseFactory:
    return ResponseFactory(settings)


ResponseFactoryDep = Annotated[ResponseFactory, Depends(get_response_factory)]


def get_voice_factory(
    settings: SettingsDep,
    ml_factory: MlFactoryDep,
) -> VoiceFactory:
    return VoiceFactory(settings, ml_factory)


VoiceFactoryDep = Annotated[VoiceFactory, Depends(get_voice_factory)]


def get_classify_intent_use_case(factory: MlFactoryDep) -> ClassifyIntentUseCase:
    return factory.create_classify_use_case()


ClassifyIntentUseCaseDep = Annotated[ClassifyIntentUseCase, Depends(get_classify_intent_use_case)]


def get_response_service(factory: ResponseFactoryDep) -> SmartResponseService:
    return factory.create_response_service()


ResponseServiceDep = Annotated[SmartResponseService, Depends(get_response_service)]


def get_generate_smart_response_use_case(
    factory: ResponseFactoryDep,
) -> GenerateSmartResponseUseCase:
    return factory.create_generate_smart_response_use_case()


GenerateSmartResponseUseCaseDep = Annotated[
    GenerateSmartResponseUseCase,
    Depends(get_generate_smart_response_use_case),
]


def get_respond_to_intent_use_case(
    ml_factory: MlFactoryDep,
    response_factory: ResponseFactoryDep,
) -> RespondToIntentUseCase:
    return response_factory.create_respond_to_intent_use_case(
        ml_factory.create_classify_use_case(),
    )


RespondToIntentUseCaseDep = Annotated[RespondToIntentUseCase, Depends(get_respond_to_intent_use_case)]


def get_process_voice_use_case(voice_factory: VoiceFactoryDep) -> ProcessVoiceCommandUseCase:
    return voice_factory.create_process_voice_use_case()


ProcessVoiceUseCaseDep = Annotated[ProcessVoiceCommandUseCase, Depends(get_process_voice_use_case)]


def get_audio_validator(voice_factory: VoiceFactoryDep) -> AudioValidator:
    return voice_factory.create_audio_validator()


AudioValidatorDep = Annotated[AudioValidator, Depends(get_audio_validator)]


def get_wakeword_factory(
    settings: SettingsDep,
    voice_factory: VoiceFactoryDep,
) -> WakeWordFactory:
    return WakeWordFactory(settings, voice_factory)


WakeWordFactoryDep = Annotated[WakeWordFactory, Depends(get_wakeword_factory)]


def get_activate_and_listen_use_case(
    factory: WakeWordFactoryDep,
) -> ActivateAndListenUseCase:
    return factory.create_activate_and_listen_use_case()


ActivateAndListenUseCaseDep = Annotated[
    ActivateAndListenUseCase,
    Depends(get_activate_and_listen_use_case),
]


_wakeword_chunk_scorer: WakeWordChunkScorer | None = None


def get_wakeword_chunk_scorer(settings: SettingsDep) -> WakeWordChunkScorer:
    """Singleton: conserva sesiones y evita recargar ONNX en cada fragmento."""
    global _wakeword_chunk_scorer
    if _wakeword_chunk_scorer is None:
        _wakeword_chunk_scorer = WakeWordChunkScorer(settings)
    return _wakeword_chunk_scorer


WakeWordChunkScorerDep = Annotated[WakeWordChunkScorer, Depends(get_wakeword_chunk_scorer)]
