"""Offline installed RECORD verification; never imports installed package code."""
import base64
import csv
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from datainsight.inspection import normalized, check_components, inside, BoundaryError

ROOT = Path('D:/MyPythonProjects/datainsight')
VENV = ROOT / '.venv'
RECORD = VENV / 'Lib/site-packages/duckdb-1.4.1.dist-info/RECORD'


@dataclass
class InstalledRecordCheck:
    status: str
    started_at: str
    ended_at: str
    record_sha256_before: str
    record_sha256_after: str
    record_unchanged: bool
    files: list
    summary: dict
    proof_scope: str
    wheel_sha256: None = None


def digest_file(path):
    size = 0
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            size += len(block)
            digest.update(block)
    return digest.digest(), size


def verify_installed_record(record_path: Path, allowed_root: Path) -> InstalledRecordCheck:
    start = datetime.now(timezone.utc).isoformat()
    root = normalized(allowed_root)
    record = normalized(record_path)
    if not inside(record, root) or record.name != 'RECORD' or not record.parent.name.endswith('.dist-info'):
        raise BoundaryError('record_outside_policy')
    check_components(root)
    check_components(record)
    before, _ = digest_file(record)
    site = record.parent.parent
    entries = []
    seen = set()
    try:
        with record.open('r', encoding='utf-8', newline='') as stream:
            rows = list(csv.reader(stream, strict=True))
    except (OSError, UnicodeError, csv.Error):
        raise BoundaryError('record_parse_failed')
    for row in rows:
        item = {'record_path': row[0] if row else None, 'status': 'invalid_format',
                'declared_hash': None, 'computed_sha256': None,
                'declared_size': None, 'computed_size': None}
        entries.append(item)
        if len(row) != 3:
            continue
        name, declared, size_text = row
        # RECORD paths use forward slashes; parent traversal can be legitimate
        # for Scripts but cannot escape the approved venv.
        if not name or '\\' in name or ':' in name or any(c in name for c in ('*', '?', '\x00', '\n', '\r')):
            continue
        relative = PurePosixPath(name)
        if relative.is_absolute():
            item['status'] = 'outside_policy'
            continue
        target = Path(os.path.abspath(site.joinpath(*relative.parts)))
        if not inside(target, root):
            item['status'] = 'outside_policy'
            continue
        key = os.path.normcase(str(target))
        if key in seen:
            item['status'] = 'duplicate_path'
            continue
        seen.add(key)
        try:
            check_components(normalized(target))
        except (BoundaryError, OSError):
            item['status'] = 'unsafe_path'
            continue
        if size_text and not re.fullmatch(r'[0-9]+', size_text):
            continue
        expected_size = int(size_text) if size_text else None
        item['declared_size'] = expected_size
        expected_digest = None
        if declared:
            item['declared_hash'] = declared
            if '=' not in declared:
                continue
            algorithm, encoded = declared.split('=', 1)
            if algorithm != 'sha256':
                item['status'] = 'unknown_algorithm'
                continue
            if not re.fullmatch(r'[A-Za-z0-9_-]{43}', encoded):
                continue
            try:
                expected_digest = base64.b64decode(encoded + '=', altchars=b'-_', validate=True)
            except ValueError:
                continue
            if len(expected_digest) != 32 or base64.urlsafe_b64encode(expected_digest).rstrip(b'=').decode() != encoded or expected_size is None:
                continue
        try:
            actual, actual_size = digest_file(target)
        except FileNotFoundError:
            item['status'] = 'missing'
            continue
        except OSError:
            item['status'] = 'read_failed'
            continue
        item['computed_sha256'] = actual.hex()
        item['computed_size'] = actual_size
        if expected_size is not None and actual_size != expected_size:
            item['status'] = 'size_mismatch'
        elif expected_digest is not None and actual != expected_digest:
            item['status'] = 'hash_mismatch'
        elif expected_digest is not None:
            item['status'] = 'verified'
        else:
            item['status'] = 'hash_not_provided'
            item['record_self_exception'] = target == record
    check_components(record)
    after, _ = digest_file(record)
    summary = {}
    for item in entries:
        summary[item['status']] = summary.get(item['status'], 0) + 1
    summary['total_entries'] = len(entries)
    unchanged = before == after
    success = bool(entries) and unchanged and all(x['status'] in ('verified', 'hash_not_provided') for x in entries)
    return InstalledRecordCheck('consistent_with_local_record' if success else 'failed', start,
        datetime.now(timezone.utc).isoformat(), before.hex(), after.hex(), unchanged,
        entries, summary, 'Only listed files versus local RECORD declarations; unhashed entries are not hash-verified. No wheel hash, official authenticity, supply-chain audit, or unlisted-file coverage.')


class RecordTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / 'tests/fixtures')
        self.root = Path(self.tmp.name)
        self.site = self.root / 'Lib/site-packages'
        self.record = self.site / 'synthetic.dist-info/RECORD'
        self.record.parent.mkdir(parents=True)
        self.file = self.site / 'synthetic.bin'
        self.file.write_bytes(b'controlled-synthetic-content')
        digest, size = digest_file(self.file)
        self.row = ['synthetic.bin', 'sha256=' + base64.urlsafe_b64encode(digest).rstrip(b'=').decode(), str(size)]
        self.write([self.row, ['synthetic.dist-info/RECORD', '', '']])

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rows):
        with self.record.open('w', encoding='utf-8', newline='') as stream:
            csv.writer(stream).writerows(rows)

    def test_normal(self):
        result = verify_installed_record(self.record, self.root)
        self.assertEqual(result.status, 'consistent_with_local_record')
        self.assertEqual(result.summary['verified'], 1)
        self.assertEqual(result.summary['hash_not_provided'], 1)
        self.assertTrue(result.record_unchanged)

    def test_tampered(self):
        self.file.write_bytes(b'x' * len(self.file.read_bytes()))
        self.assertEqual(verify_installed_record(self.record, self.root).files[0]['status'], 'hash_mismatch')

    def test_missing(self):
        self.file.unlink()
        self.assertEqual(verify_installed_record(self.record, self.root).files[0]['status'], 'missing')

    def test_duplicate(self):
        self.write([self.row, self.row])
        self.assertEqual(verify_installed_record(self.record, self.root).files[1]['status'], 'duplicate_path')

    def test_outside_before_open(self):
        self.write([['../../../outside.bin', '', '']])
        original = Path.open
        opened = []
        def tracked(path, *args, **kwargs):
            opened.append(path)
            return original(path, *args, **kwargs)
        with patch.object(Path, 'open', tracked):
            result = verify_installed_record(self.record, self.root)
        self.assertEqual(result.files[0]['status'], 'outside_policy')
        self.assertTrue(all(path == self.record for path in opened))

    def test_size_algorithm_and_format(self):
        for row, status in (([self.row[0], self.row[1], '999'], 'size_mismatch'),
                            ([self.row[0], 'md5=abc', self.row[2]], 'unknown_algorithm'),
                            ([self.row[0], 'sha256=bad', self.row[2]], 'invalid_format')):
            self.write([row])
            self.assertEqual(verify_installed_record(self.record, self.root).files[0]['status'], status)

    def test_record_changed(self):
        original = digest_file
        calls = 0
        def changed(path):
            nonlocal calls
            value = original(path)
            if path == self.record:
                calls += 1
                return hashlib.sha256(str(calls).encode('ascii')).digest(), value[1]
            return value
        with patch(__name__ + '.digest_file', changed):
            result = verify_installed_record(self.record, self.root)
        self.assertEqual(result.status, 'failed')
        self.assertFalse(result.record_unchanged)


if __name__ == '__main__':
    env = {key: os.environ.get(key) for key in ('TEMP', 'TMP', 'TMPDIR', 'PYTHONPATH', 'PYTHONDONTWRITEBYTECODE')}
    run = 'record-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output = ROOT / 'outputs/W1-B' / run
    check_components(output)
    output.mkdir()
    clock = time.perf_counter()
    log = io.StringIO()
    tests = unittest.TextTestRunner(stream=log, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RecordTests))
    (output / 'test.log').write_text(log.getvalue(), encoding='utf-8')
    status = 2
    if tests.wasSuccessful():
        try:
            result = verify_installed_record(RECORD, VENV)
            (output / 'installed-record-check.json').write_text(json.dumps(asdict(result), indent=2), encoding='utf-8')
            status = 0 if result.status == 'consistent_with_local_record' else 2
            print(json.dumps({'status': result.status, 'summary': result.summary, 'record_unchanged': result.record_unchanged}))
        except (BoundaryError, OSError) as error:
            (output / 'error.json').write_text(json.dumps({'reason_code': error.code if isinstance(error, BoundaryError) else 'record_operation_failed'}), encoding='utf-8')
    (output / 'command-environment.json').write_text(json.dumps({'argv': [sys.executable, '-B', str(Path(__file__))], 'exit_status': status,
        'test_count': tests.testsRun, 'test_success': tests.wasSuccessful(), 'version': sys.version,
        'executable': sys.executable, 'temp_directory': tempfile.gettempdir(), 'variables': env,
        'elapsed_seconds': time.perf_counter() - clock, 'network_used': False, 'duckdb_imported': False}, indent=2), encoding='utf-8')
    manifest = []
    for path in [*sorted(output.iterdir()), Path(__file__)]:
        data = path.read_bytes()
        manifest.append({'path': str(path), 'byte_size': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    (output / 'manifest.json').write_text(json.dumps({'self_excluded': True, 'files': manifest}, indent=2), encoding='utf-8')
    print(log.getvalue())
    print('EVIDENCE_DIRECTORY=' + str(output))
    sys.exit(status)
