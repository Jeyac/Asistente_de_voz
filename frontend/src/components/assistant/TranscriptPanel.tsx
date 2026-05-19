/**
 * Componente del asistente de voz: TranscriptPanel.
 */
import { Card } from "../ui/Card";

interface TranscriptPanelProps {
  transcript: string;
  placeholder?: string;
}

export function TranscriptPanel({ transcript, placeholder = "Tu voz aparecerá aquí..." }: TranscriptPanelProps) {
  return (
    <Card>
      <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
        Transcripción
      </h3>
      <p className={`min-h-[3rem] text-lg leading-relaxed ${transcript ? "text-slate-100" : "text-slate-500"}`}>
        {transcript || placeholder}
      </p>
    </Card>
  );
}
