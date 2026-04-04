. (Join-Path $PSScriptRoot "_common.ps1")

$backendProject = Get-BackendProject

Push-Location $backendProject
try {
    Invoke-Uv @(
        "run",
        "--project",
        $backendProject,
        "uvicorn",
        "source_lens_api.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000"
    )
}
finally {
    Pop-Location
}
