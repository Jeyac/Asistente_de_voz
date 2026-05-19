/** Síntesis de voz en el navegador (español). */

function loadVoices(): SpeechSynthesisVoice[] {
  return window.speechSynthesis.getVoices();
}

if (typeof window !== "undefined" && "speechSynthesis" in window) {
  loadVoices();
  window.speechSynthesis.addEventListener("voiceschanged", () => {
    loadVoices();
  });
}

function pickSpanishVoice(): SpeechSynthesisVoice | undefined {
  const voices = loadVoices();
  return (
    voices.find((v) => v.lang === "es-ES") ??
    voices.find((v) => v.lang.startsWith("es")) ??
    voices[0]
  );
}

export function isSpeechSynthesisSupported(): boolean {
  return typeof window !== "undefined" && "speechSynthesis" in window;
}

export function speakText(text: string, rate = 1): void {
  if (!text.trim() || !isSpeechSynthesisSupported()) {
    return;
  }

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "es-ES";
  utterance.rate = rate;
  const voice = pickSpanishVoice();
  if (voice) {
    utterance.voice = voice;
  }
  window.speechSynthesis.speak(utterance);
}

export function stopSpeaking(): void {
  if (isSpeechSynthesisSupported()) {
    window.speechSynthesis.cancel();
  }
}

const VOICE_KEY = "asistente-voz-speech-enabled";

export function getVoiceEnabled(): boolean {
  const stored = localStorage.getItem(VOICE_KEY);
  if (stored === null) {
    return true;
  }
  return stored === "true";
}

export function setVoiceEnabled(enabled: boolean): void {
  localStorage.setItem(VOICE_KEY, String(enabled));
}
