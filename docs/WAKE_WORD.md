# Wake word «Hey Jarvis»

Documentación del sistema de activación por palabra clave en **local** y en **Render (producción)**.

---

## Resumen

| Entorno | Micrófono | Detección | Comando |
|---------|-----------|-----------|---------|
| **Render + navegador** | Cliente (React) | Servidor openWakeWord | Cliente graba → `/voice/process-audio` |
| **Local API** | Servidor (PyAudio) | `POST /activation/listen` | Mismo flujo en backend |

La frase por defecto es **«hey jarvis»** (inglés). El modelo es `hey_jarvis_v0.1.onnx`.

---

## Flujo en producción (navegador)

```
┌─────────────┐     PCM 16kHz      ┌──────────────┐
│  Navegador  │ ─────────────────► │   Render API │
│ WakeWordMic │  POST score-chunks  │ openWakeWord │
└─────────────┘  X-Wake-Session     └──────────────┘
       │                                    │
       │         activated: true            │
       ▼                                    │
  handleWakeWordDetected                    │
       │                                    │
       ▼                                    │
  AudioRecorder (~10 s)                     │
       │                                    │
       └──── POST /voice/process-audio ────►│
                                            ▼
                                    VoiceProcessResult
```

### Por qué el audio va al servidor

openWakeWord corre en **Python** con ONNX. En Render no hay micrófono en el servidor; el navegador captura y envía fragmentos.

### Sesión `X-Wake-Session`

Cada pestaña genera un UUID. El backend mantiene **un detector por sesión** (`WakeWordChunkScorer`) para conservar el estado temporal del modelo entre fragmentos.

### Tamaño del fragmento

- **1280 muestras** int16 mono 16 kHz
- **2560 bytes** por fragmento
- `/score-chunks` acepta múltiplos de 2560 bytes concatenados

### Umbral

`WAKEWORD_THRESHOLD` (p. ej. `0.22` en `render.yaml`). Si `score >= threshold` → `activated: true`.

---

## Código relevante

### Backend

| Archivo | Función |
|---------|---------|
| `wakeword_chunk_scorer.py` | Cola de sesiones, `score_chunk`, `score_chunks` |
| `openwakeword_detector.py` | Carga ONNX, `predict(pcm)` |
| `activation.py` | Endpoints REST |
| `dependencies.py` | Singleton `WakeWordChunkScorer` |

### Frontend

| Archivo | Función |
|---------|---------|
| `wakeWordMicStream.ts` | Captura y resample a 16 kHz |
| `useOpenWakeWord.ts` | Cola, batch HTTP, cooldown |
| `WakeWordPanel.tsx` | UI y % de señal |

---

## Problemas frecuentes

| Síntoma | Causa | Solución |
|---------|-------|----------|
| Señal siempre 0% | Mic bloqueado / AudioContext suspendido | Permisos; `audioContext.resume()`; HTTPS |
| No activa en Render | Latencia + fragmentos perdidos | Usar `/score-chunks`; cola amplia |
| Funciona en PC, no en iPhone | Safari + red lenta | Hablar claro «Hey Jarvis»; esperar cold start |
| 503 en score-chunk | openWakeWord no instalado | Py 3.11, `pip install openwakeword==0.6.0 --no-deps` |
| Detecta pero no graba comando | Dos micrófonos a la vez | `micPaused` al grabar comando |

---

## Configuración Render (`render.yaml`)

```yaml
WAKEWORD_ENABLED: "true"
WAKEWORD_ENGINE: openwakeword
WAKEWORD_PHRASE: hey jarvis
WAKEWORD_MODEL_PATH: models/wakeword/hey_jarvis_v0.1.onnx
WAKEWORD_THRESHOLD: "0.22"
```

Build debe ejecutar `download_wakeword_model.py` (incluido en `render_build.sh`).

---

## Alternativa: Porcupine

`WAKEWORD_ENGINE=porcupine` requiere `PORCUPINE_ACCESS_KEY` y archivo `.ppn`. No es el flujo por defecto del proyecto.

---

## Prueba manual del endpoint

```bash
# Fragmento de silencio (score ~0)
python scripts/test_score_chunk.py
```

O con curl desde un script que envíe 2560 bytes PCM.
