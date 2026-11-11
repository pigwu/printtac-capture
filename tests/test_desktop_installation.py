"""Failure-path tests for installation and diagnosis; no network is needed."""
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from desktop import check_visualizer_deps as check

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('setup_desktop', ROOT / 'scripts/setup_desktop.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class InstallationFailureTests(unittest.TestCase):
    def test_rejects_unsupported_python_before_installing(self):
        for version, bits in [((3, 14), 64), ((3, 12), 32), ((3, 11), 64)]:
            with self.subTest(version=version, bits=bits):
                with self.assertRaisesRegex(RuntimeError, '64-bit Python 3.12'):
                    setup.validate_python(version, bits)

    def test_preserves_incomplete_environment(self):
        with tempfile.TemporaryDirectory(prefix='printtac setup ') as directory:
            root = Path(directory)
            (root / '.venv').mkdir()
            marker = root / '.venv/user-file'
            marker.write_text('preserve me')
            with patch.object(setup, 'ROOT', root), patch.object(setup, 'validate_python'), \
                 patch.object(setup, 'run') as run, redirect_stderr(io.StringIO()):
                self.assertEqual(setup.main([]), 1)
            self.assertEqual(marker.read_text(), 'preserve me')
            run.assert_not_called()

    def test_install_failure_never_reports_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = io.StringIO()
            with patch.object(setup, 'ROOT', root), patch.object(setup, 'validate_python'), \
                 patch.object(setup.venv.EnvBuilder, 'create'), \
                 patch.object(setup, 'run', side_effect=subprocess.CalledProcessError(1, ['pip'])), \
                 redirect_stdout(output), redirect_stderr(output):
                self.assertEqual(setup.main([]), 1)
            self.assertIn('[FAILED]', output.getvalue())
            self.assertNotIn('[READY]', output.getvalue())

    def test_native_crash_is_reported_and_remaining_checks_continue(self):
        output = io.StringIO()
        results = [subprocess.CompletedProcess([], 1, '', 'DLL load failed')]
        results.extend(subprocess.CompletedProcess([], 0, 'OK', '') for _ in range(len(check.PROBES) - 1))
        with patch.object(check.subprocess, 'run', side_effect=results) as run, \
             redirect_stdout(output):
            self.assertFalse(check.check_dependencies())
        self.assertEqual(run.call_count, len(check.PROBES))
        self.assertIn('DLL load failed', output.getvalue())
        self.assertNotIn('[READY]', output.getvalue())


if __name__ == '__main__':
    unittest.main()
