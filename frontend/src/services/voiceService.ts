import type { VoiceProcessResult } from "../types/api";
import { apiPostForm, apiPostJson } from "./apiClient";

export async function processVoiceAudio(audioBlob: Blob): Promise<VoiceProcessResult> {
  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.wav");
  return apiPostForm<VoiceProcessResult>("/voice/process-audio", formData);
}

export async function processVoiceText(text: string): Promise<VoiceProcessResult> {
  return apiPostJson<VoiceProcessResult>("/voice/process", { text });
}
