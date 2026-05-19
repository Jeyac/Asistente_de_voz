# Scripts del proyecto (`scripts/`)

Utilidades de entrenamiento, despliegue y desarrollo local.

---

## Entrenamiento y modelos

| Script | Uso |
|--------|-----|
| `train_intent_model.py` | Entrena el clasificador TensorFlow desde `data/intents/intents_dataset.json` |
| `ensure_intent_model.py` | Comprueba si hay que reentrenar; usado en build Render/Docker |
| `download_wakeword_model.py` | Descarga `hey_jarvis_v0.1.onnx` a `models/wakeword/` |
| `train_wakeword_placeholder.py` | Documentación para entrenar modelos custom openWakeWord |

**Ejemplos:**

```bash
$env:PYTHONPATH = "src"
python scripts/train_intent_model.py
python scripts/download_wakeword_model.py
```

---

## Arranque local de la API

| Script | Plataforma | Descripción |
|--------|------------|-------------|
| `run_api.bat` | Windows | Activa venv, `PYTHONPATH=src`, reentrena si hace falta, uvicorn |
| `run_api.ps1` | Windows PowerShell | Variante PowerShell |
| `install_deps.ps1` | Windows | Instalación de dependencias |

---

## Render (sin Docker)

| Script | Cuándo se ejecuta |
|--------|-------------------|
| `render_build.sh` | Build en Render: pip, spaCy, openWakeWord, entrenamiento ML, download wake word |
| `render_start.sh` | Start: `uvicorn` con `PYTHONPATH=src` |

Definidos en `render.yaml`:

```yaml
buildCommand: bash scripts/render_build.sh
startCommand: bash scripts/render_start.sh
```

**Nota:** Los `.sh` deben tener finales de línea LF (`.gitattributes`).

---

## Docker

| Script | Uso |
|--------|-----|
| `docker-entrypoint.sh` | Entrada del contenedor: entrenar si falta modelo, arrancar uvicorn |

---

## Documentación en español del código

| Script | Uso |
|--------|-----|
| `annotate_spanish_docstrings.py` | Añade docstrings en español a todos los `.py` de `src/asistente_voz/` |
| `annotate_frontend_spanish.py` | Añade bloque JSDoc en español a archivos del frontend sin cabecera |

```bash
python scripts/annotate_spanish_docstrings.py
python scripts/annotate_frontend_spanish.py
```

## Pruebas y utilidades

| Script | Uso |
|--------|-----|
| `test_score_chunk.py` | Prueba local de `POST /activation/score-chunk` |

---

## Orden recomendado en máquina nueva

```bash
python -m venv .venv
# activar venv
pip install -r requirements.txt
python -m spacy download es_core_news_sm
copy .env.example .env
python scripts/download_wakeword_model.py
python scripts/train_intent_model.py
# API
$env:PYTHONPATH = "src"
uvicorn asistente_voz.main:app --reload
# Frontend
cd frontend && npm install && npm run dev
```
