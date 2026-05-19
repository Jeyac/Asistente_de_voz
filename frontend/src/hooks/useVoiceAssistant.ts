import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "../services/apiClient";
import { checkHealth } from "../services/healthService";
import { processVoiceAudio, processVoiceText } from "../services/voiceService";
import type { AssistantStatus, VoiceProcessResult } from "../types/api";
import { AudioRecorder } from "../utils/audioRecorder";
import {
  getVoiceEnabled,
  isSpeechSynthesisSupported,
  setVoiceEnabled,
  speakText,
  stopSpeaking,
} from "../utils/speechSynthesis";

interface AssistantState {
  status: AssistantStatus;
  transcript: string;
  intent: string;
  confidence: number;
  response: string;
  error: string | null;
  apiOnline: boolean;
  voiceEnabled: boolean;
  wakeWordEnabled: boolean;
}

const WAKEWORD_STORAGE_KEY = "asistente-voz-wakeword-enabled";
const COMMAND_AUTO_STOP_MS = 10_000;

function getWakeWordEnabledDefault(): boolean {
  const stored = localStorage.getItem(WAKEWORD_STORAGE_KEY);
  if (stored === null) return false;
  return stored === "true";
}

const initialState: AssistantState = {
  status: "idle",
  transcript: "",
  intent: "",
  confidence: 0,
  response: "",
  error: null,
  apiOnline: false,
  voiceEnabled: getVoiceEnabled(),
  wakeWordEnabled: getWakeWordEnabledDefault(),
};

export function useVoiceAssistant() {
  const [state, setState] = useState<AssistantState>(initialState);
  const recorderRef = useRef<AudioRecorder | null>(null);
  const commandTimerRef = useRef<number | null>(null);
  const voiceEnabledRef = useRef(state.voiceEnabled);
  const statusRef = useRef(state.status);

  useEffect(() => {
    voiceEnabledRef.current = state.voiceEnabled;
  }, [state.voiceEnabled]);

  useEffect(() => {
    statusRef.current = state.status;
  }, [state.status]);

  useEffect(() => {
    checkHealth()
      .then(() => setState((prev) => ({ ...prev, apiOnline: true })))
      .catch(() => setState((prev) => ({ ...prev, apiOnline: false })));
  }, []);

  const speakResponse = useCallback((text: string) => {
    if (voiceEnabledRef.current && text) {
      speakText(text);
    }
  }, []);

  const openActionUrl = useCallback((result: VoiceProcessResult) => {
    if (result.action_url) {
      window.open(result.action_url, "_blank", "noopener,noreferrer");
    }
  }, []);

  const applyResult = useCallback(
    (result: VoiceProcessResult) => {
      setState((prev) => ({
        ...prev,
        status: "success",
        transcript: result.transcript,
        intent: result.intent,
        confidence: result.confidence,
        response: result.response,
        error: null,
      }));
      openActionUrl(result);
      speakResponse(result.response);
    },
    [openActionUrl, speakResponse],
  );

  const setError = useCallback((message: string) => {
    stopSpeaking();
    setState((prev) => ({
      ...prev,
      status: "error",
      error: message,
    }));
  }, []);

  const toggleVoice = useCallback(() => {
    setState((prev) => {
      const next = !prev.voiceEnabled;
      setVoiceEnabled(next);
      if (!next) {
        stopSpeaking();
      }
      return { ...prev, voiceEnabled: next };
    });
  }, []);

  const replayResponse = useCallback(() => {
    if (state.response) {
      speakText(state.response);
    }
  }, [state.response]);

  const startListening = useCallback(async () => {
    stopSpeaking();
    statusRef.current = "listening";
    setState((prev) => ({
      ...prev,
      status: "listening",
      error: null,
      transcript: "",
      intent: "",
      response: "",
    }));
    try {
      recorderRef.current = new AudioRecorder();
      await recorderRef.current.start();
    } catch {
      statusRef.current = "error";
      setError("No se pudo acceder al micrófono. Verifique los permisos del navegador.");
    }
  }, [setError]);

  const clearCommandTimer = useCallback(() => {
    if (commandTimerRef.current !== null) {
      window.clearTimeout(commandTimerRef.current);
      commandTimerRef.current = null;
    }
  }, []);

  const stopListening = useCallback(async () => {
    const recorder = recorderRef.current;
    if (!recorder) return;

    clearCommandTimer();
    setState((prev) => ({ ...prev, status: "processing" }));

    try {
      const wavBlob = await recorder.stop();
      recorderRef.current = null;
      const result = await processVoiceAudio(wavBlob);
      applyResult(result);
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : "Error al procesar el audio";
      setError(message);
    }
  }, [applyResult, setError, clearCommandTimer]);

  const handleWakeWordDetected = useCallback(async () => {
    if (statusRef.current === "listening" || statusRef.current === "processing") {
      return;
    }
    speakText("Te escucho");
    await startListening();
    clearCommandTimer();
    commandTimerRef.current = window.setTimeout(() => {
      if (recorderRef.current) {
        void stopListening();
      }
    }, COMMAND_AUTO_STOP_MS);
  }, [startListening, stopListening, clearCommandTimer]);

  const toggleWakeWord = useCallback(() => {
    setState((prev) => {
      const next = !prev.wakeWordEnabled;
      localStorage.setItem(WAKEWORD_STORAGE_KEY, String(next));
      return { ...prev, wakeWordEnabled: next };
    });
  }, []);

  const toggleMicrophone = useCallback(async () => {
    if (state.status === "listening") {
      await stopListening();
    } else if (state.status === "idle" || state.status === "success" || state.status === "error") {
      await startListening();
    }
  }, [state.status, startListening, stopListening]);

  const sendText = useCallback(
    async (text: string) => {
      stopSpeaking();
      setState((prev) => ({ ...prev, status: "processing", error: null }));
      try {
        const result = await processVoiceText(text);
        applyResult(result);
      } catch (err) {
        const message = err instanceof ApiError ? err.message : "Error al procesar el texto";
        setError(message);
      }
    },
    [applyResult, setError],
  );

  const reset = useCallback(() => {
    stopSpeaking();
    recorderRef.current = null;
    setState((prev) => ({
      ...initialState,
      apiOnline: prev.apiOnline,
      voiceEnabled: prev.voiceEnabled,
      wakeWordEnabled: prev.wakeWordEnabled,
    }));
  }, []);

  return {
    ...state,
    toggleMicrophone,
    sendText,
    reset,
    toggleVoice,
    toggleWakeWord,
    replayResponse,
    handleWakeWordDetected,
    speechSupported: isSpeechSynthesisSupported(),
    isListening: state.status === "listening",
    isProcessing: state.status === "processing",
  };
}
