# SPDX-License-Identifier: GPL-3.0-or-later
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from pbi_linux import cli, common, launch


class LauncherTests(unittest.TestCase):
    def run_launcher(self, folder):
        """Run a copy of the launcher beside a planted src/pbi_linux that announces itself."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / 'src/pbi_linux'
            package.mkdir(parents=True)
            (package / '__init__.py').write_text('')
            (package / 'cli.py').write_text('def main():\n    print("PLANTED")\n    return 0\n')
            script = root / folder / 'pbi-linux'
            script.parent.mkdir()
            shutil.copy2(ROOT / 'packaging/pbi-linux', script)
            done = subprocess.run([sys.executable, str(script), '--version'], capture_output=True,
                                  text=True, timeout=30, env={'PATH': '/usr/bin:/bin'})
            return done.stdout

    def test_a_source_checkout_uses_its_own_code(self):
        self.assertIn('PLANTED', self.run_launcher('packaging'))

    def test_an_installed_launcher_ignores_a_neighbouring_src(self):
        # /usr/bin/pbi-linux must never load /usr/src/pbi_linux.
        self.assertNotIn('PLANTED', self.run_launcher('bin'))


class DesktopErrorTests(unittest.TestCase):
    def test_desktop_errors_are_plain_text(self):
        # A report's file name reaches the error text; zenity must not read it as markup (links).
        name = '<a href="https://example.invalid">report</a>.pbix'
        calls = []
        def run(args, **kwargs):
            calls.append(args)
        with patch.object(launch, 'open_file', side_effect=common.Error('Not found: ' + name)), \
                patch.object(cli.shutil, 'which', return_value='/usr/bin/zenity'), \
                patch.object(cli.subprocess, 'run', run), patch('sys.stderr'):
            self.assertEqual(cli.main(['open', '--desktop', name]), 1)
        self.assertEqual(len(calls), 1)
        self.assertIn('--no-markup', calls[0])
        self.assertIn('--text=Not found: ' + name, calls[0])


if __name__ == '__main__':
    unittest.main()
