# Acciones del navegador (abrir YouTube, Google, etc.)

Cómo el asistente abre sitios web y por qué en **Safari / móvil** a veces hay que tocar un botón.

---

## Flujo completo

1. Usuario: «abre youtube».
2. API clasifica → `intent: abrir_youtube`.
3. `IntentActionExecutor` resuelve URL: `https://www.youtube.com`.
4. Respuesta JSON incluye `action_url` y `action_performed: true`.
5. Frontend intenta abrir el enlace.

---

## Backend: `intent_action_executor.py`

No abre el navegador en el servidor. Solo devuelve la URL al cliente.

| Intención | URL por defecto |
|-----------|-----------------|
| `abrir_youtube` | https://www.youtube.com |
| `abrir_google` | https://www.google.com |
| `musica` | https://music.youtube.com |
| `clima` | Búsqueda Google «clima» |
| `deportes`, `noticias`, … | Búsqueda temática en Google |
| `buscar_web` | Google o query extraída del transcript |

Requiere `ENABLE_SYSTEM_ACTIONS=true`.

Intenciones **sin URL**: `saludo`, `hora`, `despedida`, `creador`, `relacion_creador`.

---

## Frontend: apertura del enlace

### Escritorio (Chrome, Firefox, Edge)

`tryOpenExternalUrl()` usa `window.open(url, "_blank")` — suele funcionar tras la respuesta de la API.

### Safari / iPhone / iPad

Safari **bloquea ventanas emergentes** que no siguen a un toque directo del usuario. La voz → API → `window.open` **no cuenta** como gesto del usuario.

**Solución implementada:**

1. Botón verde **dentro del panel de respuesta** (`ResponsePanel`) — enlace `<a>` real.
2. Banner `ActionOpenBanner` arriba (mismo enlace, por si no se ve el panel).
3. En **móvil** (`isMobileBrowser`) nunca se usa `window.open` automático.
4. El usuario **toca** «Abrir YouTube» y el navegador abre la URL.

Archivos:

- `utils/openExternalUrl.ts` — detección Safari/iOS
- `components/assistant/ActionOpenBanner.tsx` — botón verde
- `hooks/useVoiceAssistant.ts` — `pendingActionUrl`

### Android Chrome

Comportamiento intermedio: a veces abre solo; si no, aparece el mismo banner.

---

## Cómo verificar que el comando funcionó

En la pantalla del asistente:

1. **Transcripción** — debe decir algo como «abre youtube».
2. **Intención** — debe ser `abrir_youtube` (no `desconocido`).
3. **Respuesta** — «Abriendo YouTube» o similar.
4. **Banner verde** — en móvil/Safari; tócalo para abrir.

Si la intención es `desconocido`, el problema es **reconocimiento de voz o ML**, no Safari.

---

## No abre la «app» nativa de YouTube

El asistente abre una **URL HTTPS**. iOS puede ofrecer abrir en la app de YouTube al tocar el enlace; no hay control directo desde la web sin esquemas `youtube://` (no implementados por compatibilidad).

---

## Desactivar acciones

```env
ENABLE_SYSTEM_ACTIONS=false
```

La API responderá sin `action_url`.
