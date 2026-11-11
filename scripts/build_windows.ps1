# Build current PrintTac desktop executables using the selected Python environment.
param(
    [ValidateSet("all", "monitor", "visualizer", "validator", "packet-loss", "zarr-exporter", "anyskin-monitor", "anyskin-serial", "video-debugger")]
    [string]$Tool = "all",
    [switch]$DryRun
)
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BuildArguments = @((Join-Path $PSScriptRoot "build_desktop.py"), "--tool", $Tool)
if ($DryRun) { $BuildArguments += "--dry-run" }
. (Join-Path $PSScriptRoot "desktop_python.ps1")
& $PrintTacPython @BuildArguments
if ($LASTEXITCODE -ne 0) { throw "PrintTac desktop build failed" }
