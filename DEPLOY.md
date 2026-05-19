# Despliegue con Docker y Render

## Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y en ejecución
- Cuenta en [Render](https://render.com) (para producción)
- Repositorio en GitHub

---

## Uso de Docker en tu PC

### 1. Preparar variables (solo la primera vez)

```powershell
cd "C:\Users\50256\Desktop\Asistente de voz"
copy .env.production.example .env.production
```

Opcional: edita `.env.production` si necesitas cambiar nombres del creador, etc.

### 2. Construir la imagen

```powershell
docker compose build
```

La primera vez tarda **15–25 minutos** (instala TensorFlow, entrena el modelo con **todas** las intenciones del JSON y descarga el wake word).

### 3. Arrancar la API

```powershell
docker compose up
```

En cada arranque el contenedor **vuelve a entrenar** el modelo (`RETRAIN_INTENTS_ALWAYS=true`) y luego inicia la API.

- Salud: http://localhost:8000/api/v1/health  
- Docs (si las activas en `.env.production`): http://localhost:8000/docs  

### 4. Frontend en local (otra terminal)

```powershell
cd frontend
npm install
```

Crea `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

```powershell
npm run dev
```

Abre http://localhost:5173

### 5. Comandos útiles

| Comando | Qué hace |
|---------|----------|
| `docker compose up -d` | API en segundo plano |
| `docker compose down` | Detener |
| `docker compose build --no-cache` | Reconstruir desde cero |
| `docker compose logs -f api` | Ver logs |

### 6. Desarrollo sin Docker (solo Python)

Si tienes TensorFlow instalado en Python 3.12:

```powershell
.\scripts\run_api.bat
```

Ese script **reentrena siempre** y luego arranca uvicorn.

---

## Subir a Render

### Paso 1: Push del código

```bash
git add .
git commit -m "Listo para Render con Docker"
git push origin main
```

### Paso 2: Blueprint

1. Render → **New** → **Blueprint**
2. Conecta el repositorio
3. Usa el `render.yaml` del proyecto (crea API Docker + sitio estático)

### Paso 3: Variables tras el primer deploy

**API** (`asistente-voz-api`):

| Variable | Valor |
|----------|--------|
| `CORS_ORIGINS` | `https://TU-FRONTEND.onrender.com` |

**Frontend** (`asistente-voz-web`):

| Variable | Valor |
|----------|--------|
| `VITE_API_BASE_URL` | `https://TU-API.onrender.com/api/v1` |

Redespliega el **frontend** después de guardar.

### Paso 4: Comprobar

```bash
curl https://TU-API.onrender.com/api/v1/health
```

El primer arranque en plan free puede tardar **varios minutos** (entrenamiento + wake word).

---

## Qué incluye el entrenamiento automático

| Momento | Acción |
|---------|--------|
| `docker compose build` | Entrena en la fase de build |
| Cada `docker compose up` | Reentrena con `ensure_intent_model.py` |
| Cada deploy en Render | Igual al arrancar el contenedor |
| `scripts\run_api.bat` | Reentrena en local antes de uvicorn |

El dataset es `data/intents/intents_dataset.json` (19 intenciones: deportes, noticias, historia, tecnología, etc.).

Tras entrenar, `models/tensorflow/labels.json` tendrá **todas** las etiquetas.

---

## Solución de problemas

| Problema | Solución |
|----------|----------|
| Build: sin espacio en disco | Libera ~5 GB; `docker system prune -a` |
| Health check falla al inicio | Normal; espera hasta 10 min (entrenamiento) |
| CORS | `CORS_ORIGINS` = URL exacta del frontend (https) |
| Frontend sin respuestas nuevas | Rebuild API; verifica `labels.json` con 19 intenciones |
| Wake word 503 en local sin Docker | Usa Docker o `py -3.12` + `pip install openwakeword` |

---

## Archivos clave

| Archivo | Uso |
|---------|-----|
| `Dockerfile` | Imagen multi-stage |
| `docker-compose.yml` | Local |
| `render.yaml` | Render Blueprint |
| `scripts/docker-entrypoint.sh` | Reentrena + arranca API |
| `scripts/ensure_intent_model.py` | Lógica de reentrenamiento |
