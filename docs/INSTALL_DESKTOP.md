# Desktop installation / 电脑端安装

Start with the [English README](../README.md#quick-start) or [中文 README](../README.zh-CN.md#快速开始) for the complete capture workflow. This guide covers the Python desktop environment; building the iPhone app is a [separate step](INSTALL_IPHONE_APP.md).

## Supported installation

- **CPython 3.12, 64-bit.** Windows instructions target Windows 10/11 x64. macOS requires a system supported by the pinned Qt and scientific Python wheels; use a current macOS release. Windows ARM, 32-bit Python and other Python versions are not covered by this setup.
- Download the source ZIP and **extract it**, or clone the repository. Open a terminal in the folder containing `printtac.py` and `requirements_visualizer.txt`.
- Install Python 3.12 from [python.org](https://www.python.org/downloads/release/python-31210/): under **Files**, choose **Windows installer (64-bit)** or **macOS 64-bit universal2 installer**, not a source archive. Existing newer 3.12 patch releases are also accepted. It can coexist with another Python version. On Windows, include the Python launcher; confirm `py -3.12 --version`. On macOS, confirm `python3.12 --version`.
- Run setup from a normal terminal outside an activated Conda environment. No administrator account, CUDA, standalone FFmpeg, C/C++ compiler or environment activation is needed for the pinned binary dependencies.

Windows PowerShell:

```powershell
py -3.12 scripts/setup_desktop.py
.\.venv\Scripts\python.exe printtac.py check-deps --gui
.\.venv\Scripts\python.exe printtac.py monitor --phone-ip 172.20.10.1
```

macOS Terminal:

```bash
python3.12 scripts/setup_desktop.py
./.venv/bin/python printtac.py check-deps --gui
./.venv/bin/python printtac.py monitor --phone-ip 172.20.10.1
```

Setup must finish with **`[READY]`**. It installs into `.venv/`, checks package compatibility and exercises H.264 decoder creation, ArUco detection setup and a compressed Zarr write/read round trip. `check-deps --gui` additionally opens and closes a small Qt window; it requires a graphical desktop. These checks do not verify a phone, sensors, networking or actual OpenGL rendering.

Use the same `.venv` Python whenever you launch a tool or run a command from another guide. Other guides may abbreviate it as `python`; **do not substitute the global Python**. The Windows/macOS launcher scripts already select `.venv` and stop with an installation hint if it is missing.

## Downloads and retries

Rerun the setup command after a temporary network interruption. An existing compatible `.venv` is reused; capture data is not touched. Setup stops at errors and does not fall back to building native dependencies from source.

If your network requires a package mirror, select one you trust. For example, with the Tsinghua University PyPI mirror:

```powershell
py -3.12 scripts/setup_desktop.py --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

On macOS use `python3.12` instead of `py -3.12`. The option applies to pip itself and project dependencies for that run; it does not change global pip settings. Do not disable certificate verification to work around a proxy or TLS problem. A stale mirror may not contain all pinned wheels; try the default index or a different trusted mirror.

## Troubleshooting / 常见问题

| Symptom / 现象 | Action / 处理 |
| --- | --- |
| `py` is not recognized / 找不到 `py` | Install Python 3.12 with its launcher and reopen the terminal. Alternatively invoke the full path to a Python 3.12 executable. PowerShell paths with spaces need `& "C:\path to Python\python.exe" scripts/setup_desktop.py`. |
| `No suitable Python runtime found` / 找不到 3.12 | Installing a newer Python alone is insufficient. Install **3.12 64-bit** alongside it; confirm `py -3.12 --version`. |
| Setup rejects Python 3.14 or another version | Use `py -3.12` (Windows) or `python3.12` (macOS). The old unrestricted requirements could select a native source build for newer Python versions. |
| `No matching distribution found` | Confirm Python 3.12, 64-bit, a supported OS, and access to an up-to-date package index. Read the first failed package name. Do not remove the binary-only guard or randomly upgrade NumPy/Qt/Zarr. |
| `Building wheel`, C++ compiler errors from an old command | Stop using the old global `pip install` workflow. Run `scripts/setup_desktop.py` with Python 3.12; it uses prebuilt packages. |
| Timeout, SSL/TLS, proxy error / 下载失败 | Check internet/proxy/certificate settings, retry, or use `--index-url` with a trusted mirror. Installation needs internet access. |
| `.venv` incomplete or created with a different Python | Close all PrintTac tools, rename `.venv` to an unused backup name, then rerun setup. Do not delete `uploads/` or calibration files. |
| Installation succeeds but `ModuleNotFoundError` appears | Launch with `.\.venv\Scripts\python.exe` or `./.venv/bin/python`; installing in one environment and launching another does not work. |
| Qt DLL/platform-plugin errors | Run `check-deps --gui` from a normal terminal outside Conda. Remove only stale Qt/Python path overrides you deliberately configured. Recreate `.venv` if packages were mixed. Save the complete diagnostic output if the error persists. |
| Multiple OpenCV packages / `cv2.aruco` failure | Use a clean `.venv`. This project installs only `opencv-contrib-python-headless`; the other OpenCV distributions share the same `cv2` namespace and should not be installed alongside it. |
| Zarr/Blosc import or export failure | Rerun setup with the pinned Zarr 2 / Numcodecs versions. Do not upgrade this environment to Zarr 3. |
| PowerShell refuses a `.ps1` launcher | Use the direct `.venv\Scripts\python.exe printtac.py ...` command in the README. It does not require changing PowerShell's execution policy. |
| Window opens but no phone data arrives | Installation is complete; check the phone IP, hotspot/LAN, local-network permission and firewall rules in [network setup](SETUP.md). Close duplicate listeners on the same ports. |

### Recreate an incompatible environment without deleting data

Only rename the environment directory. Choose a different backup name if `.venv-backup` already exists.

```powershell
# Windows: close PrintTac first; run in the repository root
Rename-Item -LiteralPath .venv -NewName .venv-backup
py -3.12 scripts/setup_desktop.py
```

```bash
# macOS: close PrintTac first; run in the repository root
mv -n .venv .venv-backup
python3.12 scripts/setup_desktop.py
```

中文要点：安装固定使用 **Python 3.12（64 位）**；脚本会在项目目录创建独立环境，完成后显示 `[READY]`。以后直接使用 README 中的 `.venv` 启动命令，不用重复安装或激活。网络失败可重试或指定可信镜像；已有环境损坏时先关闭软件、将 `.venv` 改名备份再重新安装，**保留 `uploads/` 和标定文件**。

## Validation for maintainers

The previous `Python 3.10 or newer` instructions were reproduced on Windows with Python 3.14.3: Zarr 2 selected a Numcodecs source package, and installation failed with `Microsoft Visual C++ 14.0 or greater is required` / `Failed building wheel for numcodecs`. The Python 3.12 baseline and binary-only installation avoid that source-build path. Python versions outside this baseline may work with other dependency combinations, but are not advertised as supported by this installer.

Run these using the project environment, not the system interpreter:

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe printtac.py check-deps --gui
.\.venv\Scripts\python.exe printtac.py monitor --help
.\.venv\Scripts\python.exe -m unittest discover -s tests -t .
```

On macOS replace the executable with `./.venv/bin/python`. CI uses `QT_QPA_PLATFORM=offscreen` for a window-creation smoke check; a real display and physical capture still require manual verification. Keep Python, Qt, NumPy, OpenCV, PyAV and Zarr pins together when updating, and test a fresh installation on each target platform.
