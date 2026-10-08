# ARPoseStreamer

Capture ARKit pose, video and optional dual magnetic sensor streams on an iPhone. Monitor, upload, replay and export experiments on a Windows or macOS computer.

[简体中文](README.zh-CN.md) · [Detailed usage](docs/USAGE.md) · [Install the iPhone app](docs/INSTALL_IPHONE_APP.md)

## Quick start

Run from the repository root:

```bash
python -m pip install -r requirements_visualizer.txt
python arpose.py monitor --phone-ip 172.20.10.1
```

Replace the phone IP when using a normal LAN instead of the iPhone hotspot. The iPhone app requires Xcode building and signing on a Mac; see the [installation guide](docs/INSTALL_IPHONE_APP.md).

For pose visualization only:

```bash
python arpose.py visualizer
```

Set the app's Host IP to the computer's IP and pose port to `5555`, then start streaming. Use Start Experiment / Stop & Save Experiment for capture. On macOS use `python3`. Run one listener per UDP port.

## Desktop tools

Use `python arpose.py <tool>`; all original tool options are forwarded.

| Task | Tool |
| --- | --- |
| Live experiments, uploads and synchronized replay | `monitor` |
| 3D trajectory | `visualizer` |
| Command-line pose reception | `receiver` |
| HTTP upload server | `upload-server` |
| Combined pose and magnetic reception | `magnetic-receiver` |
| Video diagnostics / packet loss | `video-debugger` / `packet-loss` |
| Offline trajectory validation | `validator` |
| Zarr export | `zarr-exporter` / `export-zarr` |
| AnySkin serial / UDP monitoring | `anyskin-serial` / `anyskin-monitor` |
| ArUco gripper tracking | `aruco-tracker` |

```bash
python arpose.py --help
python arpose.py monitor --help
python arpose.py receiver --host 0.0.0.0 --port 5555 --encoding binary
```

## Repository layout

| Location | Contents |
| --- | --- |
| `arpose.py` | Shared desktop entry point |
| `ios/` | iPhone Swift sources, Info.plist and app icons |
| `desktop/` | Desktop tools and shared processing modules |
| `config/` | ArUco and camera calibration configuration |
| `scripts/` | Platform launchers and executable build scripts |
| `tests/` | Automated tests |
| `docs/` | Setup, architecture, protocols, calibration and release notes |
| `project.yml` | XcodeGen configuration, run from the repository root |

Experiments still use `uploads/` at the repository root, or next to a standalone executable. Existing data stays in place. Build output, logs and datasets are ignored local artifacts.

## Development

```powershell
# Windows executable build
.\scripts\build_windows.ps1
```

```bash
# macOS executable build
./scripts/build_macos.sh

# Generate the iPhone project on a Mac
xcodegen generate

# Run automated tests from the repository root
python -m unittest discover -s tests -t .
```

Launchers moved to `scripts/`. Direct source commands now use `python desktop/<filename>.py`, or the shared entry point above. See the [module map](docs/REPOSITORY_LAYOUT.zh-CN.md) and [build guide](docs/BUILD.md).

## Further reading

[Setup](docs/SETUP.md) · [Architecture](docs/ARCHITECTURE.md) · [Protocol](docs/PROTOCOL.md) · [Magnetic capture](docs/HOTSPOT_MAGNETIC_CAPTURE.zh-CN.md) · [Zarr export](docs/ZARR_EXPORT.md) · [Calibration](docs/CALIBRATION_OVERVIEW.en.md)

MIT License. See [contributing](CONTRIBUTING.md) for development guidelines.
