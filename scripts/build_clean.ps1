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
& $BuildPython -m pip install PyQt6 pyqtgraph numpy PyOpenGL pyinstaller
if ($LASTEXITCODE -ne 0) { throw "Failed to install build dependencies" }

& $BuildPython -m PyInstaller --name "ARPose Visualizer" `
    --windowed --onefile --clean --specpath build/specs `
    --icon=ios/Assets.xcassets/AppIcon.appiconset/Icon-1024.png `
    --exclude-module torch --exclude-module pandas --exclude-module scipy `
    --exclude-module matplotlib --exclude-module IPython `
    --exclude-module jupyter --exclude-module notebook `
    --exclude-module sympy --exclude-module PIL --exclude-module tkinter `
    desktop/udp_pose_visualizer.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }

Write-Host "Build complete: dist/ARPose Visualizer.exe"
