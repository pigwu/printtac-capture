Set-Location (Split-Path -Parent $PSScriptRoot)
. (Join-Path $PSScriptRoot "desktop_python.ps1")
& $PrintTacPython desktop/udp_packet_loss_monitor.py --host 0.0.0.0 --port 5555 --encoding binary
exit $LASTEXITCODE
