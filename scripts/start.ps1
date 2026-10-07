param([switch]$Install)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $projectRoot
if ($Install -or -not (Test-Path '.venv\Scripts\python.exe')) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Instale Python 3.11 ou superior e tente novamente.' }
    & '.\.venv\Scripts\python.exe' -m pip install -r apps/api/requirements.lock
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao instalar dependências Python.' }
    npm --prefix apps/web ci
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao instalar dependências do frontend.' }
}
if ($Install -or -not (Test-Path 'apps/web/dist/index.html')) {
    npm --prefix apps/web run build
    if ($LASTEXITCODE -ne 0) { throw 'Falha no build do frontend.' }
}
Write-Host 'Canalytics: http://localhost:8093 — Ctrl+C para encerrar.'
& '.\.venv\Scripts\python.exe' -m uvicorn canalytics.main:app --app-dir apps/api --host 127.0.0.1 --port 8093 --workers 1 --no-access-log
