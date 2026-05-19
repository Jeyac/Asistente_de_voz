#!/usr/bin/env python3
"""Añade bloque JSDoc en español al inicio de archivos .ts/.tsx del frontend sin comentario."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"

DESCRIPTIONS: dict[str, str] = {
    "main.tsx": "Punto de entrada de la aplicación React (monta App en el DOM).",
    "App.tsx": "Componente raíz: layout del asistente de voz.",
    "index.css": "Estilos globales Tailwind y variables CSS.",
    "vite-env.d.ts": "Tipos de Vite (import.meta.env).",
}


def _desc_for(path: Path) -> str:
    name = path.name
    if name in DESCRIPTIONS:
        return DESCRIPTIONS[name]
    rel = path.relative_to(FRONTEND_SRC).as_posix()
    if "hooks/" in rel:
        return f"Hook React: lógica de {path.stem}."
    if "services/" in rel:
        return f"Cliente HTTP / servicio: {path.stem}."
    if "utils/" in rel:
        return f"Utilidades: {path.stem}."
    if "components/ui/" in rel:
        return f"Componente UI reutilizable: {path.stem}."
    if "components/layout/" in rel:
        return f"Componente de layout: {path.stem}."
    if "components/assistant/" in rel:
        return f"Componente del asistente de voz: {path.stem}."
    if "types/" in rel:
        return f"Tipos TypeScript compartidos ({path.stem})."
    return f"Módulo frontend: {rel}."


def _has_header(text: str) -> bool:
    stripped = text.lstrip()
    return stripped.startswith("/**") or stripped.startswith("//") or stripped.startswith("/*")


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if _has_header(text):
        return False
    desc = _desc_for(path)
    block = f"/**\n * {desc}\n */\n"
    path.write_text(block + text, encoding="utf-8")
    return True


def main() -> None:
    updated = 0
    for path in sorted(FRONTEND_SRC.rglob("*")):
        if path.suffix not in (".ts", ".tsx", ".css"):
            continue
        if process_file(path):
            updated += 1
            print(f"Actualizado: {path.relative_to(PROJECT_ROOT)}")
    print(f"\nTotal: {updated}")


if __name__ == "__main__":
    main()
