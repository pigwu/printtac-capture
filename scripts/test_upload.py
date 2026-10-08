#!/usr/bin/env python3
"""Manually simulate a phone pose upload; start the upload server first."""

import json
import time
from urllib.request import Request, urlopen


def main() -> None:
    # Keep this sample in memory so an existing test_pose.csv is never replaced.
    rows = ["sequence,sender_time,frame_time,relative_time,x,y,z,qx,qy,qz,qw"]
    for i in range(1000):
        timestamp = time.time()
        rows.append(f"{i},{timestamp},{timestamp},0.0,0.5,0.3,0.8,0.0,0.0,0.0,1.0")
    data = ("\n".join(rows) + "\n").encode("utf-8")
    request = Request(
        "http://localhost:8000/upload",
        data=data,
        headers={
            "X-Capture-ID": "test-session-001",
            "X-Capture-Component": "pose",
            "X-Original-Filename": "pose.csv",
            "X-Upload-Kind": "pose",
        },
        method="POST",
    )
    print(f"Uploading {len(data) / 1024:.2f} KB to http://localhost:8000/upload ...")
    with urlopen(request, timeout=30) as response:
        result = json.load(response)
    print(f"Upload successful! Saved to: {result['saved_to']}")


if __name__ == "__main__":
    main()
