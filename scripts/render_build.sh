#!/usr/bin/env bash
# Build en Render (sin Docker): dependencias + entrenamiento + wake word
set -euo pipefail

pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download es_core_news_sm

export PYTHONPATH=src
export RETRAIN_INTENTS_ALWAYS=true
python scripts/ensure_intent_model.py
python scripts/download_wakeword_model.py

echo "Build completado."
