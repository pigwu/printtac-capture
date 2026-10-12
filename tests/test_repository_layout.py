"""Catch path regressions caused by reorganizing source and entry points."""

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import printtac
import runtime_paths
from capture_upload_server import get_default_upload_dir
from udp_video_debug_ui import get_app_base_dir


ROOT = Path(__file__).resolve().parent.parent


class RepositoryLayoutTests(unittest.TestCase):
    def test_all_registered_tools_exist(self):
        for filename, _ in printtac.TOOLS.values():
            with self.subTest(tool=filename):
                self.assertTrue((ROOT / "desktop" / filename).is_file())

    def test_source_runtime_paths_keep_existing_data_and_configuration(self):
        self.assertEqual(get_app_base_dir(), ROOT)
        self.assertEqual(get_default_upload_dir(), ROOT / "uploads")
        self.assertTrue((get_app_base_dir() / "config/umi_gripper_aruco.json").is_file())

    def test_frozen_runtime_paths_use_executable_directory(self):
        executable = ROOT / "dist" / "monitor.exe"
        with patch.object(sys, "frozen", True, create=True), patch.object(sys, "executable", str(executable)):
            self.assertEqual(runtime_paths.get_app_base_dir(), executable.parent)
            self.assertEqual(runtime_paths.get_default_upload_dir(), executable.parent / "uploads")

    def test_dispatch_preserves_tool_options_and_user_paths(self):
        args = ["validator", "--arkit-csv", "my experiment/pose.csv", "--time-shift", "-0.5", "--help"]
        with patch.object(sys, "argv", ["printtac.py"]), patch.object(sys, "path", list(sys.path)), patch.object(printtac.runpy, "run_path") as run:
            printtac.main(args)
            entry = str(ROOT / "desktop/pose_tracking_validator.py")
            self.assertEqual(sys.argv, [entry, *args[1:]])
            run.assert_called_once_with(entry, run_name="__main__")

    def test_dispatch_rejects_unknown_tool_without_running_code(self):
        with patch.object(printtac.runpy, "run_path") as run, patch("sys.stderr"), self.assertRaises(SystemExit) as error:
            printtac.main(["unknown-tool"])
        self.assertEqual(error.exception.code, 2)
        run.assert_not_called()

    def test_gui_only_help_does_not_open_a_window(self):
        with patch.object(printtac.runpy, "run_path") as run, patch("sys.stdout"):
            printtac.main(["zarr-exporter", "--help"])
        run.assert_not_called()

    def test_project_sources_and_plist_exist(self):
        project = (ROOT / "project.yml").read_text(encoding="utf-8")
        sources = [line.split("- path: ", 1)[1].strip() for line in project.splitlines() if "- path: " in line]
        self.assertEqual(len(sources), 19)
        for source in sources:
            with self.subTest(source=source):
                self.assertTrue(source.startswith("ios/"))
                self.assertTrue((ROOT / source).exists())
        self.assertIn("INFOPLIST_FILE: ios/Info.plist", project)
        self.assertTrue((ROOT / "ios/Info.plist").is_file())


if __name__ == "__main__":
    unittest.main()
