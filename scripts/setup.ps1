# scripts/setup.ps1
$ErrorActionPreference = "Stop"

Write-Host "Setting up Python virtual environment..." -ForegroundColor Cyan

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

$pip = ".\.venv\Scripts\pip.exe"
if (-not (Test-Path $pip)) {
    $pip = ".\.venv\Scripts\pip"
}

Write-Host "Installing dependencies..." -ForegroundColor Cyan
& $pip install --upgrade pip
& $pip install -r requirements.txt

Write-Host "Setup complete." -ForegroundColor Green
