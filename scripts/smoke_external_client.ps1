param (
    [string]$BaseUrl = "http://127.0.0.1:8000/v1",
    [string]$Model = "qwen/qwen3.6-plus",
    [switch]$Stream
)

$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

Write-Host "Preparing smoke test environment..." -ForegroundColor Cyan

# Check if .venv exists and activate it
if (Test-Path ".venv") {
    Write-Host "Activating virtual environment..." -ForegroundColor Gray
    . .venv\Scripts\Activate.ps1
}

# Set environment variables for the session
$env:AI_GATEWAY_BASE_URL = $BaseUrl
$env:AI_GATEWAY_MODEL = $Model
if ($Stream) {
    $env:AI_GATEWAY_STREAM = "true"
} else {
    $env:AI_GATEWAY_STREAM = "false"
}

Write-Host "Running smoke test script with:" -ForegroundColor Gray
Write-Host "  BaseUrl: $BaseUrl" -ForegroundColor Gray
Write-Host "  Model:   $Model" -ForegroundColor Gray
Write-Host "  Stream:  $($env:AI_GATEWAY_STREAM)" -ForegroundColor Gray
Write-Host "----------------------------------------" -ForegroundColor Gray

python examples/smoke_external_client.py

Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "PowerShell wrapper completed." -ForegroundColor Cyan
