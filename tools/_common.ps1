Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script:RepoRoot = Split-Path -Parent $PSScriptRoot
$script:BackendProject = Join-Path $script:RepoRoot "backend"
$script:FrontendProject = Join-Path $script:RepoRoot "frontend"
$script:BootstrapPython = Join-Path $script:RepoRoot ".tools\bootstrap\Scripts\python.exe"
$script:BootstrapUv = Join-Path $script:RepoRoot ".tools\bootstrap\Scripts\uv.exe"
$script:WorkspaceTemp = Join-Path $script:RepoRoot ".tools\tmp"
$script:UvCache = Join-Path $script:RepoRoot ".tools\uv-cache"

New-Item -ItemType Directory -Force -Path $script:WorkspaceTemp | Out-Null
New-Item -ItemType Directory -Force -Path $script:UvCache | Out-Null
$env:TMP = $script:WorkspaceTemp
$env:TEMP = $script:WorkspaceTemp
$env:UV_CACHE_DIR = $script:UvCache
Remove-Item Env:VIRTUAL_ENV -ErrorAction SilentlyContinue

function Get-BootstrapUv {
    if (-not (Test-Path $script:BootstrapUv)) {
        throw "Bootstrap environment not found. Run .\tools\setup.ps1 first."
    }

    return $script:BootstrapUv
}

function Get-BackendProject {
    return $script:BackendProject
}

function Get-FrontendProject {
    return $script:FrontendProject
}

function Invoke-Uv {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $uv = Get-BootstrapUv
    & $uv @Arguments

    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

function Invoke-Npm {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) {
        throw "npm is required to run frontend commands."
    }

    & npm.cmd @Arguments

    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
