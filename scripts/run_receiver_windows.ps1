param(
    [string]$HostIP = "0.0.0.0",
    [int]$Port = 5555,
    [string]$Encoding = "binary"
)

Set-Location (Split-Path -Parent $PSScriptRoot)

if (Get-Command py -ErrorAction SilentlyContinue) {
    py desktop/udp_pose_receiver.py --host $HostIP --port $Port --encoding $Encoding
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    python desktop/udp_pose_receiver.py --host $HostIP --port $Port --encoding $Encoding
} else {
    Write-Error "Python launcher not found. Install Python 3 first."
}
