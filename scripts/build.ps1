# scripts/build.ps1
$ErrorActionPreference = "Stop"

Write-Host "Building EXE with PyInstaller..." -ForegroundColor Cyan

$python = ".\.venv\Scripts\python.exe"
$pyinstaller = ".\.venv\Scripts\pyinstaller.exe"
$appName = "SPRIME-PM1-Battery-Tray"
$distDir = "dist\$appName"
$buildDir = "build\$appName"
$specFile = "$appName.spec"

function Stop-ExistingApp {
    $processes = Get-Process -Name $appName -ErrorAction SilentlyContinue
    if ($processes) {
        Write-Host "Stopping running $appName process before build..." -ForegroundColor Yellow
        $processes | Stop-Process -Force
        Start-Sleep -Seconds 1
    }
}

function Remove-PathWithRetry {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [int]$Retries = 5
    )

    if (-not (Test-Path $Path)) {
        return
    }

    for ($i = 1; $i -le $Retries; $i++) {
        try {
            Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction Stop
            return
        } catch {
            if ($i -eq $Retries) {
                throw "Failed to remove '$Path'. Close any running app/window or Explorer preview using it, then retry. Original error: $($_.Exception.Message)"
            }
            Write-Host "Retrying cleanup for $Path ($i/$Retries)..." -ForegroundColor Yellow
            Start-Sleep -Seconds 1
        }
    }
}

Stop-ExistingApp
Remove-PathWithRetry -Path $distDir
Remove-PathWithRetry -Path $buildDir
Remove-PathWithRetry -Path $specFile

# Get customtkinter path
$ctk_path = & $python -c "import customtkinter, os; print(os.path.dirname(customtkinter.__file__))"
Write-Host "CustomTkinter path: $ctk_path"

$env:PYTHONPATH = "src"

& $pyinstaller --noconfirm --onedir --windowed `
    --name $appName `
    --paths "src" `
    --add-data "src/sprime_pm1_battery_tray;sprime_pm1_battery_tray/" `
    --add-data "$($ctk_path);customtkinter/" `
    pyinstaller_entry.py

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed with exit code $LASTEXITCODE."
}

$exePath = Join-Path $distDir "$appName.exe"
if (-not (Test-Path $exePath)) {
    throw "Build finished but EXE was not generated at expected path: $exePath"
}

Write-Host "Build complete. EXE is in dist\SPRIME-PM1-Battery-Tray\" -ForegroundColor Green
