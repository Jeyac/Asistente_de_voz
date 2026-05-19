@echo off
cd /d "%~dp0.."
set PYTHONPATH=src
set RETRAIN_INTENTS_ALWAYS=true
echo Reentrenando modelo...
py -3.12 scripts\ensure_intent_model.py
if errorlevel 1 (
  echo Fallo el entrenamiento. Revisa: pip install -r requirements.txt
  pause
  exit /b 1
)
echo Arrancando API...
py -3.12 -m uvicorn asistente_voz.main:app --reload --host 0.0.0.0 --port 8000
if errorlevel 1 (
  echo.
  echo Si falla: py -3.12 -m pip install -r requirements.txt
  echo           set PYTHONPATH=src
  pause
)
