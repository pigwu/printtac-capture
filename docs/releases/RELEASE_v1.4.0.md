# PrintTac Capture v1.4.0

PrintTac Capture now uses consistent repository, installation, application and executable names across the iPhone and desktop workflows.

## Changes

- Rename the generated iOS project, target and scheme to `PrintTacCapture`, and the installed app to PrintTac Capture.
- Introduce `python printtac.py` as the current desktop entry point; preserve the old command as a compatibility wrapper.
- Share one manifest for the eight Windows/macOS desktop build targets and resource paths.
- Update installation, signing, build, usage and upgrade documentation.
- Preserve old recordings, saved preference keys and cross-version single-instance behavior.

## Windows installation

Use `PrintTac-Capture.exe` for the integrated experiment monitor and replay workspace. Other PrintTac tools are listed in [BUILD.md](../BUILD.md). Place the application in a writable folder; experiments are saved in `uploads/` beside the executable.

These binaries replace older releases for the current workflow. Historical assets remain historical; changing their filenames would not update their code.

## iPhone and macOS

Build on a Mac using the [current iPhone instructions](../INSTALL_IPHONE_APP.md) or [desktop build guide](../BUILD.md). Reuse the installed iPhone app's signing identifier if you need an in-place upgrade that retains local data.

## Release asset names

- `PrintTac-Capture.exe`
- `PrintTac-Pose-Visualizer.exe`
- `PrintTac-Tracking-Validator.exe`
- `PrintTac-Packet-Loss-Monitor.exe`
- `PrintTac-Zarr-Exporter.exe`
- `PrintTac-AnySkin-UDP-Monitor.exe`
- `PrintTac-AnySkin-Serial-Mapper.exe`
- `PrintTac-Video-Debugger.exe`

`SHA256SUMS.txt` records checksums for the Windows executables.
