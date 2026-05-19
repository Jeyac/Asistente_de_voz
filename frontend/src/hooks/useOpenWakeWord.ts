import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "../services/apiClient";
import {
  endWakeWordSession,
  fetchActivationConfig,
  scoreWakeWordChunk,
  scoreWakeWordChunks,
  type ActivationConfig,
  type WakeWordChunkScore,
} from "../services/activationService";
import { WAKE_CHUNK_SAMPLES, WakeWordMicStream } from "../utils/wakeWordMicStream";

const COOLDOWN_MS = 2500;
const CHUNKS_PER_BATCH = 4;
const MAX_QUEUE_CHUNKS = 32;
const FLUSH_INTERVAL_MS = 280;

export interface UseOpenWakeWordOptions {
  enabled: boolean;
  apiOnline: boolean;
  /** Pausar micrófono wake word mientras se graba el comando (evita conflicto en móvil). */
  micPaused: boolean;
  onWakeWord: () => void;
}

function concatChunks(chunks: Int16Array[]): ArrayBuffer {
  const bytesPerChunk = WAKE_CHUNK_SAMPLES * 2;
  const merged = new Uint8Array(chunks.length * bytesPerChunk);
  chunks.forEach((chunk, index) => {
    const view = new Uint8Array(chunk.buffer, chunk.byteOffset, chunk.byteLength);
    merged.set(view, index * bytesPerChunk);
  });
  return merged.buffer;
}

export function useOpenWakeWord({
  enabled,
  apiOnline,
  micPaused,
  onWakeWord,
}: UseOpenWakeWordOptions) {
  const [listening, setListening] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastScore, setLastScore] = useState<number | null>(null);
  const [config, setConfig] = useState<ActivationConfig | null>(null);
  const sessionIdRef = useRef(crypto.randomUUID());
  const micRef = useRef<WakeWordMicStream | null>(null);
  const chunkQueueRef = useRef<Int16Array[]>([]);
  const drainingRef = useRef(false);
  const cooldownRef = useRef(false);
  const onWakeWordRef = useRef(onWakeWord);
  const flushTimerRef = useRef<number | null>(null);
  const useLegacyChunksRef = useRef(false);

  useEffect(() => {
    onWakeWordRef.current = onWakeWord;
  }, [onWakeWord]);

  const scoreBatch = useCallback(
    async (sessionId: string, batch: Int16Array[]): Promise<WakeWordChunkScore> => {
      if (!useLegacyChunksRef.current) {
        try {
          return await scoreWakeWordChunks(sessionId, concatChunks(batch));
        } catch (err) {
          if (err instanceof ApiError && err.status === 404) {
            useLegacyChunksRef.current = true;
          } else {
            throw err;
          }
        }
      }
      let maxScore = 0;
      let activated = false;
      let last: WakeWordChunkScore | null = null;
      for (const chunk of batch) {
        const pcm = new Uint8Array(chunk.byteLength);
        pcm.set(new Uint8Array(chunk.buffer, chunk.byteOffset, chunk.byteLength));
        last = await scoreWakeWordChunk(sessionId, pcm.buffer);
        maxScore = Math.max(maxScore, last.score);
        if (last.activated) {
          activated = true;
          return { ...last, score: maxScore, activated: true };
        }
      }
      if (!last) {
        throw new Error("Lote de audio vacío");
      }
      return { ...last, score: maxScore, activated };
    },
    [],
  );

  useEffect(() => {
    if (!apiOnline) {
      setConfig(null);
      return;
    }
    fetchActivationConfig()
      .then(setConfig)
      .catch(() => setConfig(null));
  }, [apiOnline]);

  const drainQueue = useCallback(async () => {
    if (drainingRef.current || cooldownRef.current) return;
    drainingRef.current = true;
    try {
      while (chunkQueueRef.current.length > 0 && !cooldownRef.current) {
        const take = Math.min(CHUNKS_PER_BATCH, chunkQueueRef.current.length);
        const batch = chunkQueueRef.current.splice(0, take);
        if (batch.length === 0) break;

        const result = await scoreBatch(sessionIdRef.current, batch);
        setLastScore(result.score);

        if (result.activated) {
          cooldownRef.current = true;
          chunkQueueRef.current = [];
          onWakeWordRef.current();
          window.setTimeout(() => {
            cooldownRef.current = false;
          }, COOLDOWN_MS);
          break;
        }

      }
    } catch (err) {
      let message = "No se pudo analizar el audio. Reinicia la API y vuelve a activar Wake word.";
      if (err instanceof ApiError) {
        message = err.message;
        const install = (err.body?.details as { install?: string } | undefined)?.install;
        if (install) message += ` Ejecuta: ${install}`;
        if (err.status === 503 && err.message.includes("openWakeWord")) {
          message =
            "openWakeWord no está en el Python de la API. Usa: scripts\\run_api.bat (Python 3.12) o pip install -r requirements.txt";
        }
      }
      setError(message);
      chunkQueueRef.current = [];
    } finally {
      drainingRef.current = false;
      if (chunkQueueRef.current.length > 0 && !cooldownRef.current) {
        void drainQueue();
      }
    }
  }, [scoreBatch]);

  const enqueueChunk = useCallback(
    (chunk: Int16Array) => {
      if (cooldownRef.current) return;
      chunkQueueRef.current.push(chunk);
      if (chunkQueueRef.current.length > MAX_QUEUE_CHUNKS) {
        chunkQueueRef.current.shift();
      }
      if (chunkQueueRef.current.length >= CHUNKS_PER_BATCH) {
        void drainQueue();
      }
    },
    [drainQueue],
  );

  const clearFlushTimer = useCallback(() => {
    if (flushTimerRef.current !== null) {
      window.clearInterval(flushTimerRef.current);
      flushTimerRef.current = null;
    }
  }, []);

  useEffect(() => {
    const canListen =
      enabled && apiOnline && !micPaused && config?.enabled && config.engine === "openwakeword";

    if (!canListen) {
      setListening(false);
      chunkQueueRef.current = [];
      clearFlushTimer();
      if (micRef.current) {
        void micRef.current.stop();
        micRef.current = null;
      }
      if (enabled && apiOnline && config && !config.enabled) {
        setError("Activa WAKEWORD_ENABLED=true en el servidor.");
      } else if (enabled && apiOnline && config && config.engine !== "openwakeword") {
        setError("El servidor debe usar WAKEWORD_ENGINE=openwakeword.");
      } else if (!enabled) {
        setError(null);
        setLastScore(null);
      }
      return undefined;
    }

    setError(null);
    let cancelled = false;
    const mic = new WakeWordMicStream();
    micRef.current = mic;

    const start = async () => {
      try {
        await mic.start((chunk) => {
          if (!cancelled) enqueueChunk(chunk);
        });
        if (!cancelled) {
          setListening(true);
          flushTimerRef.current = window.setInterval(() => {
            if (chunkQueueRef.current.length > 0 && !drainingRef.current) {
              void drainQueue();
            }
          }, FLUSH_INTERVAL_MS);
        }
      } catch {
        if (!cancelled) {
          setError("No se pudo acceder al micrófono. Verifique los permisos del navegador.");
          setListening(false);
        }
      }
    };

    void start();

    return () => {
      cancelled = true;
      setListening(false);
      chunkQueueRef.current = [];
      clearFlushTimer();
      void mic.stop();
      micRef.current = null;
      void endWakeWordSession(sessionIdRef.current).catch(() => undefined);
      sessionIdRef.current = crypto.randomUUID();
    };
  }, [enabled, apiOnline, micPaused, config, enqueueChunk, drainQueue, clearFlushTimer]);

  return {
    wakeWordListening: listening,
    wakeWordError: error,
    wakeWordPhrase: config?.phrase ?? "hey jarvis",
    wakeWordAvailable: Boolean(config?.enabled && config.engine === "openwakeword"),
    wakeWordLastScore: lastScore,
    wakeWordThreshold: config?.threshold ?? null,
  };
}
