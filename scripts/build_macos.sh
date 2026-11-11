#!/bin/bash
set -euo pipefail
project_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$project_root"
. ./scripts/desktop_python.sh
exec "$printtac_python" "$project_root/scripts/build_desktop.py" "$@"
