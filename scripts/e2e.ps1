# scripts/e2e.ps1
$ErrorActionPreference = "Stop"

Write-Host "Running E2E tests..." -ForegroundColor Cyan

Write-Host "`n1. Running Setup..." -ForegroundColor Cyan
.\scripts\setup.ps1

$python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = ".\.venv\Scripts\python"
}

Write-Host "`n2. Running Unit Tests..." -ForegroundColor Cyan
$env:PYTHONPATH = "src"
& $python -m pytest tests/
if ($LASTEXITCODE -ne 0) {
    throw "Unit tests failed!"
}

Write-Host "`n3. Running Probe..." -ForegroundColor Cyan
.\scripts\probe.ps1

Write-Host "`n4. Testing HID Protocol (Real Device Battery Read)..." -ForegroundColor Cyan
$env:PYTHONPATH = "src"
& $python -c @"
import sys
from sprime_pm1_battery_tray.hid_protocol import get_battery_info
res = get_battery_info()
print('Battery info:', res)
status = res.get('status', 'unknown')
if status in ['connected', 'disconnected']:
    print(f'Device found with status: {status}')
    sys.exit(0)
else:
    print(f'Device check failed with status: {status}')
    sys.exit(1)
"@
if ($LASTEXITCODE -ne 0) {
    throw "Real device HID check failed! (status must be connected or disconnected)"
}

Write-Host "`n5. Building EXE..." -ForegroundColor Cyan
.\scripts\build.ps1
if ($LASTEXITCODE -ne 0) {
    throw "Build script failed with exit code $LASTEXITCODE."
}

$exePath = "dist\SPRIME-PM1-Battery-Tray\SPRIME-PM1-Battery-Tray.exe"
Write-Host "`n6. Checking EXE existence at $exePath..." -ForegroundColor Cyan
if (-not (Test-Path $exePath)) {
    throw "EXE was not generated at expected path: $exePath"
}

Write-Host "`n7. Running Smoke Test on built EXE..." -ForegroundColor Cyan
& $exePath --smoke-test
$exitCode = $LASTEXITCODE
if ($exitCode -eq 0) {
    Write-Host "Smoke test passed!" -ForegroundColor Green
} else {
    throw "Smoke test failed with exit code $exitCode! This usually means an ImportError or initialization failure."
}

Write-Host "`nE2E complete! All steps passed." -ForegroundColor Green
