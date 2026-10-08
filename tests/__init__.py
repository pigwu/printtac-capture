"""Make desktop modules available during unittest discovery from the root."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "desktop"))
