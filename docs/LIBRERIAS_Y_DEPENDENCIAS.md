# Librerías y dependencias del proyecto

Inventario de **runtime**, **herramientas de desarrollo**, **modelos externos** y **servicios de terceros** usados por el Asistente de Voz.

---

## Resumen por capa

| Capa | Tecnologías principales |
|------|-------------------------|
| **API** | Python 3.11, FastAPI, Uvicorn, Pydantic |
| **ML / NLP** | TensorFlow 2.18, Keras, spaCy (`es_core_news_sm`) |
| **Voz (STT)** | SpeechRecognition → Google Web Speech API |
| **Wake word** | openWakeWord 0.6, ONNX Runtime, modelo `hey_jarvis_v0.1.onnx` |
| **Frontend** | React 19, Vite 6, TypeScript 5.7, Tailwind CSS 3.4 |
| **Hosting** | Render (Blueprint `render.yaml`) |

---

## Python — producción (`requirements-prod.txt`)

Usado en **Render** y en Docker. **No incluye PyAudio** (no compila en la nube).

| Paquete | Versión | Para qué sirve |
|---------|---------|----------------|
| `fastapi` | 0.115.6 | Framework REST, validación, OpenAPI |
| `uvicorn[standard]` | 0.34.0 | Servidor ASGI |
| `pydantic` | 2.10.4 | Esquemas y validación de datos |
| `pydantic-settings` | 2.7.0 | Configuración desde `.env` |
| `python-multipart` | 0.0.20 | Subida de archivos WAV (`process-audio`) |
| `tensorflow` | 2.18.1 | Clasificador de intenciones (Keras) |
| `spacy` | 3.8.x | Limpieza y lematización de texto |
| `SpeechRecognition` | 3.12.0 | Wrapper STT (Google, micrófono local) |
| `onnxruntime` | 1.16–1.26 | Inferencia del modelo wake word ONNX |
| `scipy` | 1.9–1.16 | Dependencia numérica de openWakeWord |
| `scikit-learn` | 1.3+ | Utilidades ML (openWakeWord) |
| `tqdm` | 4.x | Barras de progreso en scripts |
| `requests` | 2.28+ | HTTP en scripts de descarga |
| `python-dotenv` | 1.0.1 | Carga de `.env` en desarrollo |
| `httpx` | 0.28.1 | Cliente HTTP async (si se usa en infra) |

### Instalación aparte en build (Render)

| Paquete | Versión | Motivo |
|---------|---------|--------|
| `openwakeword` | 0.6.0 (`--no-deps`) | Evita `tflite-runtime` incompatible con Python 3.12 en Render |
| `es_core_news_sm` | spaCy | Modelo de lenguaje español (`python -m spacy download`) |

Script: `scripts/render_build.sh`

---

## Python — desarrollo local (`requirements-dev.txt`)

Incluye producción más herramientas locales:

| Paquete | Versión | Para qué sirve |
|---------|---------|----------------|
| *(todo `requirements-prod.txt`)* | — | Base de producción |
| `PyAudio` | 0.2.14 | Micrófono en servidor (`/voice/listen`, wake word local) |
| `pvporcupine` | 3.0.5 | Motor alternativo de wake word (requiere API key) |
| `pytest` | 8.3.4 | Tests |
| `pytest-asyncio` | 0.25.0 | Tests async de FastAPI |
| `ruff` | 0.8.4 | Linter y formateo |

Instalación local:

```bash
pip install -r requirements.txt   # apunta a requirements-dev.txt
python -m spacy download es_core_news_sm
pip install openwakeword==0.6.0 --no-deps   # recomendado igual que Render
python scripts/download_wakeword_model.py
```

---

## Versiones de Python

| Entorno | Versión | Archivo |
|---------|---------|---------|
| **Render (API)** | 3.11.11 | `runtime.txt` |
| **Desarrollo** | 3.12+ recomendado | README |
| **Node (frontend)** | 20 | `render.yaml` → `NODE_VERSION` |

> En Python 3.12, openWakeWord debe instalarse con `--no-deps` y usar ONNX, no TFLite.

---

## Frontend (`frontend/package.json`)

### Dependencias de producción (bundle)

| Paquete | Versión | Uso |
|---------|---------|-----|
| `react` | ^19.0.0 | UI |
| `react-dom` | ^19.0.0 | Render en DOM |

### Solo desarrollo (no van al build final de la misma forma)

| Paquete | Versión | Uso |
|---------|---------|-----|
| `vite` | ^6.0.6 | Bundler y dev server |
| `@vitejs/plugin-react` | ^4.3.4 | Plugin React para Vite |
| `typescript` | ^5.7.2 | Tipado |
| `tailwindcss` | ^3.4.17 | Estilos utility-first |
| `postcss` | ^8.4.49 | Pipeline CSS |
| `autoprefixer` | ^10.4.20 | Prefijos CSS |
| `@types/react` | ^19.0.2 | Tipos React |
| `@types/react-dom` | ^19.0.2 | Tipos React DOM |

El frontend **no** usa librerías de ML ni wake word en el cliente: solo `fetch` nativo hacia la API.

---

## Modelos y datos en disco (no son pip/npm)

| Recurso | Ruta | Origen |
|---------|------|--------|
| Clasificador Keras | `models/tensorflow/intent_classifier.keras` | Entrenamiento (`train_intent_model.py`) |
| Tokenizer | `models/tensorflow/tokenizer.json` | Entrenamiento |
| Etiquetas | `models/tensorflow/labels.json` | Entrenamiento |
| Metadatos entrenamiento | `models/tensorflow/training_metadata.json` | Entrenamiento |
| Wake word ONNX | `models/wakeword/hey_jarvis_v0.1.onnx` | `download_wakeword_model.py` |
| Dataset intenciones | `data/intents/intents_dataset.json` | Manual / ampliación |
| Respuestas | `data/responses/responses.json` | Manual |

### spaCy (modelo de lenguaje)

| Modelo | ID | Tamaño aprox. |
|--------|-----|----------------|
| Español | `es_core_news_sm` | ~15 MB |

---

## Servicios externos (internet)

| Servicio | Usado por | Requiere API key | Notas |
|----------|-----------|------------------|-------|
| **Google Web Speech API** | `SpeechRecognition` | No (límite de uso público) | Transcripción `es-ES`; necesita conexión |
| **Render** | Hosting API + static site | Cuenta Render | `render.yaml` |
| **Porcupine** (opcional) | `porcupine_detector.py` | Sí (`PORCUPINE_ACCESS_KEY`) | No es el flujo por defecto |
| **GitHub** (opcional) | Descarga modelos openWakeWord | No | Script `download_wakeword_model.py` |

No hay base de datos externa: todo es JSON + archivos en disco.

---

## APIs del navegador (frontend)

| API | Uso |
|-----|-----|
| `fetch` | Llamadas REST a la API |
| `MediaDevices.getUserMedia` | Micrófono (wake word y grabación) |
| `AudioContext` / `ScriptProcessorNode` | Captura y PCM 16 kHz |
| `speechSynthesis` | Respuesta hablada (TTS del sistema) |
| `localStorage` | Preferencias wake word / voz ON |

---

## Mapa: librería → archivo del proyecto

| Librería | Dónde se usa en el código |
|----------|---------------------------|
| FastAPI | `api/`, `main.py`, `core/app_factory.py` |
| TensorFlow | `infrastructure/ml/tensorflow/` |
| spaCy | `infrastructure/nlp/`, `nlp/text_cleaner.py` |
| SpeechRecognition | `infrastructure/speech/speech_service.py` |
| openWakeWord | `infrastructure/wakeword/openwakeword_detector.py` |
| React | `frontend/src/App.tsx`, componentes, hooks |

---

## Dónde está cada cosa en la documentación

| Tema | Documento |
|------|-----------|
| Código Python módulo a módulo | [BACKEND.md](./BACKEND.md) |
| Código React | [FRONTEND.md](./FRONTEND.md) |
| Modelos y entrenamiento | [DATOS_Y_MODELOS.md](./DATOS_Y_MODELOS.md) |
| Wake word | [WAKE_WORD.md](./WAKE_WORD.md) |
| Variables de entorno | [README.md](../README.md#variables-de-entorno), `.env.example` |
| Deploy e instalación | [DESPLIEGUE_SIN_DOCKER.md](./DESPLIEGUE_SIN_DOCKER.md) |

---

## Actualizar dependencias

1. Cambiar versión en `requirements-prod.txt` o `package.json`.
2. Probar localmente (`pip install`, `npm install`, tests, build).
3. En Render: nuevo deploy de API y/o frontend.
4. Actualizar esta tabla si cambias versiones fijas.
