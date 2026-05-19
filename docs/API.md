# Referencia de la API REST

Base URL por defecto: `http://localhost:8000/api/v1`

En producción sustituye por la URL de tu servicio Render.

---

## Convenciones

- Todas las respuestas de error siguen un esquema JSON uniforme (`message`, `details`, `request_id`).
- Las peticiones lentas (> `LOG_SLOW_REQUEST_MS`) se registran en logs.
- Content-Type JSON salvo endpoints con upload de archivo (`multipart/form-data`).

---

## Root y salud

### `GET /`

Información del servicio.

**Respuesta 200**

```json
{
  "service": "Asistente de Voz API",
  "version": "0.1.0",
  "environment": "development",
  "api_prefix": "/api/v1",
  "docs_url": "/docs",
  "health_url": "/api/v1/health"
}
```

---

### `GET /health`

Healthcheck para Docker, Render y balanceadores.

**Respuesta 200**

```json
{
  "status": "ok",
  "service": "Asistente de Voz API",
  "version": "0.1.0",
  "environment": "production",
  "timestamp": "2026-05-18T12:00:00+00:00",
  "request_id": "a1b2c3d4-..."
}
```

---

## Intents (TensorFlow)

### `POST /intents/predict`

Clasifica la intención del texto.

**Body**

```json
{
  "text": "abre youtube"
}
```

**Respuesta 200**

```json
{
  "intent": "abrir_youtube",
  "confidence": 0.9234,
  "raw_text": "abre youtube",
  "cleaned_text": "abrir youtube",
  "above_threshold": true,
  "probabilities": {
    "saludo": 0.01,
    "abrir_youtube": 0.92,
    "hora": 0.02
  }
}
```

**Errores**

| Código | Causa |
|--------|-------|
| 503 | Modelo no cargado |
| 422 | Texto vacío o inválido |

---

### `GET /intents/model/status`

Estado del modelo en memoria.

**Respuesta 200**

```json
{
  "loaded": true,
  "labels": ["saludo", "hora", "abrir_youtube"],
  "model_path": "/app/models/tensorflow/intent_classifier.keras"
}
```

---

## Responses

### `POST /responses/generate`

Clasifica texto y devuelve respuesta del catálogo JSON.

**Body**

```json
{
  "text": "qué hora es"
}
```

**Respuesta 200**

```json
{
  "transcript": "qué hora es",
  "intent": "hora",
  "confidence": 0.89,
  "above_threshold": true,
  "cleaned_text": "hora",
  "probabilities": { "hora": 0.89 },
  "response": {
    "intent": "hora",
    "message": "Son las 15:30.",
    "confidence": 0.89,
    "above_threshold": true,
    "variants_available": 5,
    "used_fallback": false
  }
}
```

---

### `GET /responses/catalog`

Lista intenciones con respuestas configuradas.

**Respuesta 200**

```json
{
  "version": "1.0.0",
  "default_intent": "desconocido",
  "intents": [
    { "intent": "saludo", "variants_count": 6, "enabled": true }
  ]
}
```

---

### `GET /responses/{intent_name}`

Respuesta aleatoria para una intención conocida (sin pasar por ML).

**Ejemplo:** `GET /responses/saludo`

---

## Voice

### `POST /voice/process`

Flujo completo desde **texto** (sin STT).

**Body**

```json
{
  "text": "hola"
}
```

**Respuesta 200**

```json
{
  "transcript": "hola",
  "language": "es-ES",
  "intent": "saludo",
  "confidence": 0.95,
  "above_threshold": true,
  "cleaned_text": "hola",
  "response": "¡Hola! ¿En qué puedo ayudarte?",
  "probabilities": { "saludo": 0.95 }
}
```

---

### `POST /voice/transcribe`

Solo transcribe audio a texto.

**Request:** `multipart/form-data`  
**Campo:** `audio` (archivo WAV)

**Respuesta 200**

```json
{
  "transcript": "abre google",
  "language": "es-ES"
}
```

---

### `POST /voice/process-audio`

Flujo completo: **WAV → transcripción → intención → respuesta**.

**Request:** `multipart/form-data`  
**Campo:** `audio` (archivo WAV, máx. 5 MB por defecto)

**Respuesta 200:** igual que `/voice/process`.

**Uso recomendado en producción** (frontend y clientes sin micrófono en servidor).

---

### `POST /voice/listen`

Captura desde el **micrófono del servidor** y procesa.

> **Solo desarrollo/local.** En `APP_ENV=production` responde `422` con hint para usar `/voice/process-audio`.

---

## Activation (wake word)

### `GET /activation/config`

Configuración actual de la palabra clave.

**Respuesta 200**

```json
{
  "enabled": true,
  "phrase": "oye sistema",
  "engine": "openwakeword",
  "threshold": 0.5,
  "listen_timeout": 60
}
```

---

### `POST /activation/listen`

Flujo de dos fases: detectar *"oye sistema"* → escuchar comando → clasificar → responder.

**Body (opcional)**

```json
{
  "wakeword_timeout": 30
}
```

**Respuesta 200**

```json
{
  "activation": {
    "keyword": "oye sistema",
    "engine": "openwakeword",
    "confidence": 0.87,
    "detected_at": "2026-05-18T12:00:00+00:00",
    "latency_ms": 420
  },
  "result": {
    "transcript": "abre youtube",
    "language": "es-ES",
    "intent": "abrir_youtube",
    "confidence": 0.91,
    "above_threshold": true,
    "cleaned_text": "abrir youtube",
    "response": "Abriendo YouTube.",
    "probabilities": { "abrir_youtube": 0.91 }
  }
}
```

> **Solo desarrollo/local.** No disponible en Render.

---

## Códigos de error comunes

| HTTP | Tipo | Descripción |
|------|------|-------------|
| 400 | `ValidationError` | Entrada inválida |
| 404 | `NotFoundError` | Recurso no encontrado |
| 422 | Validación Pydantic / reglas de negocio | Body o archivo incorrecto |
| 500 | Error interno | Error no controlado |
| 503 | `ModelNotLoadedError` | Modelo TF no disponible |

---

## OpenAPI / Swagger

Con `ENABLE_DOCS=true` y entorno no productivo (o `DEBUG=true`):

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

En producción (`ENABLE_DOCS=false`, `APP_ENV=production`) la documentación interactiva está deshabilitada.
