# Arquitectura del sistema

Documentación técnica del **Asistente de Voz**: capas, dependencias, modelo ML y flujos de procesamiento.

---

## Principios de diseño

1. **Independencia del dominio** — Las entidades y reglas de negocio no importan FastAPI, TensorFlow ni librerías de audio.
2. **Inversión de dependencias** — La capa de aplicación define interfaces; la infraestructura las implementa.
3. **Casos de uso explícitos** — Cada operación de negocio es una clase (`ProcessVoiceCommandUseCase`, `ClassifyIntentUseCase`, etc.).
4. **Configuración por entorno** — Sin constantes mágicas en el código; todo vía `Settings` y variables de entorno.
5. **Sin base de datos** — Persistencia en archivos JSON y artefactos de modelo en disco.

---

## Diagrama de capas

```
┌─────────────────────────────────────────────────────────────┐
│  Presentation                                                │
│  • frontend/ (React)                                         │
│  • api/v1/endpoints/*.py                                     │
│  • schemas/ (Pydantic DTOs)                                  │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP / Depends
┌──────────────────────────▼──────────────────────────────────┐
│  Application                                                 │
│  • use_cases/          (orquestación)                        │
│  • factories/          (composición de servicios)            │
│  • interfaces/         (contratos)                           │
│  • services/           (model_registry, activation_listener)│
└──────────────────────────┬──────────────────────────────────┘
                           │ interfaces
┌──────────────────────────▼──────────────────────────────────┐
│  Domain                                                      │
│  • entities/           (VoiceCommand, PredictionResult, …)   │
│  • exceptions/         (ValidationError, ModelNotLoaded, …)  │
└──────────────────────────┬──────────────────────────────────┘
                           │ implementado por
┌──────────────────────────▼──────────────────────────────────┐
│  Infrastructure                                              │
│  • ml/tensorflow/      (entrenamiento, inferencia, NLP)      │
│  • speech/             (SpeechRecognition, validador WAV)  │
│  • responses/          (loader, selector, servicio)        │
│  • wakeword/           (openWakeWord, Porcupine)             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Core (transversal)                                          │
│  • config/  • logging/  • middleware/  • lifespan/         │
│  • errors/  • bootstrap/  • app_factory.py                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Ciclo de vida de la aplicación

Al arrancar, el **lifespan** de FastAPI ejecuta el bootstrap del modelo ML:

1. `MlBootstrap` carga artefactos desde `models/tensorflow/`.
2. Registra predictor, tokenizer y labels en `ModelRegistry` (singleton).
3. Si el modelo no existe, la API arranca pero `/intents/predict` devolverá error controlado.

Middleware registrado:

| Middleware | Función |
|------------|---------|
| **CORS** | Orígenes desde `CORS_ORIGINS` |
| **Request logging** | Duración, `request_id`, alertas de peticiones lentas |

---

## Casos de uso principales

| Caso de uso | Entrada | Salida |
|-------------|---------|--------|
| `ProcessVoiceCommandUseCase` | Texto, WAV o micrófono | `VoiceProcessResult` |
| `ClassifyIntentUseCase` | Texto | `PredictionResult` |
| `RespondToIntentUseCase` | Texto | Predicción + `SmartResponse` |
| `ActivateAndListenUseCase` | Timeout opcional | Wake word + resultado de voz |

---

## Modelo de intenciones (TensorFlow)

### Dataset

Fuente: `data/intents/intents_dataset.json`

- 8 intenciones con ~8–10 ejemplos cada una.
- Idioma: español (`"language": "es"`).
- Extensible añadiendo intenciones y reentrenando.

### Preprocesamiento (`infrastructure/ml/tensorflow/nlp/`)

| Componente | Rol |
|------------|-----|
| `TextCleaner` | spaCy: tokenización, lemas, filtrado |
| `TextVectorizer` | Índices de tokens, `max_vocab_size`, padding |
| `LabelEncoder` | One-hot / índices de clase |
| `NlpPipeline` | Orquesta fit/transform para train e inferencia |

### Red neuronal (`model/architecture.py`)

| Capa | Parámetros |
|------|------------|
| Input | `(sequence_length,)` tokens |
| Embedding | `vocab_size × embedding_dim`, `mask_zero=True` |
| GlobalAveragePooling1D | Agregación de secuencia |
| Dense | 64 unidades, ReLU |
| Dropout | 0.3 |
| Dense (salida) | `num_classes`, softmax |

Optimizador: Adam (`TF_LEARNING_RATE`).  
Pérdida: `sparse_categorical_crossentropy`.  
Métrica: `accuracy`.

### Inferencia (`inference/predictor.py`)

1. Limpiar texto de entrada.
2. Vectorizar con tokenizer persistido.
3. `model.predict()` → distribución de probabilidades.
4. Si `confidence < TF_CONFIDENCE_THRESHOLD` → `TF_FALLBACK_INTENT` (`desconocido`).

### Artefactos (`artifacts/`)

`ArtifactPaths` resuelve rutas desde `Settings`.  
`ArtifactStore` guarda y carga `.keras`, JSON de tokenizer y labels.

---

## Módulo de voz

### `SpeechService`

| Método | Descripción |
|--------|-------------|
| `transcribe_from_text` | Pasa el texto sin STT (útil para pruebas) |
| `transcribe_from_audio` | WAV → Google Speech Recognition (es-ES) |
| `listen_from_microphone` | Captura en tiempo real vía PyAudio |

### Validación de audio

`AudioValidator` comprueba:

- Formato permitido (`wav`, `wave`)
- Tamaño máximo (`SPEECH_MAX_AUDIO_BYTES`, default 5 MB)
- Content-Type del upload

---

## Módulo de respuestas

`data/responses/responses.json` define variantes por intención.

Flujo:

1. `ResponseLoader` carga el catálogo al inicio.
2. `ResponseSelector` elige una variante aleatoria.
3. `SmartResponseService` combina predicción ML + selección.

Si la confianza está por debajo del umbral, usa respuestas del intent fallback.

---

## Wake word (solo local)

Motores soportados (`WAKEWORD_ENGINE`):

- **openwakeword** — modelo ONNX en `models/wakeword/oye_sistema.onnx`
- **porcupine** — requiere `PORCUPINE_ACCESS_KEY`

Flujo `ActivateAndListenUseCase`:

1. Escuchar hasta detectar la frase configurada.
2. Capturar comando de voz con SpeechRecognition.
3. Delegar en `ProcessVoiceCommandUseCase`.

En `APP_ENV=production` este flujo está **deshabilitado** (sin hardware de audio en la nube).

---

## Flujo de voz end-to-end

```
Usuario
   │
   ├─ Texto ──────────────► POST /voice/process
   ├─ Archivo WAV ────────► POST /voice/process-audio
   └─ Micrófono (local) ──► POST /voice/listen
              │
              ▼
      SpeechService (transcripción)
              │
              ▼
      ClassifyIntentUseCase
         ├─ TextCleaner
         ├─ TextVectorizer
         └─ IntentClassifier (Keras)
              │
              ▼
      SmartResponseService
         └─ ResponseSelector (JSON)
              │
              ▼
      VoiceProcessResponse
```

---

## Frontend

El cliente React (`frontend/`) graba audio a **16 kHz WAV** y lo envía a `/voice/process-audio`.

Componentes clave:

- `useVoiceAssistant` — estado del asistente
- `audioRecorder.ts` — captura y codificación WAV
- `voiceService.ts` — cliente HTTP

En desarrollo, Vite hace proxy de `/api` al backend.

---

## Despliegue y restricciones en la nube

| Funcionalidad | Local | Render / Docker |
|---------------|:-----:|:---------------:|
| `/voice/process` | Sí | Sí |
| `/voice/process-audio` | Sí | Sí |
| `/voice/listen` | Sí | No |
| `/activation/listen` | Sí | No |
| Wake word | Sí | No (`WAKEWORD_ENABLED=false`) |
| Entrenamiento ML | Manual o script | Automático en Docker build |
