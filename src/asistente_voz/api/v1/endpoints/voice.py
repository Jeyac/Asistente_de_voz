"""Endpoints REST de reconocimiento y procesamiento de voz."""
from fastapi import APIRouter, File, UploadFile, status
from asistente_voz.api.dependencies import AudioValidatorDep, ProcessVoiceUseCaseDep, SettingsDep
from asistente_voz.core.logging.setup import get_logger
from asistente_voz.domain.entities.voice_process_result import VoiceProcessResult
from asistente_voz.schemas.voice import VoiceProcessResponse, VoiceTextRequest, VoiceTranscribeResponse
router = APIRouter()
logger = get_logger(__name__)

def _to_process_response(result: VoiceProcessResult) -> VoiceProcessResponse:
    """Convierte entidad de dominio a DTO REST."""
    return VoiceProcessResponse(transcript=result.transcript, language=result.language, intent=result.intent, confidence=round(result.confidence, 4), above_threshold=result.above_threshold, cleaned_text=result.cleaned_text, response=result.response, probabilities={key: round(value, 4) for key, value in result.probabilities.items()}, action_performed=result.action_performed, action_url=result.action_url)

@router.post('/process', response_model=VoiceProcessResponse, status_code=status.HTTP_200_OK, summary='Procesar texto de voz', description='Clasifica la intención y genera respuesta a partir de texto transcrito.')
async def process_voice_text(payload: VoiceTextRequest, use_case: ProcessVoiceUseCaseDep) -> VoiceProcessResponse:
    """Función process voice text."""
    logger.info('Procesando comando de voz desde texto')
    result = await use_case.execute_from_text(payload.text)
    return _to_process_response(result)

@router.post('/transcribe', response_model=VoiceTranscribeResponse, status_code=status.HTTP_200_OK, summary='Transcribir archivo de audio', description='Convierte un archivo WAV a texto en español.')
async def transcribe_audio(use_case: ProcessVoiceUseCaseDep, validator: AudioValidatorDep, audio: UploadFile=File(..., description='Archivo WAV con el comando de voz')) -> VoiceTranscribeResponse:
    """Función transcribe audio."""
    content = await audio.read()
    validator.validate_upload(audio.filename, audio.content_type, content)
    logger.info('Transcribiendo archivo | filename=%s | size=%s', audio.filename, len(content))
    command = await use_case.transcribe_only(content)
    return VoiceTranscribeResponse(transcript=command.transcript, language=command.language)

@router.post('/process-audio', response_model=VoiceProcessResponse, status_code=status.HTTP_200_OK, summary='Procesar archivo de audio', description='Transcribe audio, clasifica intención con TensorFlow y devuelve respuesta.')
async def process_voice_audio(use_case: ProcessVoiceUseCaseDep, validator: AudioValidatorDep, audio: UploadFile=File(..., description='Archivo WAV con el comando de voz')) -> VoiceProcessResponse:
    """Función process voice audio."""
    content = await audio.read()
    validator.validate_upload(audio.filename, audio.content_type, content)
    logger.info('Procesando audio completo | filename=%s | size=%s', audio.filename, len(content))
    result = await use_case.execute_from_audio(content)
    return _to_process_response(result)

@router.post('/listen', response_model=VoiceProcessResponse, status_code=status.HTTP_200_OK, summary='Escuchar micrófono y procesar', description='Captura audio desde el micrófono local, transcribe y clasifica la intención. Requiere entorno con dispositivo de audio (no disponible en Render).')
async def listen_and_process(use_case: ProcessVoiceUseCaseDep, settings: SettingsDep) -> VoiceProcessResponse:
    """Función listen and process."""
    if settings.is_production:
        from asistente_voz.domain.exceptions.base import ValidationError
        raise ValidationError(message='La captura por micrófono no está habilitada en producción.', details={'hint': 'Use /voice/process-audio con un archivo WAV.'})
    logger.info('Escuchando micrófono para procesamiento completo')
    result = await use_case.execute_from_microphone()
    return _to_process_response(result)
