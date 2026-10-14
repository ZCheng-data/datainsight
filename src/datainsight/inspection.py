"""Conservative local path boundary; no record parsing or model integration."""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import math
import os
import stat
import time


class BoundaryError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class SourceRequest:
    source_id: str
    path: Path
    mode: str
    read_contract_ref: str


@dataclass(frozen=True)
class AccessPolicy:
    production_files: tuple[Path, ...]
    fixture_root: Path
    output_root: Path


@dataclass(frozen=True)
class ValidatedSource:
    request: SourceRequest
    path: Path
    policy: AccessPolicy


@dataclass
class FileInspection:
    format: str
    file_type: str
    byte_size: int | None
    modified_at: str | None
    file_access: str
    status: str
    reason_code: str
    errors: list


@dataclass
class FingerprintEvidence:
    algorithm: str
    sha256: str
    started_at: str
    ended_at: str
    elapsed_seconds: float
    bytes_read: int
    evidence_ref: str


@dataclass
class DirectoryInspection:
    status: str
    reason_code: str
    candidate_count: int
    unsupported_count: int


@dataclass
class InspectionReport:
    schema_version: str
    run_id: str
    stage: str
    source_id: str
    local_path_mapping_ref: str
    inspection: FileInspection
    fingerprint: FingerprintEvidence | None
    read_contract_ref: str
    parse_validation: str
    unverified: list[str]
    errors: list
    product_model_usage: str


@dataclass
class ArtifactReference:
    path: str
    sha256: str
    byte_size: int


def now():
    return datetime.now(timezone.utc).isoformat()


def normalized(value):
    text = str(value)
    if any(c in text for c in ('*', '?', '\x00', '\n', '\r')) or '://' in text:
        raise BoundaryError('invalid_path_form')
    p = Path(value)
    if not p.is_absolute() or '..' in p.parts or text.startswith(('\\\\', '//')):
        raise BoundaryError('invalid_path_form')
    if os.name == 'nt' and (len(p.drive) != 2 or ':' in text[2:]):
        raise BoundaryError('invalid_path_form')
    return p


def inside(p, root):
    return p == root or root in p.parents


def check_components(p):
    for part in [*reversed(p.parents), p]:
        try:
            s = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(s.st_mode) or getattr(s, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise BoundaryError('link_or_reparse_denied')
    resolved = p.resolve(strict=False)
    if resolved != p:
        raise BoundaryError('noncanonical_target_denied')
    return resolved


def validate_source(request: SourceRequest, policy: AccessPolicy) -> ValidatedSource:
    p = normalized(request.path)
    root = normalized(policy.fixture_root)
    if request.mode == 'file':
        allowed = p in tuple(normalized(x) for x in policy.production_files) or inside(p, root)
    elif request.mode == 'fixture_directory':
        allowed = inside(p, root)
    else:
        raise BoundaryError('invalid_mode')
    if not allowed:
        raise BoundaryError('source_outside_policy')
    check_components(root)
    check_components(p)
    return ValidatedSource(request, p, policy)


def revalidate(source):
    return validate_source(source.request, source.policy)


def inspect_file(source: ValidatedSource) -> FileInspection:
    revalidate(source)
    p = source.path
    fmt = p.suffix.lower().lstrip('.') or 'unknown'
    try:
        s = p.stat()
    except FileNotFoundError:
        return FileInspection(fmt, 'missing', None, None, 'not_opened', 'missing', 'file_missing', [])
    except OSError:
        return FileInspection(fmt, 'unknown', None, None, 'failed', 'unreadable', 'metadata_failed', [{'code': 'metadata_failed'}])
    modified = datetime.fromtimestamp(s.st_mtime, timezone.utc).isoformat()
    if not stat.S_ISREG(s.st_mode):
        return FileInspection(fmt, 'other', s.st_size, modified, 'not_opened', 'unsupported', 'not_regular_file', [])
    if fmt not in ('csv', 'parquet'):
        return FileInspection(fmt, 'regular_file', s.st_size, modified, 'not_opened', 'unsupported', 'unsupported_extension', [])
    if s.st_size == 0:
        return FileInspection(fmt, 'regular_file', 0, modified, 'not_opened', 'unreadable', 'empty_file', [])
    try:
        with p.open('rb') as stream:
            stream.read(1)
    except PermissionError:
        return FileInspection(fmt, 'regular_file', s.st_size, modified, 'failed', 'unreadable', 'permission_denied', [{'code': 'permission_denied'}])
    except OSError:
        return FileInspection(fmt, 'regular_file', s.st_size, modified, 'failed', 'unreadable', 'read_failed', [{'code': 'read_failed'}])
    return FileInspection(fmt, 'regular_file', s.st_size, modified, 'read_only_open_succeeded', 'needs_configuration', 'parse_and_contract_unverified', [])


def fingerprint_file(source: ValidatedSource) -> FingerprintEvidence:
    revalidate(source)
    if not stat.S_ISREG(source.path.stat().st_mode):
        raise BoundaryError('not_regular_file')
    started = now()
    clock = time.perf_counter()
    digest = hashlib.sha256()
    size = 0
    with source.path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            size += len(block)
            digest.update(block)
    return FingerprintEvidence('SHA-256', digest.hexdigest(), started, now(), time.perf_counter() - clock, size, 'fingerprints.json')


def inspect_fixture_directory(request: SourceRequest, policy: AccessPolicy) -> DirectoryInspection:
    source = validate_source(request, policy)
    if request.mode != 'fixture_directory':
        raise BoundaryError('invalid_mode')
    candidates = unsupported = 0
    try:
        with os.scandir(source.path) as entries:
            for entry in entries:
                p = source.path / entry.name
                check_components(p)
                if entry.is_file(follow_symlinks=False):
                    if p.suffix.lower() in ('.csv', '.parquet'):
                        candidates += 1
                    elif p.suffix.lower() not in ('.py', '.md', '.txt'):
                        unsupported += 1
    except FileNotFoundError:
        return DirectoryInspection('missing', 'fixture_directory_missing', 0, 0)
    if candidates:
        return DirectoryInspection('needs_configuration', 'candidates_unverified', candidates, unsupported)
    if unsupported:
        return DirectoryInspection('unsupported', 'unsupported_candidates', 0, unsupported)
    return DirectoryInspection('missing', 'no_data_candidates', 0, 0)


def validate_report(data):
    # Contract-specific checks, not a general schema engine.
    def reject():
        raise BoundaryError('invalid_report_structure')

    def fields(value, names):
        if type(value) is not dict or set(value) != set(names.split()):
            reject()

    def text(value):
        if type(value) is not str or not value.strip() or any(c in value for c in ('\x00', '\n', '\r')):
            reject()

    def integer(value):
        if type(value) is not int or value < 0:
            reject()

    def timestamp(value):
        text(value)
        try:
            parsed = datetime.fromisoformat(value)
            if parsed.utcoffset() is None:
                reject()
            return parsed
        except (ValueError, OverflowError):
            reject()

    def errors(value):
        if type(value) is not list:
            reject()
        for error in value:
            fields(error, 'code')
            if type(error['code']) is not str or error['code'] not in ('metadata_failed', 'permission_denied', 'read_failed'):
                reject()

    fields(data, 'schema_version run_id stage source_id local_path_mapping_ref inspection fingerprint read_contract_ref parse_validation unverified errors product_model_usage')
    for key in ('schema_version', 'run_id', 'stage', 'source_id', 'local_path_mapping_ref', 'read_contract_ref', 'parse_validation', 'product_model_usage'):
        text(data[key])
    if data['schema_version'] != '1.0' or data['stage'] != 'S0' or data['parse_validation'] != 'not_run' or data['product_model_usage'] != 'not_applicable':
        reject()
    unknowns = {'content_parse', 'schema', 'delimiter', 'encoding', 'null_markers', 'column_types', 'time_unit', 'timezone', 'business_semantics'}
    if type(data['unverified']) is not list:
        reject()
    for item in data['unverified']:
        if type(item) is not str or item not in unknowns:
            reject()
    if len(data['unverified']) != len(set(data['unverified'])):
        reject()
    errors(data['errors'])
    i = data['inspection']
    fields(i, 'format file_type byte_size modified_at file_access status reason_code errors')
    for key in ('format', 'file_type', 'file_access', 'status', 'reason_code'):
        text(i[key])
    # Format is an extension token, including unsupported extensions.
    if not i['format'].isascii() or not i['format'].isalnum():
        reject()
    cases = {
        'file_missing': ('missing', 'missing', 'not_opened'),
        'metadata_failed': ('unreadable', 'unknown', 'failed'),
        'not_regular_file': ('unsupported', 'other', 'not_opened'),
        'unsupported_extension': ('unsupported', 'regular_file', 'not_opened'),
        'empty_file': ('unreadable', 'regular_file', 'not_opened'),
        'permission_denied': ('unreadable', 'regular_file', 'failed'),
        'read_failed': ('unreadable', 'regular_file', 'failed'),
        'parse_and_contract_unverified': ('needs_configuration', 'regular_file', 'read_only_open_succeeded'),
    }
    if cases.get(i['reason_code']) != (i['status'], i['file_type'], i['file_access']):
        reject()
    errors(i['errors'])
    expected_errors = [{'code': i['reason_code']}] if i['reason_code'] in ('metadata_failed', 'permission_denied', 'read_failed') else []
    if i['errors'] != expected_errors or data['errors'] != i['errors']:
        reject()
    if i['reason_code'] in ('file_missing', 'metadata_failed'):
        if i['byte_size'] is not None or i['modified_at'] is not None:
            reject()
    else:
        integer(i['byte_size'])
        timestamp(i['modified_at'])
    if i['reason_code'] in ('empty_file', 'permission_denied', 'read_failed', 'parse_and_contract_unverified') and i['format'] not in ('csv', 'parquet'):
        reject()
    if i['reason_code'] == 'unsupported_extension' and i['format'] in ('csv', 'parquet'):
        reject()
    if i['reason_code'] == 'empty_file' and i['byte_size'] != 0:
        reject()
    if i['reason_code'] in ('permission_denied', 'read_failed', 'parse_and_contract_unverified') and i['byte_size'] == 0:
        reject()
    f = data['fingerprint']
    if f is None:
        if i['status'] == 'needs_configuration':
            reject()
        return
    fields(f, 'algorithm sha256 started_at ended_at elapsed_seconds bytes_read evidence_ref')
    for key in ('algorithm', 'sha256', 'evidence_ref'):
        text(f[key])
    if f['algorithm'] != 'SHA-256' or len(f['sha256']) != 64 or any(c not in '0123456789abcdef' for c in f['sha256']):
        reject()
    started = timestamp(f['started_at'])
    ended = timestamp(f['ended_at'])
    if ended < started:
        reject()
    if type(f['elapsed_seconds']) not in (int, float) or not math.isfinite(f['elapsed_seconds']) or f['elapsed_seconds'] < 0:
        reject()
    integer(f['bytes_read'])
    if f['bytes_read'] != i['byte_size'] or i['status'] != 'needs_configuration':
        reject()
    ref = f['evidence_ref']
    if not ref.endswith('.json') or '/' in ref or '\\' in ref or ':' in ref or '..' in ref:
        reject()


def output_target(path, policy):
    p = normalized(path)
    root = normalized(policy.output_root)
    if not inside(p, root) or p == root:
        raise BoundaryError('output_outside_policy')
    check_components(root)
    check_components(p)
    if not p.parent.is_dir():
        raise BoundaryError('output_parent_missing')
    if p.exists():
        raise BoundaryError('output_exists')
    return p


def write_inspection(result: InspectionReport, output_path: Path, policy: AccessPolicy) -> ArtifactReference:
    data = asdict(result)
    validate_report(data)
    p = output_target(output_path, policy)
    payload = (json.dumps(data, ensure_ascii=True, indent=2) + '\n').encode('utf-8')
    with p.open('xb') as stream:
        stream.write(payload)
    return ArtifactReference(str(p), hashlib.sha256(payload).hexdigest(), len(payload))
