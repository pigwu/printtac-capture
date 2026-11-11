param(
    [string]$HostIP = "0.0.0.0",
    [int]$Port = 5555,
    [string]$Encoding = "binary"
)

Set-Location (Split-Path -Parent $PSScriptRoot)

. (Join-Path $PSScriptRoot "desktop_python.ps1")
& $PrintTacPython desktop/udp_pose_receiver.py --host $HostIP --port $Port --encoding $Encoding
exit $LASTEXITCODE
