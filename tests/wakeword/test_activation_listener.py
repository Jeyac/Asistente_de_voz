"""Pruebas del orquestador de activación."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from asistente_voz.application.services.activation_listener import ActivationListenerService
from asistente_voz.domain.entities.voice_command import VoiceCommand
from asistente_voz.domain.entities.wake_word_activation import WakeWordActivation


def test_activation_then_listen_command() -> None:
    detector = MagicMock()
    detector.wait_for_activation = AsyncMock(
        return_value=WakeWordActivation.now("oye sistema", "mock", 0.9, 120.0),
    )
    detector.release = MagicMock()

    speech = MagicMock()
    speech.listen_command_after_activation = AsyncMock(
        return_value=VoiceCommand(transcript="abre youtube", language="es-ES"),
    )

    settings = MagicMock()
    settings.speech_post_wakeword_pause = 0

    service = ActivationListenerService(detector, speech, settings)

    async def _run() -> None:
        activation = await service.wait_for_wake_word()
        command = await service.listen_command()
        service.release()
        assert activation.keyword == "oye sistema"
        assert command.transcript == "abre youtube"

    asyncio.run(_run())
    detector.wait_for_activation.assert_awaited_once()
    speech.listen_command_after_activation.assert_awaited_once()
    detector.release.assert_called_once()
