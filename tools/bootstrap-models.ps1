. (Join-Path $PSScriptRoot "_common.ps1")

$ollamaBaseUrl = if ($env:SOURCE_LENS_OLLAMA_BASE_URL) {
    $env:SOURCE_LENS_OLLAMA_BASE_URL.TrimEnd("/")
}
else {
    "http://127.0.0.1:11434"
}

$models = @(
    $(if ($env:SOURCE_LENS_CHAT_MODEL) { $env:SOURCE_LENS_CHAT_MODEL } else { "qwen3:4b" }),
    $(if ($env:SOURCE_LENS_EMBEDDING_MODEL) { $env:SOURCE_LENS_EMBEDDING_MODEL } else { "qwen3-embedding:0.6b" })
)

foreach ($model in $models) {
    Write-Host "Pulling $model..."
    $pullResponse = Invoke-RestMethod `
        -Method Post `
        -Uri "$ollamaBaseUrl/api/pull" `
        -ContentType "application/json" `
        -Body (@{ name = $model; stream = $false } | ConvertTo-Json)

    Write-Host "Verifying $model..."
    if ($pullResponse.status -and $pullResponse.status -notmatch "success") {
        throw "Ollama pull did not report success for $model."
    }
}

$tagsResponse = Invoke-RestMethod -Method Get -Uri "$ollamaBaseUrl/api/tags"
$availableModels = @($tagsResponse.models | ForEach-Object { $_.name })

foreach ($model in $models) {
    if ($model -notin $availableModels) {
        throw "Model $model was not present after bootstrap."
    }
}

Write-Host "Phase 2 Ollama models are available."
