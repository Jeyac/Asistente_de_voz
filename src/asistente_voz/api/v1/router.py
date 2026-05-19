"""Agregador de routers v1."""

from fastapi import APIRouter

from asistente_voz.api.v1.endpoints import activation, health, intents, responses, root, voice

v1_router = APIRouter()
v1_router.include_router(root.router, tags=["Root"])
v1_router.include_router(health.router, tags=["Health"])
v1_router.include_router(intents.router, prefix="/intents", tags=["Intents"])
v1_router.include_router(responses.router, prefix="/responses", tags=["Responses"])
v1_router.include_router(activation.router, prefix="/activation", tags=["Activation"])
v1_router.include_router(voice.router, prefix="/voice", tags=["Voice"])
