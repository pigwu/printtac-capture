#!/usr/bin/env python3
"""Install the desktop tools in a project-local environment, without activation."""
import argparse
import os
from pathlib import Path
import struct
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent.parent


def validate_python(version=None, bits=None):
    version = sys.version_info[:2] if version is None else version
    bits = struct.calcsize("P") * 8 if bits is None else bits
    if tuple(version) != (3, 12) or bits != 64:
        raise RuntimeError(
            "Use 64-bit Python 3.12. On Windows: py -3.12 scripts/setup_desktop.py; "
            "on macOS: python3.12 scripts/setup_desktop.py. See README.md."
        )


def environment_python(directory):
    return directory / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def run(command):
    print("\n> " + subprocess.list2cmdline([str(part) for part in command]), flush=True)
    subprocess.run([str(part) for part in command], check=True, cwd=ROOT)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index-url", help="Optional trusted package index; otherwise use pip's configured index.")
    args = parser.parse_args(argv)
    try:
        validate_python()
        directory = ROOT / ".venv"
        python = environment_python(directory)
        if directory.exists():
            if not (directory / "pyvenv.cfg").is_file() or not python.is_file():
                raise RuntimeError(".venv is incomplete. Rename it and rerun setup. No files were deleted.")
            result = subprocess.run(
                [str(python), "-I", "-c", "import sys, struct; print('%d.%d %d' % (*sys.version_info[:2], struct.calcsize('P') * 8))"],
                capture_output=True, text=True, check=True,
            )
            if result.stdout.strip() != "3.12 64":
                raise RuntimeError("Existing .venv is not 64-bit Python 3.12. Rename it and rerun setup.")
            print("Reusing " + str(directory), flush=True)
        else:
            print("Creating " + str(directory), flush=True)
            venv.EnvBuilder(with_pip=True).create(directory)
        index = ["--index-url", args.index_url] if args.index_url else []
        pip = [python, "-m", "pip", "--disable-pip-version-check"]
        run([*pip, "install", "--upgrade", "pip", *index])
        # Never fall back to compiling Qt, NumPy or PyAV on a user's machine.
        run([*pip, "install", "--only-binary=:all:", "-r", ROOT / "requirements_visualizer.txt", *index])
        run([*pip, "check"])
        run([python, ROOT / "printtac.py", "check-deps"])
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print("\n[FAILED] " + str(exc), file=sys.stderr)
        print("Fix the error above and rerun setup; the environment is retained for diagnosis.\n"
              "Download errors: check network/proxy settings or --index-url with a trusted mirror.\n"
              "No matching distribution: check Python 3.12 (64-bit), OS and mirror availability.\n"
              "Troubleshooting: docs/INSTALL_DESKTOP.md", file=sys.stderr)
        return 1
    print("\n[READY] Desktop dependencies passed. No activation is needed.")
    if os.name == "nt":
        print(r".\.venv\Scripts\python.exe printtac.py monitor --phone-ip 172.20.10.1")
    else:
        print("./.venv/bin/python printtac.py monitor --phone-ip 172.20.10.1")
    print("Optional Qt window check: use the same Python with printtac.py check-deps --gui")
    return 0


if __name__ == "__main__":
    sys.exit(main())
