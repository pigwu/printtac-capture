param(
    [string]$HostIP = "0.0.0.0",
    [int]$Port = 8000
)

Set-Location (Split-Path -Parent $PSScriptRoot)

. (Join-Path $PSScriptRoot "desktop_python.ps1")
& $PrintTacPython desktop/capture_upload_server.py --host $HostIP --port $Port
exit $LASTEXITCODE
