"""B06/B07 synthetic orchestration and trusted replay tests."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from datainsight import profile as p
from datainsight.inspection import SourceRequest, AccessPolicy, validate_source, BoundaryError
from w1b_reference import generate, reference


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.fixture = tempfile.TemporaryDirectory(dir=p.ROOT / 'tests/fixtures')
        self.outputs = tempfile.TemporaryDirectory(dir=p.ROOT / 'outputs/W1-B')
        self.path = Path(self.fixture.name) / 'synthetic.csv'
        generate(self.path)
        self.source = validate_source(SourceRequest('synthetic', self.path, 'file', 'fixture'),
            AccessPolicy((), p.ROOT / 'tests/fixtures', p.ROOT / 'outputs/W1-B'))
        self.directory = Path(self.outputs.name) / 'original'
        p.run_profile(self.source, p.load_read_contract(), self.directory)

    def tearDown(self):
        self.fixture.cleanup()
        self.outputs.cleanup()

    def test_B06_semantics_and_B07_replay_all(self):
        expected = reference(self.path)
        profile = json.loads((self.directory / 'profile.json').read_text())
        for template, value in expected.items():
            self.assertEqual(profile['metrics'][template]['values'], value)
            result = p.replay_profile_evidence(self.directory / (template + '-evidence.json'),
                Path(self.outputs.name) / ('replay-' + template))
            self.assertTrue(result.consistent)
        self.assertEqual(profile['product_model_usage'], 'not_applicable')

    def test_B07_tampered_identity_before_query(self):
        path = self.directory / 'summary-evidence.json'
        original = json.loads(path.read_text())
        mutations = {'sql': 'SELECT secret', 'template_id': 'unknown', 'template_version': 'changed',
            'read_config_sha256': '0' * 64, 'parameters': ['outside'],
            'result_ref': '../outside.json', 'dataset_version': '0' * 64}
        for key, value in mutations.items():
            data = dict(original)
            data[key] = value
            path.write_text(json.dumps(data), encoding='utf-8')
            with patch.object(p, 'execute_profile_template') as execute:
                with self.assertRaises(BoundaryError):
                    p.replay_profile_evidence(path, Path(self.outputs.name) / 'rejected')
                execute.assert_not_called()
        path.write_text(json.dumps(original), encoding='utf-8')

    def test_B07_result_source_and_evidence_boundary(self):
        evidence = self.directory / 'summary-evidence.json'
        result = self.directory / 'summary-result.json'
        result.write_text('[{"row_count":999}]', encoding='utf-8')
        with patch.object(p, 'execute_profile_template') as execute:
            with self.assertRaises(BoundaryError):
                p.replay_profile_evidence(evidence, Path(self.outputs.name) / 'rejected')
            with self.assertRaises(BoundaryError):
                p.replay_profile_evidence(p.ROOT / 'unapproved.json', Path(self.outputs.name) / 'rejected')
            execute.assert_not_called()

    def test_B07_changed_source_before_query(self):
        self.path.write_bytes(b'changed,fixture,c,pv,1\n')
        with patch.object(p, 'execute_profile_template') as execute:
            with self.assertRaises(BoundaryError):
                p.replay_profile_evidence(self.directory / 'summary-evidence.json', Path(self.outputs.name) / 'rejected')
            execute.assert_not_called()

    def test_B07_file_bytes_whitespace_key_order_and_duplicates_before_query(self):
        path = self.directory / 'behaviours-result.json'
        original = path.read_bytes()
        data = json.loads(original)
        variants = [b' ' + original,
            json.dumps([dict(reversed(list(data[0].items())))], separators=(',', ':')).encode(),
            b'[{"pv":1,"pv":2}]']
        for payload in variants:
            path.write_bytes(payload)
            with patch.object(p, 'execute_profile_template') as execute:
                with self.assertRaises(BoundaryError) as raised:
                    p.replay_profile_evidence(self.directory / 'behaviours-evidence.json', Path(self.outputs.name) / 'rejected')
                self.assertEqual(raised.exception.code, 'result_digest_mismatch')
                execute.assert_not_called()
        path.write_bytes(original)

    def test_B07_all_output_references_resolve_and_fingerprints_match(self):
        self.assertTrue(p.verify_profile_references(self.directory)['references_resolvable'])
        for template in reference(self.path):
            target = Path(self.outputs.name) / ('references-' + template)
            p.replay_profile_evidence(self.directory / (template + '-evidence.json'), target)
            self.assertTrue(p.verify_profile_references(target)['references_resolvable'])
            replay = json.loads((target / 'replay.json').read_text())
            fingerprints = json.loads((target / 'fingerprints.json').read_text())
            for phase in ('before', 'after'):
                fp = replay['fingerprints'][phase]
                self.assertTrue((target / fp['evidence_ref']).is_file())
                self.assertEqual(fp, fingerprints[phase])

    def test_failed_run_has_no_success_profile(self):
        target = Path(self.outputs.name) / 'failed'
        with patch.object(p, 'execute_profile_template', side_effect=BoundaryError('controlled_failure')):
            with self.assertRaises(BoundaryError):
                p.run_profile(self.source, p.load_read_contract(), target)
        self.assertFalse((target / 'profile.json').exists())
        self.assertEqual(json.loads((target / 'failure.json').read_text())['status'], 'failed')
