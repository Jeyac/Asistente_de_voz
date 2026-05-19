/** Abrir enlaces tras comandos de voz (Safari iOS bloquea ventanas emergentes asíncronas). */

export function isMobileBrowser(): boolean {
  return /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
}

/** Safari (sobre todo en iPhone) exige un toque del usuario para abrir pestañas nuevas. */
export function requiresTapToOpenLink(): boolean {
  const ua = navigator.userAgent;
  const isIOS =
    /iPhone|iPad|iPod/i.test(ua) ||
    (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  return isIOS || /Safari/i.test(ua);
}

/**
 * En móvil siempre hay que mostrar un enlace tocable (Chrome y Safari bloquean
 * window.open tras una petición async de voz).
 */
export function shouldShowOpenLinkButton(): boolean {
  return isMobileBrowser() || requiresTapToOpenLink();
}

/**
 * Intenta abrir en pestaña nueva. Devuelve false si el navegador suele bloquearlo
 * (p. ej. Safari tras una respuesta async de la API).
 */
export function tryOpenExternalUrl(url: string): boolean {
  if (requiresTapToOpenLink()) {
    return false;
  }
  try {
    const popup = window.open(url, "_blank", "noopener,noreferrer");
    if (popup) {
      popup.opener = null;
      return true;
    }
  } catch {
    /* ignorar */
  }
  try {
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.target = "_blank";
    anchor.rel = "noopener noreferrer";
    anchor.style.display = "none";
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
    return true;
  } catch {
    return false;
  }
}

export function actionLinkLabel(intent: string, url: string): string {
  const byIntent: Record<string, string> = {
    abrir_youtube: "Abrir YouTube",
    abrir_google: "Abrir Google",
    musica: "Abrir YouTube Music",
    clima: "Ver clima",
    buscar_web: "Buscar en la web",
    deportes: "Buscar deportes",
    noticias: "Abrir noticias",
    historia: "Buscar historia",
    tecnologia: "Buscar tecnología",
    ciencia: "Buscar ciencia",
    cultura: "Buscar cultura",
    entretenimiento: "Abrir entretenimiento",
    salud: "Buscar salud",
    viajes: "Buscar viajes",
  };
  if (intent in byIntent) {
    return byIntent[intent];
  }
  try {
    const host = new URL(url).hostname.replace(/^www\./, "");
    return `Abrir ${host}`;
  } catch {
    return "Abrir enlace";
  }
}
