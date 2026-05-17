Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$bootstrapDir = Join-Path $repoRoot ".tools\bootstrap"
$bootstrapPython = Join-Path $bootstrapDir "Scripts\python.exe"
$bootstrapPip = Join-Path $bootstrapDir "Scripts\pip.exe"
$bootstrapUv = Join-Path $bootstrapDir "Scripts\uv.exe"
$backendProject = Join-Path $repoRoot "backend"
$frontendProject = Join-Path $repoRoot "frontend"
$workspaceTemp = Join-Path $repoRoot ".tools\tmp"
$uvCache = Join-Path $repoRoot ".tools\uv-cache"

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python launcher 'py' is required to run setup."
}

if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) {
    throw "npm is required to run setup."
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

Push-Location $frontendProject
try {
    & npm.cmd ci
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
finally {
    Pop-Location
}

Write-Host "Backend and frontend dependencies are ready."
Write-Host "Use .\tools\dev.ps1 to start the API and npm start in .\frontend for the Angular UI."
