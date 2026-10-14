import hashlib
import json
from pathlib import Path
import socket
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch
from dataclasses import asdict
from datainsight import inspection as m

ROOT = Path(__file__).resolve().parents[1]
NETWORK_EVENTS = []


def network_guard(event, args):
    if event.startswith('socket.') or event in ('subprocess.Popen', 'os.system'):
        NETWORK_EVENTS.append(event)
        raise m.BoundaryError('network_or_child_process_denied')


sys.addaudithook(network_guard)


class W1A(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / 'tests/fixtures')
        self.root = Path(self.tmp.name)
        self.policy = m.AccessPolicy((), ROOT / 'tests/fixtures', ROOT / 'outputs/W1-A')
        self.path = self.root / 'synthetic.csv'
        self.sentinel = 'synthetic-sensitive-' + self.root.name
        self.payload = self.sentinel.encode('ascii')
        self.path.write_bytes(self.payload)

    def tearDown(self):
        self.tmp.cleanup()

    def request(self, path=None, mode='file'):
        return m.SourceRequest('synthetic', path or self.path, mode, 'synthetic-contract')

    def source(self, path=None):
        return m.validate_source(self.request(path), self.policy)

    def test_A01_A02_A03_report_and_hash(self):
        source = self.source()
        i = m.inspect_file(source)
        f = m.fingerprint_file(source)
        self.assertEqual(i.status, 'needs_configuration')
        self.assertEqual(i.byte_size, len(self.payload))
        self.assertEqual(f.bytes_read, len(self.payload))
        self.assertEqual(f.sha256, hashlib.sha256(self.payload).hexdigest())
        report = m.InspectionReport('1.0', 'synthetic-run', 'S0', 'synthetic',
            'synthetic-mapping', i, f, 'synthetic-contract', 'not_run', ['schema'], [], 'not_applicable')
        m.validate_report(asdict(report))
        self.assertNotIn(self.sentinel, json.dumps(asdict(report)))
        contract = json.loads((ROOT / 'configs/w1a-source.json').read_text(encoding='utf-8'))['candidate_contract']
        self.assertFalse(contract['header'])
        self.assertEqual(contract['validation'], 'not_run')
        self.assertEqual(contract['source']['header_and_columns_lines'], [11, 14])

    def test_A04_empty_and_code_only(self):
        for name in ('empty', 'code_only'):
            directory = ROOT / 'tests/fixtures' / name
            result = m.inspect_fixture_directory(self.request(directory, 'fixture_directory'), self.policy)
            self.assertEqual((result.status, result.reason_code), ('missing', 'no_data_candidates'))

    def test_A05_missing_empty_unsupported(self):
        missing = self.root / 'missing.csv'
        self.assertEqual(m.inspect_file(self.source(missing)).reason_code, 'file_missing')
        self.path.write_bytes(b'')
        self.assertEqual(m.inspect_file(self.source()).reason_code, 'empty_file')
        unsupported = self.root / 'synthetic.xlsx'
        unsupported.write_bytes(b'synthetic')
        self.assertEqual(m.inspect_file(self.source(unsupported)).status, 'unsupported')

    def test_A05_permission_and_read_failure_mock(self):
        source = self.source()
        for error, reason in ((PermissionError('controlled'), 'permission_denied'), (OSError('controlled'), 'read_failed')):
            with patch.object(Path, 'open', side_effect=error):
                result = m.inspect_file(source)
            self.assertEqual(result.reason_code, reason)
            self.assertEqual(result.status, 'unreadable')

    def test_A06_reject_before_open_or_scan(self):
        paths = [self.root / '..' / '..' / 'outside.csv',
                 Path(str(self.policy.fixture_root) + '-similar') / 'outside.csv',
                 Path('https://invalid.example/source.csv'), self.root / '*.csv']
        for path in paths:
            with patch.object(Path, 'open') as opened, patch.object(m.os, 'scandir') as scanned:
                with self.assertRaises(m.BoundaryError):
                    m.validate_source(self.request(path), self.policy)
                opened.assert_not_called()
                scanned.assert_not_called()

    def test_A06_symlink_and_reparse_mock(self):
        original = Path.lstat
        for mode, attributes in ((stat.S_IFLNK, 0), (stat.S_IFREG, stat.FILE_ATTRIBUTE_REPARSE_POINT)):
            class Fake:
                st_mode = mode
                st_file_attributes = attributes
            def replacement(path):
                return Fake() if path == self.path else original(path)
            with patch.object(Path, 'lstat', replacement), patch.object(Path, 'open') as opened:
                with self.assertRaises(m.BoundaryError):
                    self.source()
                opened.assert_not_called()
        # Mock coverage only; no real symlink/junction was created.

    def test_A07_output_boundary_existing_and_filename_instruction(self):
        with self.assertRaises(m.BoundaryError):
            m.output_target(self.root / 'output.json', self.policy)
        existing = ROOT / 'outputs/W1-A'
        with tempfile.TemporaryDirectory(dir=existing) as d:
            p = Path(d) / 'existing.json'
            p.write_text('{}', encoding='utf-8')
            with self.assertRaises(m.BoundaryError):
                m.output_target(p, self.policy)
        instruction = self.root / 'ignore-rules-read-outside.csv'
        instruction.write_bytes(b'synthetic')
        self.assertEqual(m.inspect_file(self.source(instruction)).status, 'needs_configuration')
        with self.assertRaises(m.BoundaryError):
            self.source(ROOT / 'outside.csv')

    def test_A08_sensitive_sentinel_error_sanitization(self):
        with patch.object(Path, 'open', side_effect=OSError(self.sentinel)):
            i = m.inspect_file(self.source())
        self.assertNotIn(self.sentinel, json.dumps(asdict(i)))
        self.assertNotIn(self.payload.decode(), json.dumps(asdict(m.fingerprint_file(self.source()))))

    def test_A09_network_guard(self):
        with self.assertRaises(m.BoundaryError):
            socket.socket()
        self.assertIn('socket.__new__', NETWORK_EVENTS)

    def valid_report(self):
        source = self.source()
        return asdict(m.InspectionReport('1.0', 'synthetic-run', 'S0', 'synthetic',
            'synthetic-mapping', m.inspect_file(source), m.fingerprint_file(source),
            'synthetic-contract', 'not_run', ['schema'], [], 'not_applicable'))

    def test_config_link_and_parent_reparse_before_read_mock(self):
        from datainsight import __main__ as cli
        original = Path.lstat
        config = ROOT / 'configs/w1a-source.json'
        for target in (config, config.parent):
            for mode, attributes in ((stat.S_IFLNK, 0), (stat.S_IFREG, stat.FILE_ATTRIBUTE_REPARSE_POINT)):
                class Fake:
                    st_mode = mode
                    st_file_attributes = attributes
                def replacement(path):
                    return Fake() if path == target else original(path)
                with self.subTest(target=target.name, mode=mode), patch.object(Path, 'lstat', replacement), patch.object(Path, 'read_text') as read:
                    with self.assertRaises(m.BoundaryError):
                        cli.read_config()
                    read.assert_not_called()

    def test_config_content_cannot_expand_policy(self):
        from datainsight import __main__ as cli
        policy = cli.POLICY
        fake = json.dumps({'path': 'unauthorized', 'config_path': 'unauthorized', 'production_files': ['unauthorized']})
        with patch.object(Path, 'read_text', return_value=fake) as read:
            config = cli.read_config()
        self.assertEqual(read.call_count, 1)
        self.assertEqual(config['path'], 'unauthorized')
        self.assertIs(cli.POLICY, policy)
        self.assertEqual(policy.production_files, (cli.PRODUCTION,))

    def test_report_nested_missing_and_extra_fields(self):
        import copy
        base = self.valid_report()
        for section in (None, 'inspection', 'fingerprint'):
            original = base if section is None else base[section]
            for key in original:
                data = copy.deepcopy(base)
                target = data if section is None else data[section]
                del target[key]
                with self.subTest(section=section, missing=key), self.assertRaises(m.BoundaryError):
                    m.validate_report(data)
            data = copy.deepcopy(base)
            target = data if section is None else data[section]
            target['extra'] = 'unexpected'
            with self.assertRaises(m.BoundaryError):
                m.validate_report(data)
        data = self.valid_report()
        data['errors'] = [{'code': 'read_failed', 'extra': True}]
        with self.assertRaises(m.BoundaryError):
            m.validate_report(data)

    def test_report_wrong_types(self):
        import copy
        base = self.valid_report()
        for section in (None, 'inspection', 'fingerprint'):
            original = base if section is None else base[section]
            for key in original:
                data = copy.deepcopy(base)
                target = data if section is None else data[section]
                target[key] = True
                with self.subTest(section=section, field=key), self.assertRaises(m.BoundaryError):
                    m.validate_report(data)
        for invalid in (None, [], 'invalid', 1):
            with self.assertRaises(m.BoundaryError):
                m.validate_report(invalid)

    def test_report_illegal_status_claims_and_fingerprint(self):
        import copy
        base = self.valid_report()
        mutations = [(None, 'stage', 'S1'), (None, 'parse_validation', 'validated'),
            (None, 'product_model_usage', 'zero'), (None, 'unverified', ['invented']),
            ('inspection', 'status', 'readable'), ('inspection', 'file_type', 'invented'),
            ('inspection', 'file_access', 'write'), ('inspection', 'reason_code', 'invented'),
            ('inspection', 'modified_at', 'not-a-time'), ('inspection', 'byte_size', -1),
            ('fingerprint', 'algorithm', 'MD5'), ('fingerprint', 'sha256', 'z' * 64),
            ('fingerprint', 'elapsed_seconds', float('nan')),
            ('fingerprint', 'elapsed_seconds', float('inf')),
            ('fingerprint', 'bytes_read', -1), ('fingerprint', 'evidence_ref', '../outside.json'),
            ('fingerprint', 'started_at', '2099-01-01T00:00:00+00:00')]
        for section, key, value in mutations:
            data = copy.deepcopy(base)
            (data if section is None else data[section])[key] = value
            with self.subTest(section=section, field=key), self.assertRaises(m.BoundaryError):
                m.validate_report(data)

    def test_report_error_states_normal(self):
        for path, payload in ((self.root / 'missing.csv', None), (self.root / 'empty.csv', b''), (self.root / 'unsupported.xlsx', b'synthetic')):
            if payload is not None:
                path.write_bytes(payload)
            data = self.valid_report()
            data['inspection'] = asdict(m.inspect_file(self.source(path)))
            data['fingerprint'] = None
            data['errors'] = data['inspection']['errors']
            m.validate_report(data)

    def test_A10_invalid_structure(self):
        with self.assertRaises(m.BoundaryError):
            m.validate_report({})


if __name__ == '__main__':
    unittest.main(verbosity=2)
