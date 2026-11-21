# SPDX-License-Identifier: GPL-3.0-or-later
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
from pbi_linux import common, patches

CONFIG = (b'<?xml version="1.0" encoding="utf-8"?>\r\n<configuration>\r\n'
          b'  <startup useLegacyV2RuntimeActivationPolicy="true">\r\n'
          b'    <supportedRuntime version="v4.0" sku=".NETFramework,Version=v4.7.2" />\r\n'
          b'  </startup>\r\n  <runtime>\r\n'
          b'    <assemblyBinding xmlns="urn:schemas-microsoft-com:asm.v1" />\r\n'
          b'  </runtime>\r\n</configuration>\r\n')


class DesktopConfigTests(unittest.TestCase):
    def test_manager_is_named_first_in_the_runtime_section(self):
        patched = patches.patch_config(CONFIG)
        self.assertEqual(patched, CONFIG.replace(
            b'  <runtime>\r\n',
            b'  <runtime>\r\n'
            b'    <appDomainManagerAssembly value="PowerBICompositionManager" />\r\n'
            b'    <appDomainManagerType value="CompositionManager" />\r\n'))

    def test_line_endings_follow_the_file(self):
        source = CONFIG.replace(b'\r\n', b'\n')
        self.assertNotIn(b'\r', patches.patch_config(source))

    def test_unexpected_configurations_are_refused(self):
        for source in (patches.patch_config(CONFIG),
                       CONFIG.replace(b'  <runtime>\r\n', b''),
                       CONFIG.replace(b'</configuration>', b'<runtime>\r\n</runtime></configuration>')):
            with self.assertRaises(common.Error):
                patches.patch_config(source)


    def test_a_short_copy_is_refused(self):
        # An interrupted backup keeps the <runtime> line but no longer parses.
        with self.assertRaisesRegex(common.Error, 'Incomplete or damaged Desktop configuration'):
            patches.patch_config(CONFIG[:CONFIG.index(b'</runtime>')])

    def test_backup_is_renamed_into_place_only_when_complete(self):
        import tempfile
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            source, backup = Path(directory) / 'source', Path(directory) / 'originals' / 'name'
            source.write_bytes(CONFIG)
            def interrupted(src, dst):
                Path(dst).write_bytes(CONFIG[:10])
                raise KeyboardInterrupt
            with patch.object(patches.shutil, 'copy2', side_effect=interrupted):
                with self.assertRaises(KeyboardInterrupt):
                    patches._backup(source, backup)
            self.assertFalse(backup.exists())
            patches._backup(source, backup)
            self.assertEqual(backup.read_bytes(), CONFIG)
            self.assertEqual(sorted(p.name for p in backup.parent.iterdir()), ['name'])

if __name__ == '__main__':
    unittest.main()
