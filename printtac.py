#!/usr/bin/env python3
"""One entry point for the desktop tools; run from the repository directory."""

from __future__ import annotations

import argparse
from pathlib import Path
import runpy
import sys


TOOLS = {
    "monitor": ("experiment_replay_ui.py", "Live capture monitor and experiment replay"),
    "visualizer": ("udp_pose_visualizer.py", "3D pose visualization"),
    "receiver": ("udp_pose_receiver.py", "Command-line pose receiver"),
    "upload-server": ("capture_upload_server.py", "HTTP capture upload server"),
    "magnetic-receiver": ("pose_magnetic_receiver.py", "Combined pose and magnetic receiver"),
    "video-debugger": ("udp_video_debug_ui.py", "Video stream diagnostics"),
    "packet-loss": ("udp_packet_loss_monitor.py", "UDP packet loss monitor"),
    "validator": ("pose_tracking_validator.py", "Offline trajectory validation"),
    "zarr-exporter": ("zarr_exporter_ui.py", "Zarr export window"),
    "export-zarr": ("export_capture_to_zarr.py", "Command-line Zarr export"),
    "anyskin-monitor": ("anyskin_udp_monitor.py", "AnySkin UDP monitor"),
    "anyskin-serial": ("anyskin_serial_mapper.py", "AnySkin serial mapper"),
    "anyskin-sender": ("anyskin_hotspot_sender.py", "Simulated AnySkin hotspot sender"),
    "aruco-tracker": ("aruco_gripper_tracker.py", "ArUco gripper tracker"),
    "aruco-receiver": ("aruco_robot_pose_receiver.py", "ArUco robot pose receiver"),
    "align-trajectory": ("trajectory_aligner.py", "Offline trajectory alignment"),
    "export-transform": ("export_transform_matrix.py", "Export calibration transform"),
    "check-deps": ("check_visualizer_deps.py", "Check visualization dependencies"),
}


def main(argv: list[str] | None = None) -> None:
    arguments = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(
        description="PrintTac Capture desktop tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Tools:\n" + "\n".join(
            f"  {name:20} {description}" for name, (_, description) in TOOLS.items()
        ) + "\n\nUse python printtac.py <tool> --help for tool options.",
    )
    parser.add_argument("tool", metavar="TOOL", choices=TOOLS, help="Desktop tool to launch (see below)")
    # Parse only the tool name. All remaining arguments belong to that tool,
    # including --help, paths with spaces, and options with negative values.
    args = parser.parse_args(arguments[:1])
    if args.tool in {"zarr-exporter", "export-transform", "check-deps"} and arguments[1:] in (["--help"], ["-h"]):
        print(f"{TOOLS[args.tool][1]}\nUsage: python printtac.py {args.tool}\nThis tool has no command-line options.")
        return
    desktop_dir = Path(__file__).resolve().parent / "desktop"
    entry = desktop_dir / TOOLS[args.tool][0]
    sys.path.insert(0, str(desktop_dir))
    sys.argv = [str(entry), *arguments[1:]]
    runpy.run_path(str(entry), run_name="__main__")


if __name__ == "__main__":
    main()
