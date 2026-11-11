# Shared by legacy launchers. Never fall back to a different interpreter.
$PrintTacRoot = Split-Path -Parent $PSScriptRoot
$PrintTacPython = Join-Path $PrintTacRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $PrintTacPython)) {
    throw "Desktop environment missing. In the project folder run: py -3.12 scripts/setup_desktop.py"
}
