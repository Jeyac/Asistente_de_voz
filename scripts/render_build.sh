#!/usr/bin/env bash
# Build en Render (sin Docker)
set -euo pipefail

echo "=== Instalando dependencias de producción ==="
pip install --upgrade pip
pip install -r requirements-prod.txt

echo "=== openWakeWord (solo ONNX, sin tflite-runtime) ==="
pip install openwakeword==0.6.0 --no-deps

echo "=== Modelo spaCy ==="
python -m spacy download es_core_news_sm

echo "=== Entrenando clasificador de intenciones ==="
export PYTHONPATH=src
export RETRAIN_INTENTS_ALWAYS=true
export TF_EPOCHS="${TF_EPOCHS:-80}"
export TF_VALIDATION_SPLIT="${TF_VALIDATION_SPLIT:-0}"
python scripts/ensure_intent_model.py

echo "=== Modelo wake word hey_jarvis ==="
python scripts/download_wakeword_model.py

echo "=== Build OK ==="
