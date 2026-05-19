import { Card } from "../ui/Card";

interface WakeWordPanelProps {
  enabled: boolean;
  listening: boolean;
  error: string | null;
  phrase: string;
  available: boolean;
  apiOnline: boolean;
  onToggle: () => void;
}

export function WakeWordPanel({
  enabled,
  listening,
  error,
  phrase,
  available,
  apiOnline,
  onToggle,
}: WakeWordPanelProps) {
  const displayPhrase = phrase.trim() || "hey jarvis";

  return (
    <Card className="border-cyan-500/20 bg-cyan-500/5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-cyan-300/90">
            Palabra clave · {displayPhrase}
          </h3>
          <p className="mt-1 text-sm text-slate-400">
            {listening
              ? `Escuchando… di «${displayPhrase}» y luego tu comando.`
              : enabled
                ? "Iniciando detector (openWakeWord en el servidor)…"
                : "Activa para hablar sin pulsar el botón."}
          </p>
        </div>
        <button
          type="button"
          onClick={onToggle}
          disabled={!apiOnline}
          className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${
            enabled
              ? "bg-cyan-500/30 text-cyan-100"
              : "bg-slate-700/60 text-slate-300 hover:bg-slate-600/60"
          } disabled:cursor-not-allowed disabled:opacity-50`}
        >
          {enabled ? "Wake word ON" : "Wake word OFF"}
        </button>
      </div>
      {error && <p className="mt-2 text-xs text-amber-300/90">{error}</p>}
      {apiOnline && !available && !error && (
        <p className="mt-2 text-xs text-slate-500">
          En el servidor: <code className="text-slate-300">WAKEWORD_ENABLED=true</code> y modelo{" "}
          <code className="text-slate-300">hey_jarvis_v0.1.onnx</code>.
        </p>
      )}
    </Card>
  );
}
