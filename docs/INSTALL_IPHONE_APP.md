# Install PrintTac Capture on iPhone

The app requires an ARKit-capable iPhone running iOS 17 or newer, and a Mac with Xcode supporting the device's iOS version. Simultaneous primary/ultra-wide capture depends on the device's camera capabilities.

## Get the current repository

```bash
git clone https://github.com/pigwu/printtac-capture.git
cd printtac-capture
```

If you downloaded a ZIP, extract it and open Terminal in the directory containing `project.yml`. Its folder may be named `printtac-capture-main`. An existing checkout can keep its local directory name; use the current repository URL for its remote.

## Prepare Xcode

1. Install Xcode on the Mac and open it once to complete setup.
2. Install XcodeGen, for example with Homebrew:

```bash
brew install xcodegen
```

3. From the repository root, generate and open the current project:

```bash
xcodegen generate
open PrintTacCapture.xcodeproj
```

The generated project, target and scheme are **`PrintTacCapture`**. The installed home-screen name is **PrintTac Capture**. Use this generated project when following the current instructions.

## Signing and device installation

1. Select the `PrintTacCapture` project and `PrintTacCapture` target.
2. Open **Signing & Capabilities** and select your Apple signing team.
3. For a new installation, use a bundle identifier unique to your team. The source default is `com.example.PrintTacCapture`.
4. Connect and trust the iPhone, enable Developer Mode if requested, and select it as the run destination.
5. Run the `PrintTacCapture` scheme. Trust the developer profile in **Settings → General → VPN & Device Management** if required.
6. Allow camera and local-network access when opening PrintTac Capture.

An optional terminal build, after configuring signing, is:

```bash
xcodebuild -project PrintTacCapture.xcodeproj -scheme PrintTacCapture -destination 'generic/platform=iOS' build
```

Personal-team signing can expire and require rebuilding. This repository supplies source code; an iPhone install still requires Apple signing, rather than an unsigned IPA or a Windows EXE.

## Upgrade an existing installation safely

**Keep the same bundle identifier and signing team as the installed app when you need to retain its captures and settings.** Copy the existing identifier into `PRODUCT_BUNDLE_IDENTIFIER` in `project.yml` before regenerating the project. The new default identifier creates a separate app sandbox; changing the display name alone does not migrate data between sandboxes.

Upload or export important recordings before reinstalling. Install over the existing app with its original identifier; do not uninstall it first if you want its local recordings. Historical private preference keys are retained so an in-place upgrade can reuse settings. The new app writes `PrintTacCapture...` video names, while desktop tools continue to accept older recording names.

## First capture

- Follow [network and sensor setup](SETUP.md) to connect the configured right/left boards to the phone hotspot.
- Use **Start Experiment** and **Stop & Save Experiment** for local capture.
- Open `python printtac.py monitor` on the computer when you want uploads, live monitoring or replay.
- Upload saved experiments through **Past Records → Upload Data**.

The `com.example.sensor.pose` accessory protocol is a hardware integration placeholder, not the app's bundle identifier. Keep it aligned with the actual accessory protocol when using a wired sensor; see [setup](SETUP.md).
