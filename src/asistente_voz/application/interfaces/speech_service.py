"""Contrato para reconocimiento y transcripción de voz."""

from abc import ABC, abstractmethod

from asistente_voz.domain.entities.voice_command import VoiceCommand


class ISpeechService(ABC):
    """Puerto de entrada/salida de audio y texto."""

    @abstractmethod
    async def transcribe_from_audio(self, audio_bytes: bytes) -> VoiceCommand:
        """Convierte audio en texto transcrito."""

    @abstractmethod
    async def transcribe_from_text(self, text: str, language: str | None = None) -> VoiceCommand:
        """Normaliza texto ya transcrito como comando de voz."""

    @abstractmethod
    async def listen_from_microphone(self) -> VoiceCommand:
        """Captura audio desde el micrófono y devuelve la transcripción."""

    async def listen_command_after_activation(self) -> VoiceCommand:
        """Escucha el comando tras detectar la palabra clave (calibración ampliada)."""
        return await self.listen_from_microphone()
