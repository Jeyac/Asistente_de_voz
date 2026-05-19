/**
 * Componente del asistente de voz: MicrophoneButton.
 */
import { ListeningAnimation } from "./ListeningAnimation";
import { Spinner } from "../ui/Spinner";

/** Props del botón central de grabación manual (sin wake word). */
interface MicrophoneButtonProps {
  isListening: boolean;
  isProcessing: boolean;
  disabled?: boolean;
  onClick: () => void;
}

export function MicrophoneButton({
  isListening,
  isProcessing,
  disabled,
  onClick,
}: MicrophoneButtonProps) {
  const label = isProcessing
    ? "Procesando..."
    : isListening
      ? "Toca para enviar"
      : "Toca para hablar";

  return (
    <div className="relative flex flex-col items-center gap-4">
      <ListeningAnimation active={isListening} />
      <button
        type="button"
        onClick={onClick}
        disabled={disabled || isProcessing}
        aria-label={label}
        className={`
          relative z-10 flex h-24 w-24 items-center justify-center rounded-full
          transition-all duration-300 focus:outline-none focus-visible:ring-2
          focus-visible:ring-accent-glow focus-visible:ring-offset-2
          focus-visible:ring-offset-surface disabled:cursor-not-allowed disabled:opacity-50
          ${
            isListening
              ? "scale-105 bg-gradient-to-br from-cyan-500 to-indigo-600 shadow-glow-cyan"
              : "bg-gradient-to-br from-indigo-500 to-violet-600 shadow-glow hover:scale-105"
          }
        `}
      >
        {isProcessing ? <Spinner size="lg" /> : <MicrophoneIcon listening={isListening} />}
      </button>
      <p className="text-sm font-medium text-slate-400">{label}</p>
    </div>
  );
}

function MicrophoneIcon({ listening }: { listening: boolean }) {
  return (
    <svg
      className={`h-10 w-10 text-white ${listening ? "animate-pulse" : ""}`}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={1.8}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 003-3V4.5a3 3 0 10-6 0v8.25a3 3 0 003 3z"
      />
    </svg>
  );
}
