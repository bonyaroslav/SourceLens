. (Join-Path $PSScriptRoot "_common.ps1")

$backendProject = Get-BackendProject
$frontendProject = Get-FrontendProject

Push-Location $backendProject
try {
    Invoke-Uv @(
        "run",
        "--project",
        $backendProject,
        "pytest",
        "--basetemp=.pytest_tmp",
        "-p",
        "no:cacheprovider"
    )
}
finally {
    Pop-Location
}

Push-Location $frontendProject
try {
    Invoke-Npm @("run", "test:ci")
}
finally {
    Pop-Location
}
