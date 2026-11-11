param(
    [string]$Port = "COM9",
    [int]$Baud = 115200
)

$ScriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$Mapper = Join-Path (Split-Path -Parent $ScriptDirectory) "desktop/anyskin_serial_mapper.py"
$MapperArguments = @($Mapper, "--port", $Port, "--baud", $Baud)

. (Join-Path $PSScriptRoot "desktop_python.ps1")
& $PrintTacPython @MapperArguments
exit $LASTEXITCODE
