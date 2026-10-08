#!/bin/sh
cd "$(dirname "$0")/.." || exit 1
python3 desktop/capture_upload_server.py --host 0.0.0.0 --port 8000
