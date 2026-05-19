#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH=src
exec uvicorn asistente_voz.main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}" \
  --proxy-headers \
  --forwarded-allow-ips="*"
