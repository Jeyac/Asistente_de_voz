# Instala dependencias en Python 3.12 (recomendado para este proyecto)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

Write-Host "Instalando en Python 3.12..." -ForegroundColor Cyan
py -3.12 -m pip install --upgrade pip
py -3.12 -m pip uninstall -y tensorflow tensorflow-intel 2>$null
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\Programs\Python\Python312\Lib\site-packages\tensorflow" -ErrorAction SilentlyContinue
py -3.12 -m pip install -r requirements.txt
py -3.12 -m spacy download es_core_news_sm
py -3.12 scripts/download_wakeword_model.py
Write-Host "Listo. Arranca con: scripts\run_api.bat" -ForegroundColor Green
