#!/bin/bash
cd "$(dirname "$0")/.." || exit 1
python3 desktop/udp_pose_visualizer.py --host 0.0.0.0 --port 5555
