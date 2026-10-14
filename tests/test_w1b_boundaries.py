"""B04/B05 bounded-entry tests; no production or unauthorized file reads."""
from dataclasses import asdict
import json
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from datainsight import profile as p
from datainsight.profile_templates import ProfileTemplateId as T, FIELDS
from datainsight.inspection import AccessPolicy, SourceRequest, ValidatedSource, validate_source, BoundaryError


class ProfileBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=p.ROOT / 'tests/fixtures')
        self.path = Path(self.tmp.name) / 'controlled.csv'
        self.path.write_bytes(b'controlled-user,controlled-goods,controlled-category,controlled-unknown,1\n')
        self.policy = AccessPolicy((), p.ROOT / 'tests/fixtures', p.ROOT / 'outputs/W1-B')
        self.source = validate_source(SourceRequest('synthetic', self.path, 'file', 'fixture'), self.policy)
        self.contract = p.load_read_contract()

    def tearDown(self):
        self.tmp.cleanup()

    def test_B04_invalid_source_and_forged_policy_before_query(self):
        outside = p.ROOT / 'outside-mock.csv'
        fake = ValidatedSource(SourceRequest('fake', outside, 'file', 'fake'), outside,
                               AccessPolicy((outside,), p.ROOT, p.ROOT))
        inconsistent = ValidatedSource(self.source.request, outside, self.policy)
        for source in (fake, inconsistent, None):
            with patch.object(p, 'connect_profile') as connect, patch.object(Path, 'open') as opened:
                with self.assertRaises(BoundaryError):
                    p.execute_profile_template(T.SUMMARY, source, self.contract)
                connect.assert_not_called()
                opened.assert_not_called()

    def test_B04_unknown_template_extra_sql_and_illegal_contract(self):
        with patch.object(p, 'connect_profile') as connect:
            for template in ('summary', 'SELECT *', None, {'sql': 'untrusted'}):
                with self.assertRaises(BoundaryError):
                    p.execute_profile_template(template, self.source, self.contract)
            with self.assertRaises(TypeError):
                p.execute_profile_template(T.SUMMARY, self.source, self.contract, sql='untrusted')
            with self.assertRaises(BoundaryError):
                p.execute_profile_template(T.SUMMARY, self.source, p.ValidatedReadContract('{}'))
            for extra in ('sql', 'path', 'template_directory'):
                data = dict(p.EXPECTED)
                data[extra] = 'untrusted'
                with self.assertRaises(BoundaryError):
                    contract = p.validate_read_contract(p.ReadContract(data))
                    p.execute_profile_template(T.SUMMARY, self.source, contract)
            connect.assert_not_called()

    def test_B04_actual_config_component_mock_before_read(self):
        original = Path.lstat
        for target in (p.CONTRACT_PATH, p.CONTRACT_PATH.parent):
            for mode, attributes in ((stat.S_IFLNK, 0), (stat.S_IFREG, stat.FILE_ATTRIBUTE_REPARSE_POINT)):
                class Fake:
                    st_mode = mode
                    st_file_attributes = attributes
                def replacement(path):
                    return Fake() if path == target else original(path)
                with patch.object(Path, 'lstat', replacement), patch.object(Path, 'read_text') as read, patch.object(p, 'connect_profile') as connect:
                    with self.assertRaises(BoundaryError):
                        contract = p.load_read_contract()
                        p.execute_profile_template(T.SUMMARY, self.source, contract)
                    read.assert_not_called()
                    connect.assert_not_called()

    def test_B05_result_limits_and_structure_rejected_in_execution(self):
        cases = [([(1,)] * 101, 'profile_result_row_boundary'),
                 ([('x' * 65536,)], 'profile_result_byte_boundary'),
                 ([({'nested': 1},)], 'profile_result_type'),
                 ([(True,)], 'profile_result_type'),
                 ([(float('nan'),)], 'profile_result_invalid')]
        for returned, reason in cases:
            connection = MagicMock()
            cursor = connection.execute.return_value
            cursor.description = [('row_count',)]
            cursor.fetchmany.return_value = returned
            with patch.object(p, 'connect_profile', return_value=(connection, {})):
                with self.assertRaises(BoundaryError) as raised:
                    p.execute_profile_template(T.SUMMARY, self.source, self.contract)
            self.assertEqual(raised.exception.code, reason)
            cursor.fetchmany.assert_called_once_with(101)
            connection.close.assert_called_once()

    def test_B05_missing_extra_nested_enum_and_nonfinite(self):
        for template in T:
            row = {key: 0 for key in FIELDS[template]}
            rows = [row]
            if template == T.COLUMNS:
                rows = [{'column_name': name, 'null_count': 0, 'cardinality': 0} for name in p.COLUMNS]
            if template == T.TIMESTAMP:
                row.update(minimum=None, maximum=None)
            p.validate_profile_result(template, rows)
            for key in FIELDS[template]:
                bad = json.loads(json.dumps(rows))
                del bad[0][key]
                with self.assertRaises(BoundaryError):
                    p.validate_profile_result(template, bad)
            bad = json.loads(json.dumps(rows))
            bad[0]['extra'] = 'unexpected'
            with self.assertRaises(BoundaryError):
                p.validate_profile_result(template, bad)
        bad = [{'column_name': 'secret-identifier', 'null_count': 0, 'cardinality': 0}] * 5
        with self.assertRaises(BoundaryError):
            p.validate_profile_result(T.COLUMNS, bad)
        for value in (float('inf'), float('-inf'), float('nan')):
            with self.assertRaises(BoundaryError):
                p.validate_profile_result(T.SUMMARY, [{'row_count': value}])

    def test_B05_sentinel_result_and_error_sanitization(self):
        evidence = p.execute_profile_template(T.BEHAVIOURS, self.source, self.contract)
        payload = json.dumps(asdict(evidence.result))
        for sentinel in ('controlled-user', 'controlled-goods', 'controlled-category', 'controlled-unknown'):
            self.assertNotIn(sentinel, payload)
        connection = MagicMock()
        connection.execute.side_effect = p.duckdb.Error('controlled-user controlled-unknown')
        with patch.object(p, 'connect_profile', return_value=(connection, {})):
            with self.assertRaises(BoundaryError) as raised:
                p.execute_profile_template(T.SUMMARY, self.source, self.contract)
        self.assertEqual(str(raised.exception), 'profile_template_failed')
        self.assertTrue(raised.exception.__suppress_context__)
        connection.close.assert_called_once()
