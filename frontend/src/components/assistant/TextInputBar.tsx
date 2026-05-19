import { FormEvent, useState } from "react";

interface TextInputBarProps {
  disabled?: boolean;
  onSubmit: (text: string) => void;
}

export function TextInputBar({ disabled, onSubmit }: TextInputBarProps) {
  const [text, setText] = useState("");

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    const trimmed = text.trim();
    if (!trimmed) return;
    onSubmit(trimmed);
    setText("");
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={disabled}
        placeholder="O escribe un comando..."
        className="flex-1 rounded-xl border border-white/10 bg-surface-overlay px-4 py-3 text-sm text-slate-100 placeholder:text-slate-500 focus:border-accent/50 focus:outline-none focus:ring-1 focus:ring-accent/30 disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={disabled || !text.trim()}
        className="rounded-xl bg-indigo-600 px-5 py-3 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-40"
      >
        Enviar
      </button>
    </form>
  );
}
