#!/bin/bash
cd "$(dirname "$0")/.." || exit 1
. ./scripts/desktop_python.sh
exec "$printtac_python" desktop/udp_pose_visualizer.py --host 0.0.0.0 --port 5555
