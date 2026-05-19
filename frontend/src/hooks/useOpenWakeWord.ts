import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "../services/apiClient";
import {
  endWakeWordSession,
  fetchActivationConfig,
  scoreWakeWordChunk,
  type ActivationConfig,
} from "../services/activationService";
import { WakeWordMicStream } from "../utils/wakeWordMicStream";

const COOLDOWN_MS = 2500;
/** En Render la red es lenta: no descartar chunks nuevos (openWakeWord necesita secuencia continua). */
const MAX_QUEUE_CHUNKS = 24;

export interface UseOpenWakeWordOptions {
  enabled: boolean;
  apiOnline: boolean;
  onWakeWord: () => void;
}

export function useOpenWakeWord({ enabled, apiOnline, onWakeWord }: UseOpenWakeWordOptions) {
  const [listening, setListening] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [config, setConfig] = useState<ActivationConfig | null>(null);
  const sessionIdRef = useRef(crypto.randomUUID());
  const micRef = useRef<WakeWordMicStream | null>(null);
  const chunkQueueRef = useRef<Int16Array[]>([]);
  const drainingRef = useRef(false);
  const cooldownRef = useRef(false);
  const onWakeWordRef = useRef(onWakeWord);

  useEffect(() => {
    onWakeWordRef.current = onWakeWord;
  }, [onWakeWord]);

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
        const chunk = chunkQueueRef.current.shift();
        if (!chunk) break;
        const pcm = new Uint8Array(chunk.byteLength);
        pcm.set(new Uint8Array(chunk.buffer, chunk.byteOffset, chunk.byteLength));
        const result = await scoreWakeWordChunk(sessionIdRef.current, pcm.buffer);
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
  }, []);

  const enqueueChunk = useCallback(
    (chunk: Int16Array) => {
      if (cooldownRef.current) return;
      chunkQueueRef.current.push(chunk);
      if (chunkQueueRef.current.length > MAX_QUEUE_CHUNKS) {
        chunkQueueRef.current.shift();
      }
      void drainQueue();
    },
    [drainQueue],
  );

  useEffect(() => {
    const canListen = enabled && apiOnline && config?.enabled && config.engine === "openwakeword";

    if (!canListen) {
      setListening(false);
      chunkQueueRef.current = [];
      if (enabled && apiOnline && config && !config.enabled) {
        setError("Activa WAKEWORD_ENABLED=true en el servidor.");
      } else if (enabled && apiOnline && config && config.engine !== "openwakeword") {
        setError("El servidor debe usar WAKEWORD_ENGINE=openwakeword.");
      } else if (!enabled) {
        setError(null);
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
        if (!cancelled) setListening(true);
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
      void mic.stop();
      micRef.current = null;
      void endWakeWordSession(sessionIdRef.current).catch(() => undefined);
      sessionIdRef.current = crypto.randomUUID();
    };
  }, [enabled, apiOnline, config, enqueueChunk]);

  return {
    wakeWordListening: listening,
    wakeWordError: error,
    wakeWordPhrase: config?.phrase ?? "hey jarvis",
    wakeWordAvailable: Boolean(config?.enabled && config.engine === "openwakeword"),
  };
}
