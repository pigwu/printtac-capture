param(
    [string]$BindHost = "0.0.0.0",
    [int]$VideoPort = 5560,
    [int]$ArucoVideoPort = 5561,
    [int]$PosePort = 5555,
    [int]$CombinedPort = 5558,
    [int]$UploadPort = 8000,
    [string]$PhoneIP = "172.20.10.1",
    [string]$ArucoConfig = "config\umi_gripper_aruco.json"
)

Set-Location (Split-Path -Parent $PSScriptRoot)

$arguments = @(
    "desktop/experiment_replay_ui.py",
    "--bind", $BindHost,
    "--video-port", $VideoPort,
    "--aruco-video-port", $ArucoVideoPort,
    "--pose-port", $PosePort,
    "--combined-port", $CombinedPort,
    "--upload-port", $UploadPort,
    "--phone-ip", $PhoneIP,
    "--aruco-config", $ArucoConfig
)

. (Join-Path $PSScriptRoot "desktop_python.ps1")
& $PrintTacPython @arguments
exit $LASTEXITCODE
