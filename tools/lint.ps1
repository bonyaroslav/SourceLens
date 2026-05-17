. (Join-Path $PSScriptRoot "_common.ps1")

$backendProject = Get-BackendProject
$frontendProject = Get-FrontendProject

Push-Location $backendProject
try {
    Invoke-Uv @(
        "run",
        "--project",
        $backendProject,
        "ruff",
        "check",
        "src",
        "tests"
    )
}
finally {
    Pop-Location
}

Push-Location $frontendProject
try {
    Invoke-Npm @("run", "lint")
}
finally {
    Pop-Location
}
