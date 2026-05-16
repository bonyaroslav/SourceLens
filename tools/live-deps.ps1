. (Join-Path $PSScriptRoot "_common.ps1")

$backendProject = Get-BackendProject

Push-Location $backendProject
try {
    Invoke-Uv @(
        "run",
        "--project",
        $backendProject,
        "python",
        "-m",
        "source_lens_api.live_dependency_smoke"
    )
}
finally {
    Pop-Location
}
