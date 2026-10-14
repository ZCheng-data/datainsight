"""B03 closed aggregate templates versus independent fixture reference."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from datainsight import profile as p
from datainsight.profile_templates import ProfileTemplateId
from datainsight.inspection import AccessPolicy, SourceRequest, validate_source, BoundaryError
from w1b_reference import generate, reference


class ProfileReferenceTests(unittest.TestCase):
    def test_all_metrics_independent_reference(self):
        with tempfile.TemporaryDirectory(dir=p.ROOT / 'tests/fixtures') as directory:
            for case in ('mixed', 'all_null_time'):
                path = Path(directory) / (case + '.csv')
                generate(path, case)
                source = validate_source(SourceRequest('synthetic', path, 'file', 'synthetic-contract'),
                    AccessPolicy((), p.ROOT / 'tests/fixtures', p.ROOT / 'outputs/W1-B'))
                expected = reference(path)
                for template in ProfileTemplateId:
                    with self.subTest(case=case, template=template.value):
                        evidence = p.execute_profile_template(template, source, p.load_read_contract())
                        self.assertEqual(evidence.result.rows, expected[template.value])
                        self.assertEqual(evidence.parameters, [str(path)])
                        self.assertNotIn(str(path), evidence.sql)
                        text = str(evidence.result.rows)
                        for sentinel in ('sentinel-user', 'sentinel-goods', 'sentinel-category', 'unknown-sensitive-behaviour'):
                            self.assertNotIn(sentinel, text)

    def test_unknown_template_before_connection(self):
        with patch.object(p, 'connect_profile') as connection:
            with self.assertRaises(BoundaryError):
                p.execute_profile_template('arbitrary-sql', None, None)
            connection.assert_not_called()

    def test_result_boundaries_and_nested_types(self):
        invalid = [([{'row_count': 0}] * 101), [{'row_count': True}], [{'row_count': {'nested': 1}}], [{'extra': 0}], [{'row_count': 'x' * (64 * 1024)}]]
        for result in invalid:
            with self.assertRaises(BoundaryError):
                p.validate_profile_result(ProfileTemplateId.SUMMARY, result)
