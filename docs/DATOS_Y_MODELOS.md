# Datos, modelos y entrenamiento

Documentación de archivos de datos, artefactos generados y pipelines de ML / wake word.

---

## Datos (`data/`)

### `data/intents/intents_dataset.json`

Dataset de entrenamiento del clasificador.

**Estructura:**

```json
{
  "language": "es",
  "intents": [
    {
      "name": "abrir_youtube",
      "examples": ["abre youtube", "abrir youtube", ...]
    }
  ]
}
```

**Intenciones actuales (19):**

| Intención | Ejemplo de uso |
|-----------|----------------|
| `saludo` | hola, buenos días |
| `hora` | qué hora es |
| `abrir_youtube` | abre youtube |
| `abrir_google` | abre google |
| `clima` | qué tiempo hace |
| `despedida` | adiós |
| `musica` | pon música |
| `buscar_web` | busca en internet |
| `creador` | quién te creó |
| `relacion_creador` | quién es tu novio |
| `deportes` | noticias de deportes |
| `noticias` | últimas noticias |
| `historia` | historia del mundo |
| `tecnologia` | noticias de tecnología |
| `ciencia` | noticias de ciencia |
| `cultura` | cultura y arte |
| `entretenimiento` | entretenimiento |
| `salud` | consejos de salud |
| `viajes` | destinos de viaje |

**Añadir una intención:**

1. Añadir bloque en `intents_dataset.json` con ≥15 ejemplos variados.
2. Añadir respuestas en `responses.json`.
3. Reentrenar: `PYTHONPATH=src python scripts/train_intent_model.py`
4. (Opcional) Añadir URL en `intent_action_executor.py` si abre un sitio.

---

### `data/responses/responses.json`

Variantes de respuesta por intención (el asistente elige una al azar).

```json
{
  "abrir_youtube": {
    "variants": [
      "Abriendo YouTube.",
      "De acuerdo, lanzo YouTube."
    ]
  }
}
```

Intención `desconocido` — fallback cuando la confianza ML es baja.

---

## Modelo TensorFlow (`models/tensorflow/`)

Generados por entrenamiento (no editar a mano):

| Archivo | Contenido |
|---------|-----------|
| `intent_classifier.keras` | Red Keras entrenada |
| `tokenizer.json` | Vocabulario y longitud de secuencia |
| `labels.json` | Lista ordenada de nombres de intención |
| `training_metadata.json` | Accuracy, épocas, fecha |

### Arquitectura

```
Input (tokens)
  → Embedding (mask_zero)
  → GlobalAveragePooling1D
  → Dense(64, ReLU)
  → Dropout(0.3)
  → Dense(num_classes, softmax)
```

### Inferencia

1. `TextCleaner` normaliza el texto.
2. `TextVectorizer` convierte a secuencia de índices.
3. `model.predict()` → probabilidades.
4. Si `max(prob) < TF_CONFIDENCE_THRESHOLD` → intent `desconocido` (configurable).

### Predictor híbrido

Si el modelo en disco no incluye intenciones nuevas del JSON, `keyword_intent_matcher.py` puede reconocer frases conocidas como respaldo (`hybrid_intent_predictor.py`).

---

## Wake word (`models/wakeword/`)

| Archivo | Descripción |
|---------|-------------|
| `hey_jarvis_v0.1.onnx` | Modelo openWakeWord para la frase «hey jarvis» |

**Descarga:**

```bash
python scripts/download_wakeword_model.py
```

En build de Render (`scripts/render_build.sh`) se ejecuta automáticamente.

**Configuración (.env):**

```env
WAKEWORD_ENABLED=true
WAKEWORD_ENGINE=openwakeword
WAKEWORD_PHRASE=hey jarvis
WAKEWORD_MODEL_PATH=models/wakeword/hey_jarvis_v0.1.onnx
WAKEWORD_THRESHOLD=0.22
```

---

## Entrenamiento manual

```bash
# Windows PowerShell
$env:PYTHONPATH = "src"
python scripts/train_intent_model.py

# Linux/macOS
export PYTHONPATH=src
python scripts/train_intent_model.py
```

Variables útiles: `TF_EPOCHS`, `TF_BATCH_SIZE`, `TF_LEARNING_RATE`, `RETRAIN_INTENTS_ALWAYS`.

### Entrenamiento automático

| Contexto | Script |
|----------|--------|
| Docker build | `scripts/docker-entrypoint.sh` |
| Render build | `scripts/render_build.sh` → `ensure_intent_model.py` |
| Arranque local API | `scripts/run_api.bat` (opcional) |

---

## spaCy

Modelo de lenguaje para limpieza de texto:

```bash
python -m spacy download es_core_news_sm
```

Si no está instalado, el pipeline puede degradar a limpieza básica según configuración.

---

## Relación datos ↔ código

```
intents_dataset.json
       ↓
dataset_builder.py → trainer.py → models/tensorflow/*
       ↓
IntentClassifier.predict()
       ↓
responses.json → ResponseSelector → mensaje al usuario
       ↓
intent_action_executor.py → action_url (opcional)
```
