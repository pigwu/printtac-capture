# Source this helper after changing to the repository root.
printtac_python="./.venv/bin/python"
if [ ! -x "$printtac_python" ]; then
    echo "Desktop environment missing. Run: python3.12 scripts/setup_desktop.py" >&2
    exit 1
fi
