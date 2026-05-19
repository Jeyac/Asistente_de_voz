import { Card } from "../ui/Card";

interface ResponsePanelProps {
  response: string;
  voiceEnabled: boolean;
  speechSupported: boolean;
  onToggleVoice: () => void;
  onReplay: () => void;
}

export function ResponsePanel({
  response,
  voiceEnabled,
  speechSupported,
  onToggleVoice,
  onReplay,
}: ResponsePanelProps) {
  return (
    <Card className="border-indigo-500/20 bg-gradient-to-br from-indigo-500/10 to-cyan-500/5">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-indigo-300/80">
          Respuesta del asistente
        </h3>
        {speechSupported && (
          <div className="flex gap-2">
            <button
              type="button"
              onClick={onToggleVoice}
              className={`rounded-lg px-2 py-1 text-xs font-medium transition ${
                voiceEnabled
                  ? "bg-indigo-500/30 text-indigo-100"
                  : "bg-slate-700/50 text-slate-400"
              }`}
            >
              {voiceEnabled ? "Voz ON" : "Voz OFF"}
            </button>
            {response && (
              <button
                type="button"
                onClick={onReplay}
                className="rounded-lg bg-slate-700/50 px-2 py-1 text-xs text-slate-300 hover:bg-slate-600/50"
              >
                Repetir
              </button>
            )}
          </div>
        )}
      </div>
      <p className={`min-h-[3rem] text-lg leading-relaxed ${response ? "text-slate-100" : "text-slate-500"}`}>
        {response || "La respuesta aparecerá aquí..."}
      </p>
    </Card>
  );
}
