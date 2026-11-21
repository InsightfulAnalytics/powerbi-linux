# SPDX-License-Identifier: GPL-3.0-or-later
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


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


if __name__ == '__main__':
    unittest.main()
