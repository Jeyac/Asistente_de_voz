/**
 * Cliente HTTP para el módulo de voz de la API.
 */
import type { VoiceProcessResult } from "../types/api";
import { apiPostForm, apiPostJson } from "./apiClient";

/** Envía WAV grabado en el navegador → transcripción + intención + respuesta. */
export async function processVoiceAudio(audioBlob: Blob): Promise<VoiceProcessResult> {
  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.wav");
  return apiPostForm<VoiceProcessResult>("/voice/process-audio", formData);
}

/** Envía texto directamente (sin pasar por reconocimiento de voz). */
export async function processVoiceText(text: string): Promise<VoiceProcessResult> {
  return apiPostJson<VoiceProcessResult>("/voice/process", { text });
}
