# Referencia del frontend (`frontend/src/`)

Cliente web en **React 19 + TypeScript + Vite 6 + Tailwind CSS**. Se comunica con la API REST en `/api/v1`.

---

## Estructura de carpetas

```
frontend/src/
├── main.tsx              # Montaje React
├── App.tsx               # Layout principal y composición de hooks
├── index.css             # Estilos globales Tailwind
├── types/api.ts          # Tipos TypeScript del API
├── hooks/                # Lógica de estado
├── services/             # Cliente HTTP
├── utils/                # Audio, voz, enlaces externos
└── components/
    ├── layout/           # Cabecera
    ├── assistant/        # UI del asistente
    └── ui/               # Card, Badge, Spinner
```

---

## Punto de entrada

### `main.tsx`

Monta `<App />` en `#root` con `StrictMode`.

### `App.tsx`

Componente raíz:

1. `useVoiceAssistant()` — estado global del asistente.
2. `useOpenWakeWord()` — detección «Hey Jarvis».
3. Renderiza paneles: wake word, micrófono, transcripción, intención, respuesta, entrada de texto.

Props clave pasadas a wake word:

- `micPaused: assistant.isListening || assistant.isProcessing` — libera el micrófono al grabar comando.

---

## Hooks (`hooks/`)

### `useVoiceAssistant.ts`

**Estado (`AssistantState`):**

| Campo | Descripción |
|-------|-------------|
| `status` | `idle` \| `listening` \| `processing` \| `success` \| `error` |
| `transcript`, `intent`, `confidence`, `response` | Último resultado |
| `apiOnline` | Health check al montar |
| `voiceEnabled` | Síntesis de voz ON/OFF (localStorage) |
| `wakeWordEnabled` | Wake word ON/OFF (localStorage) |
| `pendingActionUrl` | URL a abrir (Safari: requiere toque) |

**Funciones exportadas:**

| Función | Acción |
|---------|--------|
| `toggleMicrophone` | Inicia/detiene grabación → `processVoiceAudio` |
| `sendText` | `POST /voice/process` con texto |
| `handleWakeWordDetected` | Tras wake word: dice «Te escucho», graba ~10 s |
| `toggleWakeWord` | Persiste preferencia en localStorage |
| `dismissPendingAction` | Cierra banner de enlace |

**Flujo de grabación:**

1. `AudioRecorder.start()` — captura PCM.
2. Al parar: WAV 16 kHz mono → `processVoiceAudio(blob)`.
3. `applyResult()` — actualiza UI, intenta abrir `action_url`, habla respuesta.

**Safari:** si `requiresTapToOpenLink()`, no usa `window.open`; muestra `pendingActionUrl` para el banner.

### `useOpenWakeWord.ts`

**Responsabilidad:** enviar audio del micrófono al servidor para detectar «Hey Jarvis».

| Constante | Valor | Motivo |
|-----------|-------|--------|
| `CHUNKS_PER_BATCH` | 4 | Menos peticiones HTTP a Render |
| `MAX_QUEUE_CHUNKS` | 32 | Buffer ante latencia de red |
| `COOLDOWN_MS` | 2500 | Evita doble activación |

**Flujo:**

1. `fetchActivationConfig()` — comprueba `enabled` y `engine`.
2. `WakeWordMicStream.start()` — emite `Int16Array` de 1280 muestras.
3. Cola → `scoreWakeWordChunks()` (fallback a `score-chunk` si 404).
4. Si `activated` → `onWakeWord()` → `handleWakeWordDetected`.

**Estado devuelto:**

- `wakeWordListening`, `wakeWordError`, `wakeWordPhrase`
- `wakeWordLastScore`, `wakeWordThreshold` — indicador de señal en UI

---

## Servicios HTTP (`services/`)

### `apiClient.ts`

| Función | Uso |
|---------|-----|
| `apiGet`, `apiPostJson`, `apiPostForm` | JSON y multipart |
| `apiPostBinary` | PCM wake word (`application/octet-stream`) |
| `apiDelete` | Cerrar sesión wake word |

Base URL: `import.meta.env.VITE_API_BASE_URL` (en Render: URL completa de la API).

Clase `ApiError` — status HTTP + cuerpo JSON de error.

### `voiceService.ts`

- `processVoiceText(text)` → `POST /voice/process`
- `processVoiceAudio(blob)` → `POST /voice/process-audio` (FormData)

### `activationService.ts`

- `fetchActivationConfig()`
- `scoreWakeWordChunk` / `scoreWakeWordChunks`
- `endWakeWordSession(sessionId)`

### `healthService.ts`

- `checkHealth()` → `GET /health`

---

## Utilidades (`utils/`)

### `audioRecorder.ts`

Graba desde `getUserMedia`, acumula buffers, exporta **WAV 16 kHz mono** (compatible con la API).

- Llama `audioContext.resume()` para móviles.
- Usa `ScriptProcessorNode` (legacy pero amplio soporte).

### `wakeWordMicStream.ts`

Captura continua para wake word:

- Objetivo: **16 kHz**, fragmentos de **1280 muestras** (2560 bytes).
- Resample si el `AudioContext` usa otra frecuencia.
- Salida silenciosa (`GainNode` a 0) para no reproducir eco.

### `speechSynthesis.ts`

- `speakText()` — respuesta hablada en español.
- `getVoiceEnabled` / `setVoiceEnabled` — preferencia en localStorage.

### `openExternalUrl.ts`

| Función | Rol |
|---------|-----|
| `requiresTapToOpenLink()` | Detecta iOS/Safari |
| `tryOpenExternalUrl(url)` | `window.open` en escritorio |
| `actionLinkLabel(intent, url)` | Texto del botón «Abrir YouTube» |

---

## Componentes (`components/`)

### Layout

| Componente | Archivo | Descripción |
|------------|---------|-------------|
| `Header` | `layout/Header.tsx` | Título + badge API conectada/desconectada |

### Asistente

| Componente | Descripción |
|------------|-------------|
| `WakeWordPanel` | Toggle wake word, frase, señal %, errores |
| `MicrophoneButton` | Botón central grabar/parar |
| `ListeningAnimation` | Animación mientras escucha |
| `TranscriptPanel` | Texto reconocido |
| `IntentPanel` | Intención + confianza |
| `ResponsePanel` | Respuesta + voz ON/OFF + repetir |
| `TextInputBar` | Comando por texto |
| `ActionOpenBanner` | Botón verde para abrir URL en Safari |

### UI genéricos

`Card`, `Badge`, `Spinner` — contenedores y estados visuales.

---

## Tipos (`types/api.ts`)

```typescript
interface VoiceProcessResult {
  transcript: string;
  intent: string;
  confidence: number;
  response: string;
  action_url?: string | null;
  action_performed?: boolean;
  probabilities: Record<string, number>;
}
```

---

## Configuración

### `frontend/.env`

```env
# Desarrollo (proxy Vite → localhost:8000)
VITE_API_BASE_URL=/api/v1

# Producción (Render)
# VITE_API_BASE_URL=https://tu-api.onrender.com/api/v1
```

### `vite.config.ts`

Proxy `/api` → `http://localhost:8000` en desarrollo.

### Build producción

```bash
cd frontend
npm install
npm run build   # salida en dist/
```

En Render (`render.yaml`): `rootDir: frontend`, variable `VITE_API_BASE_URL` en build.

---

## Flujo de datos (diagrama)

```
App
 ├─ useVoiceAssistant ──► voiceService ──► API /voice/*
 ├─ useOpenWakeWord ────► activationService ──► API /activation/*
 └─ ActionOpenBanner ───► <a href> (toque usuario, Safari)
```

---

## Limitaciones del navegador

| Limitación | Dónde se mitiga |
|------------|-----------------|
| Popup bloqueado tras voz | `ActionOpenBanner`, `openExternalUrl.ts` |
| AudioContext suspendido | `resume()` en mic streams |
| Un solo micrófono | `micPaused` en wake word |
| HTTPS obligatorio para mic | Render sirve HTTPS |

Ver [ACCIONES_NAVEGADOR.md](./ACCIONES_NAVEGADOR.md).
