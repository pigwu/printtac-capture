# Repository metadata

## Repository name

`printtac-capture`

Display title: **PrintTac Capture**.

## Description

Phone-first multimodal demonstration collection for PrintTac: iOS recording, tactile/vision/pose replay, calibration and Zarr export.

## Homepage

https://peppasaur.github.io/PrintTac/

## Topics

`printtac`, `tactile-sensing`, `robot-learning`, `demonstration-learning`, `umi`, `arkit`, `ios`, `multimodal`, `data-collection`, `zarr`

## Social preview

Use `docs/assets/printtac-capture.svg` as the source for a preview image. It describes the implemented capture-to-dataset workflow without author names, affiliations or personal contact details.

## Current product names

Repository: `printtac-capture`. Display title: **PrintTac Capture**. The iOS project/target/scheme is `PrintTacCapture`; the entry point is `ios/PrintTacCaptureApp.swift`; the installed app is **PrintTac Capture**. The canonical desktop command is `python printtac.py`, and executable names are defined in `config/desktop_tools.json`.

`arpose.py` remains a compatibility entry point. Private persisted preference keys, the cross-version monitor lock and old recording-name input patterns remain intentionally readable for upgrades. Historical release artifacts keep their original version names. See [iPhone installation](INSTALL_IPHONE_APP.md) for preserving the bundle identifier and local data during an upgrade.
