. (Join-Path $PSScriptRoot "_common.ps1")

$backendProject = Get-BackendProject

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
