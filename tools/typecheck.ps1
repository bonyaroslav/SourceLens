. (Join-Path $PSScriptRoot "_common.ps1")

$backendProject = Get-BackendProject
$frontendProject = Get-FrontendProject

Push-Location $backendProject
try {
    Invoke-Uv @(
        "run",
        "--project",
        $backendProject,
        "pyright"
    )
}
finally {
    Pop-Location
}

Push-Location $frontendProject
try {
    Invoke-Npm @("run", "typecheck")
}
finally {
    Pop-Location
}
