# API en desarrollo — usa Python 3.12 y PYTHONPATH=src
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root
$env:PYTHONPATH = "src"

$py = $null
foreach ($candidate in @("py -3.12", "python")) {
    try {
        Invoke-Expression "$candidate -c `"import sys; print(sys.version)`"" | Out-Null
        $py = $candidate
        break
    } catch { }
}
if (-not $py) { $py = "python" }

Write-Host "Arrancando API ($py) | PYTHONPATH=src | http://127.0.0.1:8000" -ForegroundColor Cyan
if ($py -eq "py -3.12") {
    py -3.12 -m pip install -q -r requirements.txt 2>$null
    py -3.12 -m uvicorn asistente_voz.main:app --reload --host 0.0.0.0 --port 8000
} else {
    python -m uvicorn asistente_voz.main:app --reload --host 0.0.0.0 --port 8000
}
