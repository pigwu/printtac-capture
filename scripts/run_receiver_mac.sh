#!/bin/sh
cd "$(dirname "$0")/.." || exit 1
. ./scripts/desktop_python.sh
exec "$printtac_python" desktop/udp_pose_receiver.py --host 0.0.0.0 --port 5555 --encoding binary
