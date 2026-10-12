# Build PrintTac desktop executables

Build on the target operating system: Windows creates `.exe` files; macOS creates `.app` bundles. Python 3.10 or newer is required for source builds.

## Prepare the environment

Use one Python environment for dependency installation and building:

```bash
python -m pip install -r requirements_visualizer.txt
python -m pip install pyinstaller pillow
```

On macOS use `python3`. A clean virtual environment is recommended. PyInstaller packages this environment; the recipient of a correctly built standalone executable does not need Python.

## Build on Windows

From the repository root:

```powershell
# Recommended experiment monitor only
.\scripts\build_windows.ps1 -Tool monitor

# All eight desktop applications
.\scripts\build_windows.ps1

# Validate source and packaging paths without building
.\scripts\build_windows.ps1 -DryRun
```

## Build on macOS

```bash
# Recommended experiment monitor only
bash scripts/build_macos.sh --tool monitor

# All eight desktop applications
bash scripts/build_macos.sh

# Validate packaging commands
bash scripts/build_macos.sh --dry-run
```

## Current output names

The product list is defined once in `config/desktop_tools.json` and used by both platforms.

| Tool | Windows (`dist/`) | macOS (`dist/`) |
| --- | --- | --- |
| `monitor` | `PrintTac Capture.exe` | `PrintTac Capture.app` |
| `visualizer` | `PrintTac Pose Visualizer.exe` | `PrintTac Pose Visualizer.app` |
| `validator` | `PrintTac Tracking Validator.exe` | `PrintTac Tracking Validator.app` |
| `packet-loss` | `PrintTac Packet Loss Monitor.exe` | `PrintTac Packet Loss Monitor.app` |
| `zarr-exporter` | `PrintTac Zarr Exporter.exe` | `PrintTac Zarr Exporter.app` |
| `anyskin-monitor` | `PrintTac AnySkin UDP Monitor.exe` | `PrintTac AnySkin UDP Monitor.app` |
| `anyskin-serial` | `PrintTac AnySkin Serial Mapper.exe` | `PrintTac AnySkin Serial Mapper.app` |
| `video-debugger` | `PrintTac Video Debugger.exe` | `PrintTac Video Debugger.app` |

Specs are stored in `build/specs/`, intermediate files in `build/pyinstaller/`, and distributable applications in `dist/`. Source, resource and icon paths are resolved from the repository root, even when the script is launched from a different directory.

## Install a desktop application

Download current assets from the repository's [Releases page](https://github.com/pigwu/printtac-capture/releases/latest), or copy the application you built locally. Use **PrintTac Capture** for the integrated monitor, upload receiver and replay workspace.

Release assets use hyphens, for example `PrintTac-Capture.exe`, while local build output uses the spaced filenames in the table. They contain the same application.

Keep the application in a writable directory because recorded experiments are saved in `uploads/` beside it. Close older monitors before launching a new one; they use the same network ports. Existing `uploads/` can remain alongside the new executable. Source runs continue to use the repository-root `uploads/`.

For macOS, distribute a build created on macOS. Signing and notarization require your own Apple configuration. If the operating system rejects a downloaded application, verify its origin and signature; a source rebuild is also available.

## Troubleshooting

- **Import or Qt binding failures:** build in the same environment used to install requirements. The builder selects PyQt6 and excludes conflicting Qt bindings.
- **QtCore DLL errors in a mixed Conda environment:** the builder prioritizes Windows system libraries so an incompatible Conda ICU DLL cannot replace the Windows ICU API required by Qt. Use the provided builder instead of repackaging an old spec file.
- **Missing sensor configuration:** both ArUco and ultra-wide configuration files are bundled. User calibration can still be selected separately.
- **Large executable:** scientific, video and Qt dependencies are included; actual sizes vary by environment.
- **An older EXE still shows the old name:** source changes do not modify already-built binaries. Use a newly built PrintTac executable. Historical release assets retain their original version names.
- **Video decoder unavailable:** rebuild the monitor/video debugger with its manifest settings; the builder collects PyAV for those tools.

The smaller visualizer-only environment is available through `.\scripts\build_clean.ps1` on Windows. It produces `PrintTac Pose Visualizer.exe`, rather than the integrated monitor.
