# scripts/run.ps1
$ErrorActionPreference = "Stop"

$python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = ".\.venv\Scripts\python"
}

$env:PYTHONPATH = "src"

# Run detached to avoid leaving a console window, but for script we can just use pythonw
$pythonw = $python -replace "python.exe", "pythonw.exe"
if (Test-Path $pythonw) {
    Start-Process $pythonw -ArgumentList "-m", "sprime_pm1_battery_tray"
} else {
    Start-Process $python -ArgumentList "-m", "sprime_pm1_battery_tray" -WindowStyle Hidden
}
