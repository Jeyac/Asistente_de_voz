/**
 * Componente de layout: Header.
 */
import { Badge } from "../ui/Badge";

interface HeaderProps {
  apiOnline: boolean;
}

export function Header({ apiOnline }: HeaderProps) {
  return (
    <header className="flex flex-col items-center gap-3 text-center sm:flex-row sm:justify-between sm:text-left">
      <div>
        <h1 className="font-display text-2xl font-bold tracking-tight text-gradient sm:text-3xl">
          Asistente de Voz
        </h1>
        <p className="mt-1 text-sm text-slate-400">Inteligencia artificial conversacional</p>
      </div>
      <Badge variant={apiOnline ? "success" : "warning"}>
        {apiOnline ? "API conectada" : "API desconectada"}
      </Badge>
    </header>
  );
}
