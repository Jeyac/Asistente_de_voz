#!/bin/sh
set -eu

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
WORKERS="${WORKERS:-1}"
LOG_LEVEL="${LOG_LEVEL:-info}"

echo "=== Reentrenando modelo de intenciones (dataset actual) ==="
export RETRAIN_INTENTS_ALWAYS=true
python scripts/ensure_intent_model.py

if [ ! -f "models/wakeword/hey_jarvis_v0.1.onnx" ]; then
  echo "=== Descargando modelo wake word ==="
  python scripts/download_wakeword_model.py
fi

echo "=== Iniciando API | host=${HOST} port=${PORT} workers=${WORKERS} ==="
exec uvicorn asistente_voz.main:app \
    --host "${HOST}" \
    --port "${PORT}" \
    --workers "${WORKERS}" \
    --proxy-headers \
    --forwarded-allow-ips="*" \
    --log-level "${LOG_LEVEL}"
