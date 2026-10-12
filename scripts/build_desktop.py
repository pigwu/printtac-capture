#!/usr/bin/env python3
"""Build the current desktop tools from one Windows/macOS product manifest."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "config/desktop_tools.json"


def load_tools():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def build_environment():
    env = dict(os.environ, QT_API="pyqt6")
    if sys.platform == "win32":
        # Qt uses the Windows ICU API. An unrelated Conda ICU with the same
        # DLL basename has versioned symbols and must not shadow System32.
        system_directory = Path(os.environ["SystemRoot"]) / "System32"
        env["PATH"] = str(system_directory) + os.pathsep + env.get("PATH", "")
    return env


def build_arguments(tool):
    arguments = [
        "--name", tool["name"], "--clean", "--noconfirm", "--windowed", "--onefile",
        "--specpath", str(ROOT / "build/specs"),
        "--workpath", str(ROOT / "build/pyinstaller"),
        "--distpath", str(ROOT / "dist"),
        "--paths", str(ROOT / "desktop"),
        "--icon", str(ROOT / "ios/Assets.xcassets/AppIcon.appiconset/Icon-1024.png"),
    ]
    for source, destination in (
        ("requirements_visualizer.txt", "."),
        ("config/umi_gripper_aruco.json", "config"),
        ("config/ultrawide_intrinsics.json", "config"),
    ):
        arguments += ["--add-data", f"{ROOT / source}{os.pathsep}{destination}"]
    for module in ("OpenGL", "OpenGL.GL", "OpenGL.GLU", "OpenGL.GLUT", "pyqtgraph.opengl"):
        arguments += ["--hidden-import", module]
    for module in ("PyQt5", "PySide2", "PySide6", "torch", "pandas", "IPython", "jupyter", "notebook", "sympy", "tkinter"):
        arguments += ["--exclude-module", module]
    for module in tool.get("collect", []):
        arguments += ["--collect-all", module]
    arguments.append(str(ROOT / "desktop" / tool["entry"]))
    return arguments


def main():
    tools = load_tools()
    parser = argparse.ArgumentParser(description="Build PrintTac desktop executables on the current platform.")
    parser.add_argument("--tool", choices=["all", *(tool["tool"] for tool in tools)], default="all")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print build commands without installing or building.")
    args = parser.parse_args()
    selected = tools if args.tool == "all" else [tool for tool in tools if tool["tool"] == args.tool]
    if not args.dry_run and importlib.util.find_spec("PyInstaller") is None:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "pillow"], check=True)
    env = build_environment()
    for tool in selected:
        command = [sys.executable, "-m", "PyInstaller", *build_arguments(tool)]
        if not Path(command[-1]).is_file():
            raise FileNotFoundError(command[-1])
        if args.dry_run:
            print(subprocess.list2cmdline(command))
        else:
            subprocess.run(command, cwd=ROOT, env=env, check=True)
            suffix = ".exe" if sys.platform == "win32" else ".app" if sys.platform == "darwin" else ""
            print(f"Built: {ROOT / 'dist' / (tool['name'] + suffix)}")


if __name__ == "__main__":
    main()
