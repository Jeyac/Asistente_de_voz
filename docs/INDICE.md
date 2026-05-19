# Índice de documentación del código

Documentación técnica del proyecto **Asistente de Voz**. Empieza aquí si quieres entender o modificar el código.

> El código fuente incluye **comentarios en español** en módulos clave (hooks, casos de uso, wake word, acciones, API). La referencia detallada sigue en los documentos `.md` de esta carpeta.

---

## Guías principales

| Documento | Contenido |
|-----------|-----------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Capas, principios, flujos ML/voz, despliegue |
| [BACKEND.md](./BACKEND.md) | **Referencia de todo el código Python** (`src/asistente_voz/`) |
| [FRONTEND.md](./FRONTEND.md) | **Referencia de todo el código React** (`frontend/src/`) |
| [API.md](./API.md) | Endpoints REST, ejemplos request/response |
| [DATOS_Y_MODELOS.md](./DATOS_Y_MODELOS.md) | JSON de intenciones/respuestas, TensorFlow, wake word ONNX |
| [WAKE_WORD.md](./WAKE_WORD.md) | «Hey Jarvis»: micrófono, score-chunk, Render |
| [ACCIONES_NAVEGADOR.md](./ACCIONES_NAVEGADOR.md) | Abrir YouTube/Google; Safari y móviles |
| [SCRIPTS.md](./SCRIPTS.md) | Scripts de entrenamiento, build y arranque |
| [DESPLIEGUE_SIN_DOCKER.md](./DESPLIEGUE_SIN_DOCKER.md) | Render sin Docker (`render.yaml`) |

---

## Mapa rápido del repositorio

```
Asistente de voz/
├── src/asistente_voz/     → Backend (FastAPI, Clean Architecture)
├── frontend/src/          → Cliente web (React + Vite)
├── data/                  → Dataset y respuestas (JSON)
├── models/                → Artefactos ML y wake word (generados)
├── scripts/               → Entrenamiento, build Render, utilidades
├── tests/                 → pytest
├── render.yaml            → Blueprint Render (API + static site)
└── docs/                  → Esta carpeta
```

---

## Flujos que debes conocer

### 1. Comando de voz (botón micrófono o texto)

```
Usuario → frontend (WAV/texto)
       → POST /api/v1/voice/process-audio
       → SpeechService (Google STT)
       → ClassifyIntentUseCase (TensorFlow + respaldo keywords)
       → SmartResponseService (responses.json)
       → IntentActionExecutor (URL opcional)
       → JSON → frontend (respuesta + action_url)
```

### 2. Wake word «Hey Jarvis» (producción)

```
Usuario → WakeWordMicStream (PCM 16 kHz)
       → POST /activation/score-chunks (openWakeWord en servidor)
       → activated=true → grabar comando → process-audio
```

### 3. Abrir sitios (YouTube, etc.)

```
Intención abrir_youtube → action_url en respuesta
                       → frontend: botón «Abrir YouTube» (Safari)
                       → o window.open en escritorio
```

---

## Intenciones del modelo (19 + fallback)

`saludo`, `hora`, `abrir_youtube`, `abrir_google`, `clima`, `despedida`, `musica`, `buscar_web`, `creador`, `relacion_creador`, `deportes`, `noticias`, `historia`, `tecnologia`, `ciencia`, `cultura`, `entretenimiento`, `salud`, `viajes`, más `desconocido` como fallback.

Definidas en `data/intents/intents_dataset.json` y `data/responses/responses.json`.

---

## Enlaces externos útiles

- [openWakeWord](https://github.com/dscripka/openWakeWord)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Render Blueprint](https://render.com/docs/blueprint-spec)
