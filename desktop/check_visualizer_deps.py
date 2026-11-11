#!/usr/bin/env python3
"""
Dependency and native-library smoke checks for the PrintTac desktop tools.
"""

import argparse
from importlib import metadata
import os
import struct
import subprocess
import sys


# Separate processes also report native-library crashes instead of losing the
# entire check (for example, when Qt cannot load a platform plugin).
PROBES = {
    "Qt": "from PyQt6 import QtCore, QtGui, QtWidgets; print(QtCore.QT_VERSION_STR)",
    "3D plotting": "import pyqtgraph.opengl; from OpenGL import GL; print('imports OK')",
    "Serial": "import serial; print(serial.__version__)",
    "NumPy / SciPy": "import numpy as np; from scipy.spatial.transform import Rotation; assert np.allclose(Rotation.identity().as_matrix(), np.eye(3)); print(np.__version__)",
    "Matplotlib": "import matplotlib; matplotlib.use('Agg'); from matplotlib.figure import Figure; Figure().subplots().plot([0, 1]); print(matplotlib.__version__)",
    "OpenCV / ArUco": "import cv2; cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50), cv2.aruco.DetectorParameters()); print(cv2.__version__)",
    "PyAV / H.264": "import av; av.CodecContext.create('h264', 'r'); print(av.__version__)",
    "Zarr / codecs": """
import tempfile
import numpy as np
import zarr
from numcodecs import Blosc
with tempfile.TemporaryDirectory() as directory:
    group = zarr.open_group(directory, mode='w')
    expected = np.arange(12, dtype=np.float32).reshape(4, 3)
    group.create_dataset('probe', data=expected, compressor=Blosc(cname='zstd'))
    np.testing.assert_array_equal(zarr.open_group(directory, mode='r')['probe'][:], expected)
print(zarr.__version__)
""",
}

GUI_PROBE = """
from PyQt6.QtWidgets import QApplication, QWidget
app = QApplication([])
window = QWidget()
window.setWindowTitle('PrintTac installation check')
window.show()
app.processEvents()
window.close()
print('Qt window created successfully')
"""


def check_dependencies(gui=False):
    print(f"Python: {sys.executable}\nVersion: {sys.version.split()[0]}", flush=True)
    all_ok = sys.version_info[:2] == (3, 12) and struct.calcsize('P') == 8
    if not all_ok:
        print('[FAIL] Supported installation uses 64-bit Python 3.12.')

    opencv = []
    for name in ('opencv-python', 'opencv-python-headless', 'opencv-contrib-python', 'opencv-contrib-python-headless'):
        try:
            metadata.version(name)
        except metadata.PackageNotFoundError:
            continue
        opencv.append(name)
    if len(opencv) > 1:
        print('[FAIL] Multiple packages share cv2: ' + ', '.join(opencv))
        print('       Recreate the project environment using scripts/setup_desktop.py.')
        all_ok = False

    env = dict(os.environ, QT_API='pyqt6', PYQTGRAPH_QT_LIB='PyQt6')
    probes = dict(PROBES)
    if gui:
        probes['Qt window'] = GUI_PROBE
    for name, source in probes.items():
        try:
            result = subprocess.run([sys.executable, '-c', source], env=env,
                                    capture_output=True, text=True, errors='replace', timeout=60)
            if result.returncode:
                detail = (result.stderr or result.stdout).strip()[-2500:]
                raise RuntimeError(f'exit {result.returncode}: {detail}')
            print(f'[OK]   {name}: {result.stdout.strip()}', flush=True)
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
            print(f'[FAIL] {name}: {exc}', flush=True)
            all_ok = False

    if all_ok:
        print('\n[READY] Desktop dependency checks passed.')
        print('Camera, network, sensor connections and OpenGL rendering require a separate device check.')
    else:
        print('\n[FAILED] Use Python 3.12 to run scripts/setup_desktop.py, then use the project .venv Python.')
        print('Troubleshooting: docs/INSTALL_DESKTOP.md')
    return all_ok


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check desktop dependencies, native libraries and export codecs.')
    parser.add_argument('--gui', action='store_true', help='Also briefly create a Qt window (requires a desktop session).')
    args = parser.parse_args()
    sys.exit(0 if check_dependencies(gui=args.gui) else 1)
