<div align="center">

![PrintTac Capture workflow](docs/assets/printtac-capture.svg)

# PrintTac Capture

**Untethered multimodal demonstration collection with an iPhone.**

Record vision, motion and tactile observations locally. Upload, replay and prepare datasets for robot learning.

[![iOS](https://img.shields.io/badge/iOS-17%2B-202F2C?style=flat-square)](docs/INSTALL_IPHONE_APP.md) [![Desktop](https://img.shields.io/badge/Desktop-Windows%20%7C%20macOS-202F2C?style=flat-square)](docs/SETUP.md) [![Output](https://img.shields.io/badge/Output-MP4%20%2B%20CSV%20%2B%20Zarr-E87346?style=flat-square)](docs/ZARR_EXPORT.md) [![License](https://img.shields.io/badge/License-MIT-799878?style=flat-square)](LICENSE)

[Project page](https://peppasaur.github.io/PrintTac/) · [简体中文](README.zh-CN.md) · [Quick start](#quick-start) · [Documentation](#documentation)

</div>

## What this repository provides

PrintTac Capture is the data-collection software for the PrintTac portable demonstration workflow. A handheld UMI-style gripper combines an iPhone with optional PrintTac fingertips. The phone records camera video, ARKit camera pose and right/left magnetic sensor streams; a desktop workspace handles uploads, inspection, replay, gripper-aperture processing and Zarr export.

**The iPhone is the recording hub.** A computer can monitor a live session, but demonstrations can be recorded without a host connection and uploaded afterward.

| Capture on the phone | Review on the desktop | Prepare for learning |
| --- | --- | --- |
| RGB and supported ultra-wide video | Grouped experiment uploads | ArUco gripper-aperture processing |
| ARKit pose and recording timestamps | Video, pose and tactile replay | Optional camera-to-gripper calibration |
| Independent right/left magnetic logs | Stream and transport diagnostics | Aligned Zarr episode export |

The [PrintTac project page](https://peppasaur.github.io/PrintTac/) introduces the tactile hardware and research results. This repository implements the capture and dataset-preparation workflow; hardware CAD, sensor firmware, force-estimation models and policy training/deployment are separate components.

## Quick start

On Windows, a current [release executable](https://github.com/pigwu/printtac-capture/releases/latest) can be run directly: choose **PrintTac-Capture.exe** for monitoring, uploads and replay. Use a writable folder and keep existing `uploads/` beside the executable. The source workflow below is for building the iPhone app and running tools with Python.

### 1. Prepare the phone

If the app is already installed, skip this build step. Otherwise build and sign it on a Mac using Xcode and XcodeGen; follow the [iPhone installation guide](docs/INSTALL_IPHONE_APP.md). The project, target and scheme are `PrintTacCapture`; the installed app is named PrintTac Capture. **Xcode is needed to build the phone app, not to run the Windows desktop tools.**

For tactile collection, connect the configured right/left sensor boards to the iPhone hotspot. Configure and check each board using the [magnetic capture guide](docs/HOTSPOT_MAGNETIC_CAPTURE.zh-CN.md). Pose/video recording also works with no magnetic boards connected.

### 2. Open the desktop workspace

Use **64-bit Python 3.12** for the source installation. Download/extract the repository (or clone it), then open a terminal in the folder containing `printtac.py`. Avoid installing into an existing Conda or system environment. The setup script creates `.venv`, installs the pinned dependencies from binary packages and checks video decoding, ArUco, plotting and Zarr read/write support. It can be rerun after an interrupted download.

**Windows 10/11, x64 — PowerShell:**

Install Python 3.12 (64-bit) with its Python launcher from [python.org](https://www.python.org/downloads/release/python-31210/) (under **Files**, choose **Windows installer (64-bit)**, not the source archive), then reopen PowerShell. An existing newer 3.12 patch release also works. `py -3.12 --version` must print `Python 3.12.x`.

```powershell
# First installation (run in the extracted repository folder)
py -3.12 scripts/setup_desktop.py

# Launch after setup reports [READY]; use this command on subsequent runs too
.\.venv\Scripts\python.exe printtac.py monitor --phone-ip 172.20.10.1
```

**macOS — Terminal:**

Install Python 3.12 using the [macOS universal2 installer](https://www.python.org/downloads/release/python-31210/) (under **Files**), or use an existing Python 3.12 installation, then run:

```bash
python3.12 scripts/setup_desktop.py
./.venv/bin/python printtac.py monitor --phone-ip 172.20.10.1
```

No environment activation, administrator terminal or C/C++ compiler is needed for this installation. Always use the `.venv` interpreter to run desktop tools; bare `python`, `python3` or `py` may select a different installation. Existing platform launchers in `scripts/` also use this `.venv`.

`172.20.10.1` is the usual iPhone hotspot address. On a regular LAN, use the phone's actual IP. The desktop window can open without the phone connected. For download failures, Python-version errors and an optional Qt window check, see [desktop installation and troubleshooting](docs/INSTALL_DESKTOP.md).

### 3. Record, upload and replay

1. On the phone, use **Start Experiment** to begin local recording.
2. Use **Stop & Save Experiment** to finalize the capture.
3. Transfer saved captures through **Past Records → Upload Data** with the desktop receiver running.
4. Select an experiment in the desktop workspace to inspect video, pose and available tactile streams.

Source runs store experiments in `uploads/` at the repository root. Packaged desktop tools store them in `uploads/` beside the executable. A typical dual-board capture contains:

```text
uploads/<experiment>/
├── video.mp4
├── ultrawide_video.mp4          # when recorded on a supported device
├── pose.csv
├── magnetic_right.csv          # when right-board samples are present
├── magnetic_left.csv           # when left-board samples are present
└── capture_manifest.json
```

### 4. Export a dataset

```powershell
.\.venv\Scripts\python.exe printtac.py export-zarr --capture "uploads/<experiment>" --out "dataset.zarr"
```

On macOS, replace `.\.venv\Scripts\python.exe` with `./.venv/bin/python`.

See the [export guide](docs/ZARR_EXPORT.md) for calibration, field definitions and action targets. Raw ARKit pose is a camera trajectory; applying it as a gripper/robot pose requires the appropriate calibration. Raw magnetic measurements are tactile observations, rather than calibrated force/torque values. Exported next-observation action targets are derived from demonstrations.

## Choose a tool

The shared entry point is `.\.venv\Scripts\python.exe printtac.py <tool>` on Windows, or `./.venv/bin/python printtac.py <tool>` on macOS. Append the tool arguments below. Use `--help` to inspect options, and run one listener per UDP port.

| Goal | Tool arguments |
| --- | --- |
| Live experiments, uploads and replay | `monitor` |
| View only the 3D pose trajectory | `visualizer` |
| Receive pose in a terminal | `receiver` |
| Run only the HTTP upload server | `upload-server` |
| Receive combined pose and tactile packets | `magnetic-receiver` |
| Inspect video / packet loss | `video-debugger` / `packet-loss` |
| Validate a recorded trajectory | `validator` |
| Open the Zarr export window | `zarr-exporter` |
| Configure serial sensors / track gripper aperture | `anyskin-serial` / `aruco-tracker` |
| Diagnose the desktop environment | `check-deps --gui` |

```powershell
.\.venv\Scripts\python.exe printtac.py --help
.\.venv\Scripts\python.exe printtac.py monitor --help
```

## Repository map

```text
printtac-capture/
├── printtac.py                 # shared desktop launcher
├── ios/                        # iPhone capture app and resources
├── desktop/                    # reception, replay and dataset processing
├── config/                     # sensor/camera/gripper calibration
├── scripts/                    # platform launchers and executable builds
├── tests/                      # automated regression tests
├── docs/                       # setup, protocols and workflow guides
├── project.yml                 # XcodeGen project definition
└── requirements_visualizer.txt # desktop dependencies
```

Detailed module responsibilities are listed in the [module map](docs/REPOSITORY_LAYOUT.zh-CN.md).

## Documentation

| Start here | Reference |
| --- | --- |
| [Desktop installation and troubleshooting](docs/INSTALL_DESKTOP.md) | |
| [iPhone installation](docs/INSTALL_IPHONE_APP.md) | [Architecture](docs/ARCHITECTURE.md) |
| [Network and sensor setup](docs/SETUP.md) | [Packet and recording protocols](docs/PROTOCOL.md) |
| [Magnetic capture](docs/HOTSPOT_MAGNETIC_CAPTURE.zh-CN.md) | [ArUco gripper integration](docs/ARUCO_GRIPPER_INTEGRATION.zh-CN.md) |
| [Zarr export](docs/ZARR_EXPORT.md) | [Calibration](docs/CALIBRATION_OVERVIEW.en.md) |
| [Detailed usage](docs/USAGE.md) | [Desktop executable builds](docs/BUILD.md) |

## Development

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -t .
```

On macOS, use `./.venv/bin/python`.

On a Mac, generate the iPhone project with `xcodegen generate` from the repository root. Build desktop executables with `.\scripts\build_windows.ps1` on Windows or `bash scripts/build_macos.sh` on macOS. See [contributing](CONTRIBUTING.md) for development guidance.

Current installations use `PrintTacCapture.xcodeproj` and `python printtac.py`. The old `arpose.py` entry point still forwards commands. For an iPhone upgrade that retains recordings, reuse the installed app's bundle identifier and signing team; see the [upgrade instructions](docs/INSTALL_IPHONE_APP.md#upgrade-an-existing-installation-safely).

## License

[MIT](LICENSE).
