$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

Write-Host "--- Tiểu Tony AI Gateway Environment Check ---" -ForegroundColor Cyan

# 1. Python version
try {
    $pyVer = python --version 2>&1
    Write-Host "Python: OK ($pyVer)" -ForegroundColor Green
} catch {
    Write-Host "Python: MISSING (Python not found in PATH)" -ForegroundColor Red
}

# 2. Virtualenv
if ($env:VIRTUAL_ENV) {
    Write-Host "Virtualenv: OK (Active: $env:VIRTUAL_ENV)" -ForegroundColor Green
} elseif (Test-Path ".venv") {
    Write-Host "Virtualenv: INACTIVE (Found .venv but not activated)" -ForegroundColor Yellow
} else {
    Write-Host "Virtualenv: MISSING (No .venv found)" -ForegroundColor Red
}

# 3. .env file
if (Test-Path ".env") {
    Write-Host ".env file: OK" -ForegroundColor Green
    # Check OPENROUTER_API_KEY inside .env
    $envContent = Get-Content ".env"
    $hasKey = $false
    foreach ($line in $envContent) {
        if ($line -match "^OPENROUTER_API_KEY=(.+)$" -and $matches[1] -ne "your_openrouter_api_key_here" -and $matches[1].Trim() -ne "") {
            $hasKey = $true
            break
        }
    }
    if ($hasKey) {
        Write-Host "OPENROUTER_API_KEY: SET" -ForegroundColor Green
    } else {
        Write-Host "OPENROUTER_API_KEY: MISSING or DEFAULT" -ForegroundColor Yellow
    }
} else {
    Write-Host ".env file: MISSING" -ForegroundColor Red
}

# 4. Import check
try {
    $fastapiCheck = python -c "import fastapi; print('OK')" 2>&1
    if ($fastapiCheck -eq "OK") {
        Write-Host "FastAPI import: OK" -ForegroundColor Green
    } else {
        Write-Host "FastAPI import: MISSING" -ForegroundColor Red
    }
} catch {
    Write-Host "FastAPI import: MISSING" -ForegroundColor Red
}

Write-Host "--- Check Complete ---" -ForegroundColor Cyan
