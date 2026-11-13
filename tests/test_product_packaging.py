"""Verify packaging resources and existing capture compatibility after renaming."""

from pathlib import Path
import plistlib
import tempfile
import unittest
import os
import sys

import arpose
import printtac
from export_capture_to_zarr import discover_capture
from scripts.build_desktop import ROOT, build_arguments, build_environment, load_tools


class ProductPackagingTests(unittest.TestCase):
    def test_build_environment_selects_qt_and_native_windows_libraries(self):
        env = build_environment()
        self.assertEqual(env["QT_API"], "pyqt6")
        if sys.platform == "win32":
            self.assertEqual(Path(env["PATH"].split(os.pathsep)[0]), Path(os.environ["SystemRoot"]) / "System32")

    def test_legacy_launcher_uses_the_same_dispatcher(self):
        self.assertIs(arpose.main, printtac.main)
        self.assertIs(arpose.TOOLS, printtac.TOOLS)

    def test_every_packaged_tool_is_registered_and_has_a_source(self):
        tools = load_tools()
        self.assertEqual(len({tool["name"] for tool in tools}), len(tools))
        for tool in tools:
            with self.subTest(tool=tool["tool"]):
                self.assertEqual(printtac.TOOLS[tool["tool"]][0], tool["entry"])
                self.assertTrue((ROOT / "desktop" / tool["entry"]).is_file())
                self.assertTrue(tool["name"].startswith("PrintTac"))

    def test_build_uses_absolute_resource_paths_and_packages_both_configs(self):
        arguments = build_arguments(load_tools()[0])
        self.assertTrue(Path(arguments[-1]).is_absolute())
        self.assertTrue(Path(arguments[arguments.index("--icon") + 1]).is_file())
        data = [arguments[i + 1] for i, value in enumerate(arguments) if value == "--add-data"]
        for filename in ("umi_gripper_aruco.json", "ultrawide_intrinsics.json"):
            self.assertTrue(any(filename in item for item in data))

    def test_iphone_project_matches_its_entry_point_and_display_name(self):
        project = (ROOT / "project.yml").read_text(encoding="utf-8")
        self.assertTrue(project.startswith("name: PrintTacCapture\n"))
        self.assertIn("ios/PrintTacCaptureApp.swift", project)
        self.assertIn("struct PrintTacCaptureApp: App", (ROOT / "ios/PrintTacCaptureApp.swift").read_text())
        with (ROOT / "ios/Info.plist").open("rb") as stream:
            self.assertEqual(plistlib.load(stream)["CFBundleDisplayName"], "PrintTac Capture")

    def test_old_and_new_phone_video_names_remain_discoverable(self):
        for prefix in ("ARPoseStreamer", "PrintTacCapture"):
            with self.subTest(prefix=prefix), tempfile.TemporaryDirectory() as directory:
                # discover_capture resolves OS aliases in the temporary root.
                folder = Path(directory).resolve()
                (folder / "pose.csv").write_text("relative_time,x,y,z,qx,qy,qz,qw\n0,0,0,0,0,0,0,1\n")
                video = folder / f"{prefix}-recording.mp4"
                video.write_bytes(b"video-placeholder")
                self.assertEqual(discover_capture(folder).video_path, video)
