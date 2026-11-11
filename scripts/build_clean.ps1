# Build the visualizer with an isolated copy of the pinned desktop environment.
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot
$env:QT_API = "pyqt6"

# Keep the environment under build/ for reuse; no recursive cleanup is needed.
$BuildEnvironment = Join-Path $ProjectRoot "build/visualizer-env"
. (Join-Path $PSScriptRoot 'desktop_python.ps1')
& $PrintTacPython -m venv $BuildEnvironment
if ($LASTEXITCODE -ne 0) { throw "Failed to create build environment" }
$BuildPython = Join-Path $BuildEnvironment "Scripts/python.exe"
& $BuildPython -m pip install --only-binary=:all: -r (Join-Path $ProjectRoot 'requirements_visualizer.txt') pyinstaller pillow
if ($LASTEXITCODE -ne 0) { throw "Failed to install build dependencies" }

& $BuildPython (Join-Path $PSScriptRoot "build_desktop.py") --tool visualizer
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }

Write-Host "Build complete: dist/PrintTac Pose Visualizer.exe"
