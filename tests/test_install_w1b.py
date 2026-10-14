"""Installation policy flow tests: all install/import processes are mocked."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace

ROOT = Path('D:/MyPythonProjects/datainsight')
sys.path.insert(0, str(ROOT))
import install_w1b as installer


class InstallPolicyTests(unittest.TestCase):
    def effective(self):
        return {'temp': str(ROOT / '.cache/tmp'), 'uv_cache': str(ROOT / '.cache/uv'),
                'interpreter': str(installer.PYTHON)}

    def test_c_drive_cache_temp_target_refused_before_supervision(self):
        for key in ('temp', 'uv_cache', 'interpreter'):
            effective = self.effective()
            effective[key] = 'C:/controlled-mock-outside/target'
            with self.subTest(key=key), patch.object(installer, 'supervise') as supervise, patch.object(installer.subprocess, 'run') as imported:
                with self.assertRaisesRegex(RuntimeError, 'effective_path_mismatch'):
                    installer.install_once({}, effective, ROOT / 'outputs/W1-B/mock-not-created')
                supervise.assert_not_called()
                imported.assert_not_called()

    def test_wrong_version_stops_after_one_mock_install(self):
        self.check_invalid_import({'version': '0.0.0', 'module': str(ROOT / '.venv/Lib/site-packages/duckdb/__init__.py')})

    def test_outside_module_stops_after_one_mock_install(self):
        self.check_invalid_import({'version': '1.4.1', 'module': 'C:/controlled-mock-outside/duckdb/__init__.py'})

    def check_invalid_import(self, result):
        successful = {'parent_exit_status': 0, 'timeout': False, 'termination_confirmed': True}
        with patch.object(installer, 'supervise', return_value=successful) as supervise, patch.object(installer.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout=json.dumps(result))) as imported:
            record = installer.install_once({}, self.effective(), ROOT / 'outputs/W1-B/mock-not-created')
        self.assertFalse(record['import_valid'])
        self.assertEqual(record['installation_actions_started'], 1)
        supervise.assert_called_once()
        imported.assert_called_once()
        self.assertIn('duckdb==1.4.1', supervise.call_args.args[0])
        self.assertEqual(supervise.call_args.args[2], 300)
        # install_once returns failure to main(), whose existing exit policy is 2.
        self.assertEqual(0 if record.get('import_valid') else 2, 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
