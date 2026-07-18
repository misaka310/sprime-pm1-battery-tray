$ErrorActionPreference = 'Stop'

$entrypoint = Join-Path $PSScriptRoot 'scripts\run.ps1'
& $entrypoint @args
exit $LASTEXITCODE
