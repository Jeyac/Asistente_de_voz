# syntax=docker/dockerfile:1

# -----------------------------------------------------------------------------
# Stage 1: dependencias + entrenamiento del modelo (sin pasos manuales en Render)
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && python -m spacy download es_core_news_sm

COPY data/ ./data/
COPY src/ ./src/
COPY scripts/ ./scripts/

# Entrenar modelo + wake word durante el build (sin pasos manuales en Render)
ENV PYTHONPATH=/app/src \
    APP_ENV=production \
    TF_EPOCHS=120 \
    TF_VALIDATION_SPLIT=0 \
    WAKEWORD_ENABLED=true
RUN python scripts/train_intent_model.py \
    && python scripts/download_wakeword_model.py

# -----------------------------------------------------------------------------
# Stage 2: imagen de producción ligera
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PIP_NO_CACHE_DIR=1 \
    APP_ENV=production \
    DEBUG=false \
    LOG_FORMAT=json \
    LOG_TO_FILE=false

WORKDIR /app

# Runtime: solo librerías de audio necesarias (sin compiladores)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libportaudio2 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --gid app --home-dir /app app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/data ./data
COPY --from=builder /app/models ./models
COPY --from=builder /app/src ./src
COPY --from=builder /app/scripts ./scripts
COPY scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod +x /usr/local/bin/docker-entrypoint.sh \
    && mkdir -p logs \
    && chown -R app:app /app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=600s --retries=5 \
    CMD python -c "import os,urllib.request; p=os.getenv('PORT','8000'); urllib.request.urlopen(f'http://127.0.0.1:{p}/api/v1/health', timeout=5)"

ENTRYPOINT ["docker-entrypoint.sh"]
