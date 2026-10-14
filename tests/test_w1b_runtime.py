"""B08/B09 source-change and fixed CLI tests; no production reads."""
from dataclasses import replace
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from datainsight import profile as p
from datainsight import __main__ as cli
from datainsight.inspection import SourceRequest, AccessPolicy, validate_source, BoundaryError, FingerprintEvidence
from w1b_reference import generate


class RuntimeTests(unittest.TestCase):
    def test_production_baseline_mismatch_before_query(self):
        source = validate_source(SourceRequest('textbook_userbehavior', cli.PRODUCTION, 'file', 'contract'),
            AccessPolicy((cli.PRODUCTION,), p.ROOT / 'tests/fixtures', p.ROOT / 'outputs/W1-B'))
        fake = FingerprintEvidence('SHA-256', '0'*64, 'mock', 'mock', 0, 0, 'fingerprints.json')
        with patch.object(p, 'fingerprint_file', return_value=fake), patch.object(p, 'execute_profile_template') as query:
            with self.assertRaises(BoundaryError):
                p.run_profile(source, p.load_read_contract(), p.ROOT / 'outputs/W1-B/not-created')
            query.assert_not_called()

    def test_source_change_after_queries_fails_without_success_profile(self):
        with tempfile.TemporaryDirectory(dir=p.ROOT / 'tests/fixtures') as f, tempfile.TemporaryDirectory(dir=p.ROOT / 'outputs/W1-B') as o:
            path = Path(f) / 'synthetic.csv'
            generate(path)
            source = validate_source(SourceRequest('synthetic', path, 'file', 'fixture'), AccessPolicy((),p.ROOT/'tests/fixtures',p.ROOT/'outputs/W1-B'))
            original = p.fingerprint_file(source)
            target = Path(o) / 'failed'
            with patch.object(p, 'fingerprint_file', side_effect=[original, replace(original, sha256='0'*64)]):
                with self.assertRaises(BoundaryError):
                    p.run_profile(source, p.load_read_contract(), target)
            self.assertFalse((target/'profile.json').exists())
            self.assertEqual(json.loads((target/'failure.json').read_text())['status'], 'failed')

    def test_cli_replay_boundary_controlled_failure(self):
        args = SimpleNamespace(command='replay', evidence=p.ROOT/'unapproved.json', output_dir=p.ROOT/'outputs/W1-B/not-created')
        with patch.object(p, 'execute_profile_template') as query, patch('sys.stdout', new_callable=io.StringIO) as output:
            code = cli.profile_entry(args, [])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())['status'], 'failed')
        query.assert_not_called()
