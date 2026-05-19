/**
 * Componente del asistente de voz: IntentPanel.
 */
import { Badge } from "../ui/Badge";
import { Card } from "../ui/Card";

interface IntentPanelProps {
  intent: string;
  confidence: number;
}

/** Muestra la intención clasificada por TensorFlow (p. ej. abrir_youtube). */
export function IntentPanel({ intent, confidence }: IntentPanelProps) {
  const hasIntent = Boolean(intent);

  return (
    <Card>
      <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
        Intención detectada
      </h3>
      {hasIntent ? (
        <div className="flex flex-wrap items-center gap-3">
          <Badge variant="accent">{intent}</Badge>
          <span className="text-sm text-slate-400">
            Confianza: <span className="font-mono text-cyan-300">{(confidence * 100).toFixed(1)}%</span>
          </span>
        </div>
      ) : (
        <p className="text-slate-500">Esperando comando...</p>
      )}
    </Card>
  );
}
