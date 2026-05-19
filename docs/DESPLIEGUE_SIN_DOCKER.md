# Despliegue en Render sin Docker (paso a paso)

Guía para subir el proyecto a **GitHub** y publicarlo en **Render** (API Python + frontend estático).

---

## Parte 1: Preparar el proyecto en tu PC

### 1.1 No subas secretos

Estos archivos **no** deben ir a GitHub (ya están en `.gitignore`):

- `.env`
- `.venv` / `venv`
- `logs/`
- `frontend/node_modules/`

### 1.2 (Opcional) Probar que el repo está listo

```powershell
cd "C:\Users\50256\Desktop\Asistente de voz"
git status
```

Si dice que no es un repositorio git, sigue el **Parte 2**.

---

## Parte 2: Subir a GitHub

### 2.1 Crear cuenta y repositorio en GitHub

1. Entra en https://github.com e inicia sesión.
2. Clic en **+** → **New repository**.
3. Nombre ejemplo: `asistente-de-voz`.
4. **Public** o **Private** (como prefieras).
5. **No** marques “Add a README” si ya tienes código local.
6. Clic en **Create repository**.

GitHub te mostrará comandos; usa los de abajo adaptados a tu URL.

### 2.2 Inicializar Git en tu carpeta (solo la primera vez)

Abre PowerShell en la carpeta del proyecto:

```powershell
cd "C:\Users\50256\Desktop\Asistente de voz"
git init
git branch -M main
```

### 2.3 Primer commit

```powershell
git add .
git status
```

Revisa que **no** aparezca `.env` en la lista. Si aparece, no lo subas:

```powershell
git reset HEAD .env
```

Commit:

```powershell
git commit -m "Asistente de voz: API, frontend y despliegue Render sin Docker"
```

### 2.4 Conectar con GitHub y subir

Sustituye `TU_USUARIO` y `TU_REPO` por los tuyos:

```powershell
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

Te pedirá login de GitHub (navegador o token).

### 2.5 Cambios posteriores

Cada vez que modifiques código:

```powershell
git add .
git commit -m "Describe el cambio"
git push
```

Render puede redesplegar solo si activaste auto-deploy.

---

## Parte 3: Desplegar en Render

### 3.1 Cuenta Render

1. https://render.com → **Get Started** (puedes entrar con GitHub).
2. Autoriza acceso a tus repositorios.

### 3.2 Crear servicios con Blueprint

1. **Dashboard** → **New** → **Blueprint**.
2. Conecta el repositorio `asistente-de-voz` (o el nombre que uses).
3. Render lee `render.yaml` y propone **2 servicios**:
   - `asistente-voz-api` (Python)
   - `asistente-voz-web` (sitio estático)
4. Clic en **Apply**.

El **primer deploy de la API** puede tardar **15–25 minutos** (instala TensorFlow, entrena el modelo, descarga wake word).

### 3.3 Variables que debes configurar a mano

Cuando termine el primer deploy, entra a cada servicio:

#### API → Environment

| Variable | Valor |
|----------|--------|
| `CORS_ORIGINS` | URL del frontend, ej. `https://asistente-voz-web.onrender.com` |

(Sin barra final. Si usas varias URLs, sepáralas con coma.)

#### Frontend → Environment

| Variable | Valor |
|----------|--------|
| `VITE_API_BASE_URL` | URL de la API + `/api/v1`, ej. `https://asistente-voz-api.onrender.com/api/v1` |

Guarda y pulsa **Manual Deploy** → **Deploy latest commit** en el **frontend** (para que el build use la URL correcta).

### 3.4 Comprobar

1. Abre `https://TU-API.onrender.com/api/v1/health` → debe responder JSON con `"status":"ok"` o similar.
2. Abre la URL del frontend.
3. Prueba texto: «últimas noticias», «qué hora es», etc.

---

## Parte 4: Qué hace Render en el build (sin Docker)

El archivo `scripts/render_build.sh`:

1. `pip install -r requirements.txt`
2. Descarga modelo spaCy español
3. **Reentrena** el modelo con `data/intents/intents_dataset.json`
4. Descarga modelo wake word `hey_jarvis`

El arranque usa `scripts/render_start.sh` → uvicorn en el puerto que Render asigna.

---

## Parte 5: Plan free – cosas a tener en cuenta

| Tema | Detalle |
|------|---------|
| **Cold start** | Tras ~15 min sin uso, la primera petición tarda ~30–60 s |
| **Build lento** | Normal en el primer deploy |
| **Micrófono en servidor** | No hay mic en Render; usa el **navegador** (botón o wake word) |
| **Wake word** | Funciona: el micrófono es del cliente, la API analiza fragmentos |

---

## Resumen rápido

```text
1. git init → git add . → git commit → git push (GitHub)
2. Render → Blueprint → repo → Apply
3. CORS_ORIGINS en API = URL del frontend
4. VITE_API_BASE_URL en web = URL API + /api/v1
5. Redesplegar frontend
```

---

## Si el deploy falló (Blueprint)

Causas corregidas en el repo:

1. **PyAudio** no compila en Render → la API usa `requirements-prod.txt` (sin PyAudio).
2. **Scripts `.sh` con saltos Windows** → archivo `.gitattributes` fuerza LF.
3. **Frontend** → `rootDir: frontend` en `render.yaml`.

**Qué hacer ahora:**

```powershell
git add .
git commit -m "Fix deploy Render: requirements-prod, rootDir frontend"
git push
```

En Render: **Blueprint** → **Manual sync** o borra los servicios fallidos y vuelve a **Apply**.

Revisa **Logs** del build en cada servicio si vuelve a fallar.

## Si el build de la API falla

- Revisa **Logs** del servicio API en Render.
- Causas habituales: timeout (plan free), memoria insuficiente.
- Solución: **Manual Deploy** o bajar `TF_EPOCHS` a `50` en Environment.

## Archivos de esta modalidad

| Archivo | Función |
|---------|---------|
| `render.yaml` | `runtime: python` (no Docker) |
| `runtime.txt` | Python 3.12 en Render |
| `scripts/render_build.sh` | Instalar + entrenar |
| `scripts/render_start.sh` | Arrancar uvicorn |
