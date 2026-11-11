param(
    [string]$BindHost = "0.0.0.0",
    [int]$VideoPort = 5560,
    [int]$PosePort = 5555
)

Set-Location (Split-Path -Parent $PSScriptRoot)

. (Join-Path $PSScriptRoot "desktop_python.ps1")
& $PrintTacPython desktop/udp_video_debug_ui.py --bind $BindHost --video-port $VideoPort --pose-port $PosePort
exit $LASTEXITCODE
