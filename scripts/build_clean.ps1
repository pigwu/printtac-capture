# Build the visualizer with a minimal, isolated Python environment.
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot
$env:QT_API = "pyqt6"

# Keep the environment under build/ for reuse; no recursive cleanup is needed.
$BuildEnvironment = Join-Path $ProjectRoot "build/visualizer-env"
python -m venv $BuildEnvironment
if ($LASTEXITCODE -ne 0) { throw "Failed to create build environment" }
$BuildPython = Join-Path $BuildEnvironment "Scripts/python.exe"
& $BuildPython -m pip install PyQt6 pyqtgraph numpy PyOpenGL pyinstaller pillow
if ($LASTEXITCODE -ne 0) { throw "Failed to install build dependencies" }

& $BuildPython (Join-Path $PSScriptRoot "build_desktop.py") --tool visualizer
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }

Write-Host "Build complete: dist/PrintTac Pose Visualizer.exe"
