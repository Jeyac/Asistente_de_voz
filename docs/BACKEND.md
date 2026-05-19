# Referencia del backend (`src/asistente_voz/`)

Documentación módulo a módulo del código Python. El backend sigue **Clean Architecture**: el dominio no importa FastAPI ni TensorFlow.

---

## Punto de entrada

| Archivo | Función |
|---------|---------|
| `main.py` | Crea `app` con `create_app(settings)`; `run()` arranca uvicorn en desarrollo |
| `core/app_factory.py` | Registra lifespan, middleware, routers y manejadores de error |
| `core/bootstrap/app_routes.py` | Monta `/api/v1` y rutas raíz |

---

## Capa API (`api/`)

### `api/router.py` y `api/v1/router.py`

Agregan routers bajo el prefijo `API_PREFIX` (default `/api/v1`):

| Prefijo | Módulo | Tag |
|---------|--------|-----|
| `/` | `endpoints/root.py` | Root |
| `/health` | `endpoints/health.py` | Health |
| `/intents` | `endpoints/intents.py` | Intents |
| `/responses` | `endpoints/responses.py` | Responses |
| `/activation` | `endpoints/activation.py` | Activation |
| `/voice` | `endpoints/voice.py` | Voice |

### `api/dependencies.py`

Inyección de dependencias FastAPI (`Depends`):

| Dependencia | Proporciona |
|-------------|-------------|
| `SettingsDep` | `Settings` (singleton cacheado) |
| `MlFactoryDep` | Factory ML + `ModelRegistry` |
| `VoiceFactoryDep` | Factory voz + ML |
| `ProcessVoiceCommandUseCaseDep` | Caso de uso principal de voz |
| `WakeWordChunkScorerDep` | Singleton scorer wake word por sesión |
| `ActivateAndListenUseCaseDep` | Flujo micrófono servidor (solo local) |

### Endpoints (`api/v1/endpoints/`)

#### `health.py`

- `GET /health` — Estado del servicio para Render/Docker.

#### `root.py`

- `GET /` — Metadatos del API (nombre, versión, enlaces).

#### `intents.py`

- `POST /intents/predict` — Clasifica texto → intención + probabilidades.
- `GET /intents/model/status` — Si el modelo TensorFlow está cargado.

#### `responses.py`

- `POST /responses/generate` — Clasificar + respuesta aleatoria.
- `GET /responses/catalog` — Lista de intenciones con respuestas.
- `GET /responses/{intent}` — Una respuesta aleatoria para la intención.

#### `voice.py`

| Ruta | Descripción | Producción |
|------|-------------|:----------:|
| `POST /voice/process` | Texto → transcripción simulada → ML → respuesta | Sí |
| `POST /voice/transcribe` | WAV → solo texto | Sí |
| `POST /voice/process-audio` | WAV → flujo completo + `action_url` | Sí |
| `POST /voice/listen` | Micrófono servidor (PyAudio) | No |

#### `activation.py`

| Ruta | Descripción |
|------|-------------|
| `GET /activation/config` | `enabled`, `phrase`, `engine`, `threshold` |
| `POST /activation/score-chunk` | Un fragmento PCM (2560 bytes) |
| `POST /activation/score-chunks` | Varios fragmentos concatenados (menos latencia) |
| `DELETE /activation/session` | Libera detector de la sesión `X-Wake-Session` |
| `POST /activation/listen` | Wake word + comando en servidor (**bloqueado en producción**) |

---

## Esquemas Pydantic (`schemas/`)

DTOs de entrada/salida HTTP (no son entidades de dominio):

| Archivo | Modelos principales |
|---------|---------------------|
| `voice.py` | `VoiceProcessRequest`, `VoiceProcessResponse` |
| `intent.py` | `IntentPredictRequest`, `IntentPredictResponse` |
| `response.py` | `SmartResponseRequest`, catálogo |
| `activation.py` | `ActivationConfigResponse`, `WakeWordChunkScoreResponse` |
| `common.py` | Errores y tipos compartidos |

---

## Capa de aplicación (`application/`)

### Casos de uso (`use_cases/`)

| Clase | Responsabilidad |
|-------|-----------------|
| `ProcessVoiceCommandUseCase` | Orquesta STT → clasificación → respuesta → acción URL |
| `ClassifyIntentUseCase` | Texto limpio → `PredictionResult` |
| `RespondToIntentUseCase` | Clasificar + devolver mensaje |
| `GenerateSmartResponseUseCase` | Respuesta desde predicción existente |
| `ActivateAndListenUseCase` | Wake word local + comando micrófono |
| `GetDynamicResponseUseCase` | Respuesta aleatoria por nombre de intención |

**Flujo interno de `ProcessVoiceCommandUseCase`:**

1. `SpeechService` → `VoiceCommand` (transcript, language).
2. `ClassifyIntentUseCase` → intent, confidence, probabilities.
3. `SmartResponseService` → mensaje aleatorio desde JSON.
4. Si confianza ≥ umbral: `IntentActionExecutor` → `action_url` opcional.

### Interfaces (`interfaces/`)

Contratos que implementa la infraestructura:

| Interfaz | Implementación |
|----------|----------------|
| `ISpeechService` | `SpeechService` |
| `IResponseProvider` | `SmartResponseService` |
| `IWakeWordDetector` | `OpenWakeWordDetector`, `PorcupineDetector` |
| `IIntentActionExecutor` | `IntentActionExecutor` |

### Factories (`factories/`)

| Factory | Crea |
|---------|------|
| `MlFactory` | Predictor, `ClassifyIntentUseCase` |
| `ResponseFactory` | Loader, selector, `SmartResponseService` |
| `VoiceFactory` | `ProcessVoiceCommandUseCase` completo |
| `WakeWordFactory` | Detector según `WAKEWORD_ENGINE` |

### Servicios (`services/`)

| Servicio | Rol |
|----------|-----|
| `model_registry.py` | Singleton: modelo Keras, tokenizer, labels en memoria |
| `wakeword_chunk_scorer.py` | Un `OpenWakeWordDetector` por `X-Wake-Session`; puntúa PCM |
| `activation_listener.py` | Escucha wake word + pausa + comando (local) |
| `ml_bootstrap.py` | Carga artefactos al arrancar; predictor híbrido TF + keywords |

---

## Dominio (`domain/`)

### Entidades (`entities/`)

| Entidad | Campos relevantes |
|---------|-------------------|
| `VoiceCommand` | `transcript`, `language` |
| `VoiceProcessResult` | transcript, intent, confidence, response, `action_url`, `action_performed` |
| `PredictionResult` | intent, confidence, probabilities, cleaned_text |
| `WakeWordActivation` | keyword, engine, confidence, latency_ms |
| `IntentActionResult` | performed, url, detail |
| `SmartResponse` | message, intent, above_threshold, used_fallback |

### Excepciones (`exceptions/`)

| Módulo | Ejemplos |
|--------|----------|
| `base.py` | `ValidationError`, `NotFoundError` |
| `wakeword_exceptions.py` | `WakeWordTimeoutError`, `WakeWordModelNotFoundError` |
| `ml_exceptions.py` | `ModelNotLoadedError` |

Mapeadas a JSON en `core/errors/handlers.py`.

---

## Infraestructura (`infrastructure/`)

### ML TensorFlow (`infrastructure/ml/tensorflow/`)

| Ruta | Descripción |
|------|-------------|
| `nlp/text_cleaner.py` | Normalización (spaCy opcional) |
| `nlp/text_vectorizer.py` | Tokens → secuencia con padding |
| `nlp/label_encoder.py` | Intención ↔ índice |
| `nlp/pipeline.py` | Orquesta fit/transform |
| `model/architecture.py` | Embedding → GAP → Dense → Softmax |
| `training/trainer.py` | Entrenamiento Keras |
| `training/dataset_builder.py` | Lee `intents_dataset.json` |
| `inference/predictor.py` | `IntentClassifier.predict()` |
| `artifacts/artifact_store.py` | Guardar/cargar `.keras`, tokenizer, labels |
| `model_loader.py` | Carga al `ModelRegistry` |

### Predictor híbrido (`infrastructure/ml/`)

| Archivo | Rol |
|---------|-----|
| `keyword_intent_matcher.py` | Coincidencia por palabras clave si TF falla o intención nueva |
| `hybrid_intent_predictor.py` | Combina TF + keywords; usado en bootstrap |

### Voz (`infrastructure/speech/`)

| Archivo | Rol |
|---------|-----|
| `speech_service.py` | Google Speech Recognition (es-ES), micrófono PyAudio |
| `audio_validator.py` | Tamaño y formato WAV en uploads |
| `exception_mapper.py` | Errores de red/audio → excepciones de dominio |

### Respuestas (`infrastructure/responses/`)

| Archivo | Rol |
|---------|-----|
| `response_loader.py` | Carga `data/responses/responses.json` |
| `response_selector.py` | Elige variante aleatoria |
| `response_service.py` | `SmartResponseService` — une ML + catálogo |

### Acciones (`infrastructure/actions/`)

| Archivo | Rol |
|---------|-----|
| `intent_action_executor.py` | Mapea intención → URL (YouTube, Google, búsquedas temáticas) |

Intenciones con URL: `abrir_youtube`, `abrir_google`, `musica`, `clima`, `deportes`, `noticias`, etc.  
Intenciones solo informativas: `saludo`, `hora`, `creador`, `despedida`.

### Wake word (`infrastructure/wakeword/`)

| Archivo | Rol |
|---------|-----|
| `openwakeword_detector.py` | Modelo ONNX; `score_int16_chunk()`, `wait_for_activation()` |
| `porcupine_detector.py` | Alternativa con API key Picovoice |
| `detector_factory.py` | Elige motor según `WAKEWORD_ENGINE` |
| `audio_stream.py` | `MicrophoneChunkStream` para servidor local |

Constante: `CHUNK_SAMPLES = 1280` (~80 ms a 16 kHz).

### Persistencia (`infrastructure/persistence/json/`)

| Archivo | Rol |
|---------|-----|
| `intents_repository.py` | Lee dataset de entrenamiento |
| `responses_repository.py` | Acceso al catálogo de respuestas |
| `base_repository.py` | Utilidades JSON |

---

## Core transversal (`core/`)

### Configuración (`core/config/`)

`Settings` hereda de módulos especializados:

| Módulo | Variables ejemplo |
|--------|-------------------|
| `app_config.py` | `APP_ENV`, `DEBUG`, `APP_NAME` |
| `server_config.py` | `HOST`, `PORT`, `API_PREFIX`, `CORS_ORIGINS` |
| `ml_config.py` | `TF_EPOCHS`, `TF_CONFIDENCE_THRESHOLD`, rutas modelo |
| `wakeword_config.py` | `WAKEWORD_ENABLED`, `WAKEWORD_PHRASE`, `WAKEWORD_THRESHOLD` |
| `actions_config.py` | `ENABLE_SYSTEM_ACTIONS`, `CREATOR_NAME` |
| `logging_config.py` | `LOG_LEVEL`, `LOG_FORMAT` |
| `data_config.py` | Rutas a `data/` y `models/` |

Propiedad útil: `settings.is_production` — bloquea micrófono en servidor.

### Logging (`core/logging/setup.py`)

`get_logger(__name__)` — formato JSON en producción.

### Middleware (`core/middleware/`)

| Archivo | Función |
|---------|---------|
| `cors.py` | Orígenes desde `CORS_ORIGINS` |
| `request_logging.py` | `request_id`, duración, alertas lentas |

### Errores (`core/errors/handlers.py`)

Convierte excepciones de dominio y HTTP en respuestas JSON uniformes.

### Lifespan / bootstrap

Al arrancar: `MlBootstrap` entrena o carga modelo; registra predictor en `ModelRegistry`.

---

## Tests (`tests/`)

| Carpeta | Qué prueba |
|---------|------------|
| `api/` | Endpoints HTTP con TestClient |
| `ml/` | NLP, repositorio intents |
| `responses/` | Loader y selector |
| `speech/` | Validador de audio |
| `actions/` | URLs por intención |
| `wakeword/` | Activation listener |

Ejecutar: `PYTHONPATH=src pytest tests/ -v`

---

## Variables de entorno críticas

Ver `.env.example`. Las más usadas al desarrollar:

```env
PYTHONPATH=src
WAKEWORD_ENABLED=true
WAKEWORD_PHRASE=hey jarvis
WAKEWORD_MODEL_PATH=models/wakeword/hey_jarvis_v0.1.onnx
ENABLE_SYSTEM_ACTIONS=true
TF_CONFIDENCE_THRESHOLD=0.75
CORS_ORIGINS=http://localhost:5173
```
