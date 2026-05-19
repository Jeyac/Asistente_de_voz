#!/usr/bin/env python3
"""
Añade docstrings en español a módulos/clases/funciones de Python que no tengan documentación.

Uso: python scripts/annotate_spanish_docstrings.py
Solo modifica archivos bajo src/asistente_voz/ (no tests ni venv).
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src" / "asistente_voz"

# Plantillas en español según nombre del símbolo
FUNC_HINTS: dict[str, str] = {
    "__init__": "Inicializa la instancia.",
    "execute": "Ejecuta la operación principal.",
    "predict": "Realiza la predicción.",
    "load": "Carga datos o artefactos desde disco.",
    "save": "Guarda datos o artefactos en disco.",
    "validate": "Valida la entrada.",
    "configure": "Configura el componente.",
    "register": "Registra el elemento en el sistema.",
    "create": "Crea y devuelve una instancia.",
    "get": "Obtiene un valor o dependencia.",
    "setup": "Configura el módulo o servicio.",
}


def _hint_for_name(name: str, *, is_class: bool = False) -> str:
    if is_class:
        readable = name.replace("_", " ")
        return f"Clase {readable}."
    if name in FUNC_HINTS:
        return FUNC_HINTS[name]
    readable = name.replace("_", " ")
    if name.startswith("get_"):
        return f"Obtiene {readable[4:]}."
    if name.startswith("set_"):
        return f"Establece {readable[4:]}."
    if name.startswith("is_"):
        return f"Indica si {readable[3:]}."
    if name.startswith("_"):
        return f"Método interno: {readable.lstrip('_ ')}."
    return f"Función {readable}."


def _module_doc_from_path(path: Path) -> str:
    rel = path.relative_to(SRC_ROOT).with_suffix("")
    parts = rel.parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    area = " / ".join(parts)
    return f"Módulo del paquete asistente_voz ({area})."


class SpanishDocstringTransformer(ast.NodeTransformer):
    def __init__(self, module_path: Path) -> None:
        self.module_path = module_path
        self.changed = False

    def visit_Module(self, node: ast.Module) -> ast.Module:
        if not ast.get_docstring(node):
            doc = _module_doc_from_path(self.module_path)
            node.body.insert(
                0,
                ast.Expr(value=ast.Constant(value=doc)),
            )
            self.changed = True
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.Module:
        if not ast.get_docstring(node):
            doc = _hint_for_name(node.name, is_class=True)
            node.body.insert(0, ast.Expr(value=ast.Constant(value=doc)))
            self.changed = True
        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        if not ast.get_docstring(node):
            doc = _hint_for_name(node.name)
            node.body.insert(0, ast.Expr(value=ast.Constant(value=doc)))
            self.changed = True
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        if not ast.get_docstring(node):
            doc = _hint_for_name(node.name)
            node.body.insert(0, ast.Expr(value=ast.Constant(value=doc)))
            self.changed = True
        self.generic_visit(node)
        return node


def process_file(path: Path) -> bool:
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        print(f"Omitido (sintaxis): {path}", file=sys.stderr)
        return False
    transformer = SpanishDocstringTransformer(path)
    new_tree = transformer.visit(tree)
    if not transformer.changed:
        return False
    ast.fix_missing_locations(new_tree)
    try:
        new_source = ast.unparse(new_tree)
    except Exception:
        print(f"Omitido (unparse): {path}", file=sys.stderr)
        return False
    path.write_text(new_source + "\n", encoding="utf-8")
    return True


def main() -> int:
    updated = 0
    for path in sorted(SRC_ROOT.rglob("*.py")):
        if process_file(path):
            updated += 1
            print(f"Actualizado: {path.relative_to(PROJECT_ROOT)}")
    print(f"\nTotal archivos actualizados: {updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
