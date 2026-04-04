. (Join-Path $PSScriptRoot "_common.ps1")

$backendProject = Get-BackendProject

Push-Location $backendProject
try {
    Invoke-Uv @(
        "run",
        "--project",
        $backendProject,
        "pytest",
        "-p",
        "no:cacheprovider"
    )
}
finally {
    Pop-Location
}
