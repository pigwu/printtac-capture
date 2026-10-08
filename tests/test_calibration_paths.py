"""Default calibration lookup must be portable and optional."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import export_capture_to_zarr as exporter
from runtime_paths import get_app_base_dir


class CalibrationPathTests(unittest.TestCase):
    def test_default_is_in_application_config_directory(self):
        self.assertEqual(exporter.DEFAULT_EEF_CALIBRATION_RESULT,
                         get_app_base_dir() / "config/offline_calibration_result.json")

    def test_missing_calibration_keeps_raw_pose_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "calibration.json"
            with patch.object(exporter, "DEFAULT_EEF_CALIBRATION_RESULT", path):
                self.assertIsNone(exporter.default_eef_calibration_result())

    def test_existing_calibration_is_discovered(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "calibration.json"
            path.write_text("{}", encoding="utf-8")
            with patch.object(exporter, "DEFAULT_EEF_CALIBRATION_RESULT", path):
                self.assertEqual(exporter.default_eef_calibration_result(), path)
