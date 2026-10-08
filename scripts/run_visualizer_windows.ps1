Set-Location (Split-Path -Parent $PSScriptRoot)
py desktop/udp_pose_visualizer.py --host 0.0.0.0 --port 5555
