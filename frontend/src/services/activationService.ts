import { apiDelete, apiGet, apiPostBinary } from "./apiClient";

export interface ActivationConfig {
  enabled: boolean;
  phrase: string;
  engine: string;
  threshold: number;
  listen_timeout: number;
}

export interface WakeWordChunkScore {
  score: number;
  activated: boolean;
  phrase: string;
  threshold: number;
}

export function fetchActivationConfig(): Promise<ActivationConfig> {
  return apiGet<ActivationConfig>("/activation/config");
}

export function scoreWakeWordChunk(
  sessionId: string,
  pcmChunk: ArrayBuffer,
): Promise<WakeWordChunkScore> {
  return apiPostBinary<WakeWordChunkScore>("/activation/score-chunk", pcmChunk, {
    "X-Wake-Session": sessionId,
  });
}

/** Varios fragmentos de 2560 bytes concatenados (menos viajes HTTP en producción). */
export function scoreWakeWordChunks(
  sessionId: string,
  pcmBatch: ArrayBuffer,
): Promise<WakeWordChunkScore> {
  return apiPostBinary<WakeWordChunkScore>("/activation/score-chunks", pcmBatch, {
    "X-Wake-Session": sessionId,
  });
}

export function endWakeWordSession(sessionId: string): Promise<void> {
  return apiDelete("/activation/session", { "X-Wake-Session": sessionId });
}
