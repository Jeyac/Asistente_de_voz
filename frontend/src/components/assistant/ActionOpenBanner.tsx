/**
 * Banner con enlace real para abrir sitios tras un comando de voz.
 *
 * Safari/iOS bloquean window.open() asíncrono; el usuario debe tocar este botón.
 */
import { actionLinkLabel } from "../../utils/openExternalUrl";
import { Card } from "../ui/Card";

interface ActionOpenBannerProps {
  url: string;
  intent: string;
  onDismiss: () => void;
}

export function ActionOpenBanner({ url, intent, onDismiss }: ActionOpenBannerProps) {
  const label = actionLinkLabel(intent, url);

  return (
    <Card className="border-emerald-500/30 bg-emerald-500/10">
      <p className="text-sm text-emerald-100">
        En el teléfono debes <strong>tocar el botón</strong> (Safari y Chrome no abren sitios solos tras la voz).
        También hay otro botón verde bajo la respuesta del asistente.
      </p>
      <div className="mt-3 flex flex-wrap gap-2">
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex min-h-[44px] flex-1 items-center justify-center rounded-lg bg-emerald-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-emerald-900/30 transition hover:bg-emerald-500 active:scale-[0.98]"
        >
          {label}
        </a>
        <button
          type="button"
          onClick={onDismiss}
          className="min-h-[44px] rounded-lg border border-slate-600/60 px-3 py-2 text-xs text-slate-400 hover:bg-slate-800/50"
        >
          Cerrar
        </button>
      </div>
    </Card>
  );
}
