"""Locations shared by source runs and standalone desktop executables."""

from pathlib import Path
import sys


def get_app_base_dir() -> Path:
    """Keep runtime data next to the executable or at the repository root."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def get_default_upload_dir() -> Path:
    return (get_app_base_dir() / "uploads").resolve()
