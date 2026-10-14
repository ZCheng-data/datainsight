"""Strict-reading fixtures only; no production source access."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from datainsight import profile as p
from datainsight.inspection import AccessPolicy, SourceRequest, validate_source, BoundaryError


class StrictCSVTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=p.ROOT / 'tests/fixtures')
        self.path = Path(self.temp.name) / 'synthetic.csv'
        self.contract = p.load_read_contract()
        self.policy = AccessPolicy((), p.ROOT / 'tests/fixtures', p.ROOT / 'outputs/W1-B')

    def tearDown(self):
        self.temp.cleanup()

    def source(self, data):
        self.path.write_bytes(data)
        return validate_source(SourceRequest('synthetic', self.path, 'file', 'synthetic-contract'), self.policy)

    def test_strict_nulls_literals_leading_zero_and_no_trim(self):
        source = self.source(b'001,002,003,pv,0001\n,"",NULL,NA, 12 \n')
        result = p.strict_csv_check(source, self.contract)
        self.assertEqual(result['row_count'], 2)
        self.assertEqual(result['nonnull'], {'user_id': 1, 'goods_id': 1, 'category_id': 2, 'behaviour': 2, 'timestamp': 2})
        self.assertEqual(result['read_schema'], [{'name': name, 'type': 'VARCHAR'} for name in p.COLUMNS])
        # Fixture-only internal reference inspection, never a product raw-row API.
        connection, _ = p.connect_profile()
        try:
            rows = connection.execute('SELECT * FROM ' + p.READ_RELATION, [str(source.path)]).fetchall()
            self.assertEqual(rows[0], ('001', '002', '003', 'pv', '0001'))
            self.assertEqual(rows[1], (None, None, 'NULL', 'NA', ' 12 '))
        finally:
            connection.close()

    def test_quoted_comma_newline_and_escaped_quote(self):
        source = self.source(b'"a,b","c\nd","e""f",pv,1\n')
        self.assertEqual(p.strict_csv_check(source, self.contract)['row_count'], 1)

    def test_column_count_encoding_and_quote_errors(self):
        for data in (b'a,b,c,pv\n', b'a,b,c,pv,1,extra\n', b'\xff,b,c,pv,1\n', b'"unterminated,b,c,pv,1\n'):
            source = self.source(data)
            with self.subTest(case_length=len(data)), self.assertRaises(BoundaryError) as raised:
                p.strict_csv_check(source, self.contract)
            self.assertEqual(raised.exception.code, 'strict_csv_parse_failed')

    def test_extra_contract_keys_and_parameters_before_connect(self):
        for change in ({'sql': 'untrusted'}, {'header': True}, {'auto_detect': True}, {'nullstr': 'NULL'}, {'ignore_errors': True}):
            data = dict(p.EXPECTED)
            data.update(change)
            with patch.object(p, 'connect_profile') as connect, self.assertRaises(BoundaryError):
                p.validate_read_contract(p.ReadContract(data))
            connect.assert_not_called()

    def test_contract_config_reparse_before_read(self):
        with patch.object(p, 'check_components', side_effect=BoundaryError('link_or_reparse_denied')), patch.object(Path, 'read_text') as read:
            with self.assertRaises(BoundaryError):
                p.load_read_contract()
            read.assert_not_called()

    def test_engine_settings_are_actual_and_extensions_disabled(self):
        connection, settings = p.connect_profile()
        try:
            self.assertEqual(settings['autoinstall_known_extensions'], 'false')
            self.assertEqual(settings['autoload_known_extensions'], 'false')
            self.assertEqual(settings['allow_unsigned_extensions'], 'false')
            self.assertEqual(Path(settings['temp_directory']), p.ROOT / '.cache/duckdb/tmp')
            self.assertEqual(Path(settings['extension_directory']), p.ROOT / '.cache/duckdb/extensions')
        finally:
            connection.close()
