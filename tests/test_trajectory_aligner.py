"""CSV loading used by the trajectory alignment entry point."""

from pathlib import Path
import tempfile
import unittest

import numpy as np
from trajectory_aligner import load_iphone_csv, load_robot_csv


class TrajectoryCsvTests(unittest.TestCase):
    def test_loads_xyz_without_depending_on_column_order(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pose.csv"
            path.write_text("time,z,x,y\n0,3,1,2\n1,6,4,5\n", encoding="utf-8-sig")
            expected = np.array([[1, 2, 3], [4, 5, 6]], dtype=float)
            np.testing.assert_array_equal(load_iphone_csv(path), expected)
            np.testing.assert_array_equal(load_robot_csv(path), expected)

    def test_does_not_silently_accept_non_numeric_positions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pose.csv"
            path.write_text("x,y,z\ninvalid,1,2\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_iphone_csv(path)
