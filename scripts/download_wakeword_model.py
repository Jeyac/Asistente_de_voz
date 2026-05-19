#!/usr/bin/env python
"""Descarga modelos openWakeWord oficiales y copia hey_jarvis al proyecto."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGET_DIR = PROJECT_ROOT / "models" / "wakeword"
MODEL_NAME = "hey_jarvis_v0.1.onnx"


def main() -> int:
    try:
        from openwakeword.utils import download_models
    except ImportError:
        print("Instale dependencias: pip install openwakeword onnxruntime")
        return 1

    print("Descargando modelos openWakeWord...")
    download_models()

    import openwakeword

    package_root = Path(openwakeword.__file__).resolve().parent
    source = package_root / "resources" / "models" / MODEL_NAME
    if not source.is_file():
        print(f"No se encontró el modelo en: {source}")
        return 1

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    destination = TARGET_DIR / MODEL_NAME
    shutil.copy2(source, destination)

    size_kb = destination.stat().st_size / 1024
    print(f"Modelo copiado: {destination} ({size_kb:.0f} KB)")
    print()
    print("Configure en .env:")
    print("  WAKEWORD_PHRASE=hey jarvis")
    print(f"  WAKEWORD_MODEL_PATH=models/wakeword/{MODEL_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
