Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$bootstrapDir = Join-Path $repoRoot ".tools\bootstrap"
$bootstrapPython = Join-Path $bootstrapDir "Scripts\python.exe"
$bootstrapPip = Join-Path $bootstrapDir "Scripts\pip.exe"
$bootstrapUv = Join-Path $bootstrapDir "Scripts\uv.exe"
$backendProject = Join-Path $repoRoot "backend"
$workspaceTemp = Join-Path $repoRoot ".tools\tmp"
$uvCache = Join-Path $repoRoot ".tools\uv-cache"

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python launcher 'py' is required to run setup."
}

New-Item -ItemType Directory -Force -Path $workspaceTemp | Out-Null
New-Item -ItemType Directory -Force -Path $uvCache | Out-Null
$env:TMP = $workspaceTemp
$env:TEMP = $workspaceTemp
$env:UV_CACHE_DIR = $uvCache
Remove-Item Env:VIRTUAL_ENV -ErrorAction SilentlyContinue

if (-not (Test-Path $bootstrapPython)) {
    & py -m venv $bootstrapDir

    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

if (-not (Test-Path $bootstrapPip)) {
    & $bootstrapPython -m ensurepip --upgrade
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

if (-not (Test-Path $bootstrapUv)) {
    & $bootstrapPython -m pip install --upgrade pip uv
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

& $bootstrapUv sync --project $backendProject --extra dev
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "Backend environment is ready."
Write-Host "Use .\tools\dev.ps1 to start the API."
