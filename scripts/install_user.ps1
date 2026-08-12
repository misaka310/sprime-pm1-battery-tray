param(
    [switch]$EnableStartup
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$SourceDir = Join-Path $RepoRoot "dist\SPRIME-PM1-Battery-Tray"
$SourceExe = Join-Path $SourceDir "SPRIME-PM1-Battery-Tray.exe"

if (-not (Test-Path -LiteralPath $SourceExe)) {
    throw "Built application not found: $SourceExe. Run scripts/build.ps1 first."
}

$AppName = "SPRIME-PM1-Battery-Tray"
$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\SPRIME PM1 Battery Tray"
$InstallExe = Join-Path $InstallDir "$AppName.exe"

$Running = Get-Process -Name $AppName -ErrorAction SilentlyContinue
if ($Running) {
    $Running | Stop-Process -Force
    Start-Sleep -Milliseconds 500
}

if (Test-Path -LiteralPath $InstallDir) {
    Remove-Item -LiteralPath $InstallDir -Recurse -Force
}
New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
Copy-Item -Path (Join-Path $SourceDir "*") -Destination $InstallDir -Recurse -Force

$ProgramsDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
$StartupDir = Join-Path $ProgramsDir "Startup"
$StartMenuShortcut = Join-Path $ProgramsDir "SPRIME PM1 Battery Tray.lnk"
$StartupShortcut = Join-Path $StartupDir "SPRIME PM1 Battery Tray.lnk"

New-Item -ItemType Directory -Path $ProgramsDir -Force | Out-Null
New-Item -ItemType Directory -Path $StartupDir -Force | Out-Null

function Set-AppShortcut {
    param([Parameter(Mandatory = $true)][string]$ShortcutPath)

    $Shell = New-Object -ComObject WScript.Shell
    $Shortcut = $Shell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $InstallExe
    $Shortcut.WorkingDirectory = $InstallDir
    $Shortcut.IconLocation = "$InstallExe,0"
    $Shortcut.Description = "SPRIME PM1 battery monitor"
    $Shortcut.Save()
}

Set-AppShortcut -ShortcutPath $StartMenuShortcut

$ConfigDir = Join-Path $env:APPDATA "SprimePM1BatteryTray"
$ConfigPath = Join-Path $ConfigDir "config.json"
$StartOnBoot = $false
$Config = $null

if (Test-Path -LiteralPath $ConfigPath) {
    try {
        $Config = Get-Content -LiteralPath $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($null -ne $Config.start_on_boot) {
            $StartOnBoot = [bool]$Config.start_on_boot
        }
    }
    catch {
        Write-Warning "Existing config could not be read; leaving startup disabled unless -EnableStartup is specified."
    }
}

if ($EnableStartup) {
    $StartOnBoot = $true
    New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null
    if ($null -eq $Config) {
        $Config = [pscustomobject]@{}
    }
    if ($Config.PSObject.Properties.Name -contains "start_on_boot") {
        $Config.start_on_boot = $true
    }
    else {
        $Config | Add-Member -NotePropertyName "start_on_boot" -NotePropertyValue $true
    }
    $ConfigJson = $Config | ConvertTo-Json -Depth 10
    $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($ConfigPath, $ConfigJson, $Utf8NoBom)
}

if ($StartOnBoot) {
    Set-AppShortcut -ShortcutPath $StartupShortcut
}
else {
    Remove-Item -LiteralPath $StartupShortcut -Force -ErrorAction SilentlyContinue
}

$RunKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
Remove-ItemProperty -Path $RunKey -Name "SPRIME PM1 Battery Tray" -ErrorAction SilentlyContinue

Write-Output "INSTALL_EXE=$InstallExe"
Write-Output "START_MENU_SHORTCUT=$StartMenuShortcut"
Write-Output "STARTUP_ENABLED=$StartOnBoot"
if ($StartOnBoot) {
    Write-Output "STARTUP_SHORTCUT=$StartupShortcut"
}
