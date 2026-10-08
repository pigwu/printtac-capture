Set-Location (Split-Path -Parent $PSScriptRoot)
python desktop/udp_packet_loss_monitor.py --host 0.0.0.0 --port 5555 --encoding binary
