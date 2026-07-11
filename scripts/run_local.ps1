param (
    [switch]$Reload
)

$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

Write-Host "Starting Tiểu Tony AI Gateway..." -ForegroundColor Cyan

# Check if .venv exists
if (-not (Test-Path ".venv")) {
    Write-Host "Warning: .venv not found. Did you forget to create it?" -ForegroundColor Yellow
} else {
    # Activate venv
    Write-Host "Activating virtual environment..."
    . .venv\Scripts\Activate.ps1
}

# Check .env
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found. Copying from .env.example..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item .env.example .env
        Write-Host "Copied .env.example to .env. Please update it if necessary." -ForegroundColor Green
    }
}

# Run Uvicorn
$UvicornArgs = @("ai_gateway.api.app:app")
if ($Reload) {
    $UvicornArgs += "--reload"
}

Write-Host "Running: python -m uvicorn $($UvicornArgs -join ' ')" -ForegroundColor Green
python -m uvicorn @UvicornArgs
