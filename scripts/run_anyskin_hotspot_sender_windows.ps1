param(
    [string]$PhoneIP = "172.20.10.1",
    [int]$Port = 5557,
    [double]$Rate = 100
)

$ScriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$Sender = Join-Path (Split-Path -Parent $ScriptDirectory) "desktop/anyskin_hotspot_sender.py"
$SenderArguments = @($Sender, "--host", $PhoneIP, "--port", $Port, "--rate", $Rate)

. (Join-Path $PSScriptRoot "desktop_python.ps1")
& $PrintTacPython @SenderArguments
exit $LASTEXITCODE
