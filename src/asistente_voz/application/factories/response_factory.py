"""Factory del sistema de respuestas inteligentes."""
from asistente_voz.application.interfaces.response_provider import IResponseProvider
from asistente_voz.application.interfaces.response_selector import IResponseSelector
from asistente_voz.application.use_cases.generate_smart_response import GenerateSmartResponseUseCase
from asistente_voz.application.use_cases.get_dynamic_response import GetDynamicResponseUseCase
from asistente_voz.application.use_cases.respond_to_intent import RespondToIntentUseCase
from asistente_voz.core.config.settings import Settings
from asistente_voz.infrastructure.persistence.json.base_repository import JsonFileRepository
from asistente_voz.infrastructure.responses.response_loader import ResponseLoader
from asistente_voz.infrastructure.responses.response_selector import RandomResponseSelector
from asistente_voz.infrastructure.responses.response_service import SmartResponseService

class ResponseFactory:
    """Construye dependencias del catálogo de respuestas."""

    def __init__(self, settings: Settings) -> None:
        """Inicializa la instancia."""
        self._settings = settings
        self._service: SmartResponseService | None = None

    def create_selector(self) -> IResponseSelector:
        """Función create selector."""
        return RandomResponseSelector()

    def create_loader(self) -> ResponseLoader:
        """Función create loader."""
        json_repo = JsonFileRepository(self._settings.responses_data_path)
        return ResponseLoader(json_repo)

    def create_response_service(self) -> SmartResponseService:
        """Función create response service."""
        if self._service is None:
            self._service = SmartResponseService(loader=self.create_loader(), selector=self.create_selector(), settings=self._settings)
        return self._service

    def create_response_provider(self) -> IResponseProvider:
        """Función create response provider."""
        return self.create_response_service()

    def create_get_response_use_case(self) -> GetDynamicResponseUseCase:
        """Función create get response use case."""
        return GetDynamicResponseUseCase(self.create_response_provider())

    def create_generate_smart_response_use_case(self) -> GenerateSmartResponseUseCase:
        """Función create generate smart response use case."""
        return GenerateSmartResponseUseCase(self.create_response_provider())

    def create_respond_to_intent_use_case(self, classify_intent_use_case) -> RespondToIntentUseCase:
        """Función create respond to intent use case."""
        return RespondToIntentUseCase(classify_intent=classify_intent_use_case, response_provider=self.create_response_provider())
