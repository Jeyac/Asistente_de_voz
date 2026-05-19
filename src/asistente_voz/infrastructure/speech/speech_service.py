"""Servicio de reconocimiento de voz con SpeechRecognition."""
import asyncio
import io
import speech_recognition as sr
from asistente_voz.application.interfaces.speech_service import ISpeechService
from asistente_voz.core.config.settings import Settings
from asistente_voz.core.logging.setup import get_logger
from asistente_voz.domain.entities.voice_command import VoiceCommand
from asistente_voz.infrastructure.speech.exception_mapper import SpeechExceptionMapper
logger = get_logger(__name__)

class SpeechRecognitionService(ISpeechService):
    """Adaptador de SpeechRecognition con soporte para español."""

    def __init__(self, settings: Settings) -> None:
        """Inicializa la instancia."""
        self._settings = settings
        self._recognizer = sr.Recognizer()
        self._recognizer.dynamic_energy_threshold = True
        self._mapper = SpeechExceptionMapper()

    @property
    def language(self) -> str:
        """Función language."""
        return self._settings.speech_recognition_language

    async def transcribe_from_audio(self, audio_bytes: bytes) -> VoiceCommand:
        """Convierte bytes WAV en texto."""
        logger.info('Transcribiendo audio | bytes=%s', len(audio_bytes))
        return await asyncio.to_thread(self._transcribe_audio_sync, audio_bytes)

    async def listen_from_microphone(self) -> VoiceCommand:
        """Captura audio del micrófono y lo transcribe."""
        logger.info('Escuchando micrófono | timeout=%ss | phrase_limit=%ss', self._settings.speech_recognition_timeout, self._settings.speech_recognition_phrase_limit)
        return await asyncio.to_thread(self._listen_microphone_sync, timeout=self._settings.speech_recognition_timeout, phrase_limit=self._settings.speech_recognition_phrase_limit, ambient_duration=self._settings.speech_ambient_noise_duration)

    async def listen_command_after_activation(self) -> VoiceCommand:
        """Captura el comando tras wake word (más tiempo y calibración de ruido)."""
        logger.info('Escuchando comando post-activación | timeout=%ss | phrase_limit=%ss | ambient=%ss', self._settings.speech_post_wakeword_timeout, self._settings.speech_post_wakeword_phrase_limit, self._settings.speech_post_wakeword_ambient_duration)
        return await asyncio.to_thread(self._listen_microphone_sync, timeout=self._settings.speech_post_wakeword_timeout, phrase_limit=self._settings.speech_post_wakeword_phrase_limit, ambient_duration=self._settings.speech_post_wakeword_ambient_duration)

    async def transcribe_from_text(self, text: str, language: str | None=None) -> VoiceCommand:
        """Normaliza texto ya proporcionado (sin pasar por audio)."""
        cleaned = text.strip()
        if not cleaned:
            from asistente_voz.domain.exceptions.base import ValidationError
            raise ValidationError(message='El texto del comando no puede estar vacío.')
        return VoiceCommand(transcript=cleaned, language=language or self.language)

    def _transcribe_audio_sync(self, audio_bytes: bytes) -> VoiceCommand:
        """Método interno: transcribe audio sync."""

        def _run() -> VoiceCommand:
            """Método interno: run."""
            with io.BytesIO(audio_bytes) as buffer:
                with sr.AudioFile(buffer) as source:
                    audio = self._recognizer.record(source)
            text = self._recognizer.recognize_google(audio, language=self.language)
            logger.info('Transcripción desde audio completada')
            return VoiceCommand(transcript=text.strip(), language=self.language)
        return self._mapper.wrap(_run)

    def _listen_microphone_sync(self, *, timeout: int, phrase_limit: int, ambient_duration: float) -> VoiceCommand:
        """Método interno: listen microphone sync."""

        def _run() -> VoiceCommand:
            """Método interno: run."""
            with sr.Microphone(sample_rate=16000) as source:
                logger.info('Calibrando ruido ambiente | duration=%.1fs', ambient_duration)
                self._recognizer.adjust_for_ambient_noise(source, duration=ambient_duration)
                logger.info('Habla ahora — escuchando comando...')
                audio = self._recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            text = self._recognizer.recognize_google(audio, language=self.language)
            logger.info('Transcripción desde micrófono completada | text=%s', text[:80])
            return VoiceCommand(transcript=text.strip(), language=self.language)
        return self._mapper.wrap(_run)
