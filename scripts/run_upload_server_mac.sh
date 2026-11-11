#!/bin/sh
cd "$(dirname "$0")/.." || exit 1
. ./scripts/desktop_python.sh
exec "$printtac_python" desktop/capture_upload_server.py --host 0.0.0.0 --port 8000
