/**
 * Componente raíz de la aplicación web del asistente de voz.
 *
 * Combina el asistente (micrófono, texto, respuestas) con el detector
 * de palabra clave y el banner para abrir enlaces en Safari.
 */
import { Header } from "./components/layout/Header";
import { IntentPanel } from "./components/assistant/IntentPanel";
import { MicrophoneButton } from "./components/assistant/MicrophoneButton";
import { ResponsePanel } from "./components/assistant/ResponsePanel";
import { TextInputBar } from "./components/assistant/TextInputBar";
import { TranscriptPanel } from "./components/assistant/TranscriptPanel";
import { ActionOpenBanner } from "./components/assistant/ActionOpenBanner";
import { WakeWordPanel } from "./components/assistant/WakeWordPanel";
import { useOpenWakeWord } from "./hooks/useOpenWakeWord";
import { useVoiceAssistant } from "./hooks/useVoiceAssistant";

export default function App() {
  const assistant = useVoiceAssistant();
  const {
    wakeWordListening,
    wakeWordError,
    wakeWordPhrase,
    wakeWordAvailable,
    wakeWordLastScore,
    wakeWordThreshold,
  } = useOpenWakeWord({
    enabled: assistant.wakeWordEnabled,
    apiOnline: assistant.apiOnline,
    // Liberar el micrófono del wake word mientras se graba el comando.
    micPaused: assistant.isListening || assistant.isProcessing,
    onWakeWord: assistant.handleWakeWordDetected,
  });

  return (
    <div className="mx-auto flex min-h-screen max-w-2xl flex-col gap-8 px-4 py-8 sm:px-6 sm:py-12">
      <Header apiOnline={assistant.apiOnline} />

      <WakeWordPanel
        enabled={assistant.wakeWordEnabled}
        listening={wakeWordListening}
        error={wakeWordError}
        phrase={wakeWordPhrase}
        available={wakeWordAvailable}
        apiOnline={assistant.apiOnline}
        lastScore={wakeWordLastScore}
        threshold={wakeWordThreshold}
        onToggle={assistant.toggleWakeWord}
      />

      <section className="flex flex-col items-center py-4">
        <MicrophoneButton
          isListening={assistant.isListening}
          isProcessing={assistant.isProcessing}
          disabled={!assistant.apiOnline}
          onClick={assistant.toggleMicrophone}
        />
      </section>

      {assistant.error && (
        <div
          role="alert"
          className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200"
        >
          {assistant.error}
        </div>
      )}

      {assistant.actionLink && (
        <ActionOpenBanner
          url={assistant.actionLink.url}
          intent={assistant.actionLink.intent}
          onDismiss={assistant.dismissActionLink}
        />
      )}

      <section className="grid gap-4">
        <TranscriptPanel transcript={assistant.transcript} />
        <IntentPanel intent={assistant.intent} confidence={assistant.confidence} />
        <ResponsePanel
          response={assistant.response}
          voiceEnabled={assistant.voiceEnabled}
          speechSupported={assistant.speechSupported}
          actionLink={assistant.actionLink}
          onToggleVoice={assistant.toggleVoice}
          onReplay={assistant.replayResponse}
        />
      </section>

      <TextInputBar
        disabled={!assistant.apiOnline || assistant.isListening || assistant.isProcessing}
        onSubmit={assistant.sendText}
      />

      <footer className="text-center text-xs text-slate-600">
        Powered by FastAPI · TensorFlow · SpeechRecognition
      </footer>
    </div>
  );
}
