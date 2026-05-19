#!/usr/bin/env python
"""
Guía para obtener el modelo 'oye sistema'.

openWakeWord (recomendado):
  1. pip install openwakeword
  2. Siga: https://github.com/dscripka/openWakeWord#training-models
  3. Guarde el .onnx en models/wakeword/oye_sistema.onnx

Porcupine (alternativa):
  1. Cree cuenta en https://console.picovoice.ai/
  2. Entrene la palabra 'oye sistema' en español
  3. Descargue el .ppn y configúrelos en PORCUPINE_KEYWORD_PATH
  4. Establezca WAKEWORD_ENGINE=porcupine y PORCUPINE_ACCESS_KEY
"""

print(__doc__)
