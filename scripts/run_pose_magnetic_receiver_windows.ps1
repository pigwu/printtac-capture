param(
    [string]$BindHost = "0.0.0.0",
    [int]$Port = 5558,
    [string]$PhoneIP = "",
    [int]$VideoPort = 5560,
    [string]$OutputDirectory = ""
)

$ScriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$Receiver = Join-Path (Split-Path -Parent $ScriptDirectory) "desktop/pose_magnetic_receiver.py"
$ReceiverArguments = @(
    $Receiver,
    "--host", $BindHost,
    "--port", $Port,
    "--video-port", $VideoPort
)

if ($PhoneIP) {
    $ReceiverArguments += @("--phone-ip", $PhoneIP)
}
if ($OutputDirectory) {
    $ReceiverArguments += @("--output-dir", $OutputDirectory)
}

. (Join-Path $PSScriptRoot "desktop_python.ps1")
& $PrintTacPython @ReceiverArguments
exit $LASTEXITCODE
