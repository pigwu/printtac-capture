Set-Location (Split-Path -Parent $PSScriptRoot)
. (Join-Path $PSScriptRoot "desktop_python.ps1")
& $PrintTacPython desktop/udp_pose_visualizer.py --host 0.0.0.0 --port 5555
exit $LASTEXITCODE
