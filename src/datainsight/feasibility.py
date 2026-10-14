"""Offline W2-A adapter and independent CLI; input files never grant access."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
from . import feasibility_rules as rules_module

ROOT = Path(__file__).absolute().parents[2]
LEGACY = ROOT / 'outputs/W1-B/final-20261009T061339601505Z/production/profile.json'
ACCEPTANCE = ROOT / 'docs/acceptance/results/W1-final-acceptance-and-handoff.md'
CONTRACT = ROOT / 'configs/w1b-read-contract-v1.json'
BASELINE = '7095a57fbd6eb1292bec5ccde4713ac256678b8551eb478d3b5aaad89612cfb4'
OUTPUT = ROOT / 'outputs/W2-A'
FIXTURE = ROOT / 'tests/fixtures/w2a'
LIMIT = 128 * 1024
COLUMNS = ('user_id', 'goods_id', 'category_id', 'behaviour', 'timestamp')
FIELDS = {'summary': ('row_count',), 'columns': ('column_name', 'null_count', 'cardinality'),
          'behaviours': ('pv', 'fav', 'cart', 'buy', 'missing', 'other'),
          'duplicates': ('duplicate_groups', 'excess_rows'),
          'timestamp': ('null_count', 'valid_integer', 'format_failed', 'range_failed', 'minimum', 'maximum')}
UNITS = {'behaviour_record_counts': 'raw_record', 'gmv': 'currency_amount',
         'strict_funnel': 'ordered_user_conversion'}
EVIDENCE_KEYS = set(('schema_version evidence_id run_id dataset_version source_id source_path '
    'read_config_ref read_config_version read_config_sha256 template_id template_version '
    'template_sha256 sql parameters python_version duckdb_version status started_at ended_at '
    'result_ref result_sha256 metric_definition_version engine_configuration').split())
PROFILE_KEYS = set(('schema_version run_id stage status dataset_version reading_schema metrics '
                    'product_model_usage limitations').split())
DIAGNOSIS_KEYS = set(('schema_version run_id stage status question_ref question_hash question_version '
    'dataset_version input_manifest_ref input_manifest_hash ruleset_id ruleset_version ruleset_hash '
    'request_state capability prerequisite_checks quality_observations eligible_method_ids gaps '
    'human_decision_state limitations').split())
RECEIPT_KEYS = set(('schema_version run_id diagnosis_run_id diagnosis_ref diagnosis_hash dataset_version '
    'input_manifest_sha256 question_version question_hash ruleset_id ruleset_version ruleset_hash '
    'decision actor confirmed_at acceptance_scope').split())
REQUIRED = ('input-manifest.json', 'reference-check.json', 'environment.json',
            'network-observation.json', 'cli-command.json')


class BoundaryError(ValueError):
    pass


def fail(reason):
    raise BoundaryError(reason)


def now():
    return datetime.now(timezone.utc).isoformat()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True,
                       allow_nan=False) + '\n').encode('utf-8')


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def exact(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        fail('invalid_object_keys')


def text(value):
    if type(value) is not str or not value or len(value) > 4096:
        fail('invalid_text')


def identifier(value):
    if type(value) is not str or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}', value):
        fail('invalid_identifier')


def hash_value(value):
    if type(value) is not str or not re.fullmatch('[0-9a-f]{64}', value):
        fail('invalid_hash')


def timestamp(value):
    text(value)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        fail('invalid_timestamp')
    if parsed.tzinfo is None:
        fail('timestamp_timezone_required')


def path_check(value, root):
    raw = str(value)
    p = Path(value)
    if (not p.is_absolute() or '..' in p.parts or raw.startswith(('\\\\', '//'))
            or any(c in raw for c in ('*', '?', '\x00', '\n', '\r')) or '://' in raw
            or (os.name == 'nt' and (len(p.drive) != 2 or ':' in raw[2:]))):
        fail('invalid_path')
    if p != root and root not in p.parents:
        fail('path_outside_policy')
    for part in (*reversed(p.parents), p):
        try:
            s = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(s.st_mode) or getattr(s, 'st_file_attributes', 0) & 0x400:
            fail('reparse_denied')
    if p.resolve(strict=False) != p:
        fail('noncanonical_path')
    return p


def relative(p):
    return p.relative_to(ROOT).as_posix()


def read_bytes(p, root=ROOT):
    p = path_check(p, root)
    if not p.is_file() or p.stat().st_size > LIMIT:
        fail('file_missing_or_size_boundary')
    with p.open('rb') as stream:
        payload = stream.read(LIMIT + 1)
    if len(payload) > LIMIT:
        fail('file_size_boundary')
    return payload


def parse(payload):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                fail('duplicate_json_key')
            result[key] = value
        return result
    def finite(value):
        number = float(value)
        if not math.isfinite(number):
            fail('nonfinite_json')
        return number
    try:
        return json.loads(payload.decode('utf-8'), object_pairs_hook=pairs,
                          parse_float=finite, parse_constant=lambda _: fail('nonfinite_json'))
    except (UnicodeError, json.JSONDecodeError, RecursionError):
        fail('invalid_json')


def result_check(metric, rows):
    expected = len(COLUMNS) if metric == 'columns' else 1
    if type(rows) is not list or len(rows) != expected:
        fail('result_structure')
    for i, row in enumerate(rows):
        exact(row, FIELDS[metric])
        for key, value in row.items():
            if key == 'column_name':
                if value != COLUMNS[i]:
                    fail('column_order')
            elif key in ('minimum', 'maximum'):
                if value is not None and (type(value) is not int or not -(2**63) <= value < 2**63):
                    fail('result_type')
            elif type(value) is not int or value < 0:
                fail('result_type')
        if metric == 'timestamp':
            if row['valid_integer'] == 0:
                if row['minimum'] is not None or row['maximum'] is not None:
                    fail('timestamp_result')
            elif (row['minimum'] is None or row['maximum'] is None
                  or row['minimum'] > row['maximum']):
                fail('timestamp_result')


def final_check(directory, command=None):
    terminal = parse(read_bytes(directory / 'final-status.json'))
    keys = ('run_id', 'command', 'status', 'exit_status', 'completed_at', 'required_evidence_refs')
    exact(terminal, keys if command == 'profile' else ('schema_version', *keys))
    if (terminal.get('schema_version', '1.0') != '1.0' or terminal['run_id'] != directory.name
            or terminal['status'] != 'success' or type(terminal['exit_status']) is not int
            or terminal['exit_status'] != 0 or (command and terminal['command'] != command)):
        fail('invalid_success_terminal')
    timestamp(terminal['completed_at'])
    required = REQUIRED[1:] if command == 'profile' else REQUIRED
    if terminal['required_evidence_refs'] != list(required):
        fail('terminal_references')
    for name in required:
        parse(read_bytes(directory / name))
    return terminal


def load_accepted_profile(profile_ref, acceptance_ref):
    profile_path = path_check(profile_ref, ROOT)
    acceptance_path = path_check(acceptance_ref, ROOT)
    legacy = profile_path == LEGACY and acceptance_path == ACCEPTANCE
    if not legacy:
        if profile_path.name != 'profile.json':
            fail('profile_filename')
        path_check(profile_path, FIXTURE)
        if acceptance_path != profile_path.parent / 'fixture-acceptance.json':
            fail('unsupported_profile_source')
    manifest = []
    def load(path, json_file=True):
        payload = read_bytes(path)
        manifest.append({'path': relative(path), 'sha256': digest(payload)})
        return parse(payload) if json_file else payload
    acceptance = load(acceptance_path, not legacy)
    profile = load(profile_path)
    exact(profile, PROFILE_KEYS)
    if (profile['schema_version'] != '1.0' or profile['stage'] != 'S1'
            or profile['run_id'] != profile_path.parent.name
            or profile['product_model_usage'] != 'not_applicable'):
        fail('profile_identity')
    hash_value(profile['dataset_version'])
    if profile['reading_schema'] != [{'name': name, 'type': 'VARCHAR'} for name in COLUMNS]:
        fail('reading_schema')
    if type(profile['limitations']) is not list or not all(type(v) is str for v in profile['limitations']):
        fail('profile_limitations')
    exact(profile['metrics'], FIELDS)
    if legacy:
        if (profile['status'] != 'success' or profile['dataset_version'] != BASELINE
                or BASELINE.encode('ascii') not in acceptance):
            fail('legacy_acceptance_mismatch')
        # This exact local document is the authority; not an independent hash anchor.
        load(profile_path.parent.parent / 'production-commands.json')
        basis = 'accepted_legacy_production'
    else:
        exact(acceptance, ('schema_version', 'kind', 'dataset_version'))
        if acceptance != {'schema_version': '1.0', 'kind': 'controlled_fixture',
                          'dataset_version': profile['dataset_version']}:
            fail('fixture_acceptance')
        if profile['status'] != 'computed_pending_finalization':
            fail('new_profile_not_pending_computation')
        final_check(profile_path.parent, 'profile')
        for name in ('final-status.json', *REQUIRED[1:]):
            load(profile_path.parent / name)
        basis = 'current_protocol_success'
    contract_payload = read_bytes(CONTRACT)
    manifest.append({'path': relative(CONTRACT), 'sha256': digest(contract_payload)})
    contract = parse(contract_payload)
    expected_contract = {'version': '1.0', 'source_id': 'textbook_userbehavior', 'header': False,
        'columns': {name: 'VARCHAR' for name in COLUMNS}, 'delimiter': ',', 'encoding': 'utf-8',
        'quote': '"', 'escape': '"', 'nullstr': '', 'allow_quoted_nulls': True,
        'auto_detect': False, 'ignore_errors': False, 'strict_mode': True, 'null_padding': False,
        'trim': False, 'bad_rows': 'error_and_stop', 'time_unit': 'unknown', 'timezone': 'unknown'}
    if encoded(contract) != encoded(expected_contract):
        fail('read_contract_mismatch')
    refs = {}
    for metric in FIELDS:
        evidence = load(profile_path.parent / (metric + '-evidence.json'))
        exact(evidence, EVIDENCE_KEYS)
        item = profile['metrics'][metric]
        exact(item, ('evidence_id', 'result_ref', 'values'))
        for key in ('sql', 'source_id', 'source_path', 'python_version', 'duckdb_version'):
            text(evidence[key])
        if type(evidence['parameters']) is not list or not all(type(v) is str for v in evidence['parameters']):
            fail('evidence_parameters')
        exact(evidence['engine_configuration'], ('allow_unsigned_extensions', 'autoinstall_known_extensions',
              'autoload_known_extensions', 'enable_external_access', 'extension_directory', 'temp_directory'))
        if not all(type(v) is str for v in evidence['engine_configuration'].values()):
            fail('engine_configuration_type')
        for key in ('started_at', 'ended_at'):
            timestamp(evidence[key])
        for key in ('template_sha256', 'read_config_sha256', 'result_sha256'):
            hash_value(evidence[key])
        if (evidence['schema_version'] != '1.0' or evidence['status'] != 'success'
                or evidence['run_id'] != profile['run_id']
                or evidence['dataset_version'] != profile['dataset_version']
                or evidence['evidence_id'] != profile['run_id'] + ':' + metric
                or evidence['template_id'] != metric or evidence['template_version'] != '1.0'
                or evidence['metric_definition_version'] != '1.0'
                or evidence['read_config_version'] != '1.0'
                or evidence['read_config_ref'] != relative(CONTRACT)
                or evidence['read_config_sha256'] != digest(contract_payload)
                or evidence['result_ref'] != metric + '-result.json'
                or item['result_ref'] != evidence['result_ref']
                or item['evidence_id'] != evidence['evidence_id']):
            fail('evidence_reference_mismatch')
        result_path = profile_path.parent / (metric + '-result.json')
        payload = read_bytes(result_path)
        manifest.append({'path': relative(result_path), 'sha256': digest(payload)})
        rows = parse(payload)
        result_check(metric, rows)
        if digest(payload) != evidence['result_sha256'] or encoded(rows) != encoded(item['values']):
            fail('result_hash_or_values_mismatch')
        refs[metric] = {'evidence_ref': relative(profile_path.parent / (metric + '-evidence.json')),
                        'result_ref': relative(result_path), 'result_sha256': digest(payload), 'values': rows}
    fingerprints = load(profile_path.parent / 'fingerprints.json')
    exact(fingerprints, ('before', 'after', 'consistent'))
    if fingerprints['consistent'] is not True:
        fail('inconsistent_fingerprints')
    for phase in ('before', 'after'):
        fp = fingerprints[phase]
        exact(fp, ('algorithm', 'bytes_read', 'elapsed_seconds', 'ended_at', 'evidence_ref', 'sha256', 'started_at'))
        if (fp['algorithm'] != 'SHA-256' or fp['evidence_ref'] != 'fingerprints.json'
                or fp['sha256'] != profile['dataset_version'] or type(fp['bytes_read']) is not int
                or fp['bytes_read'] < 0 or type(fp['elapsed_seconds']) not in (int, float)
                or not math.isfinite(fp['elapsed_seconds']) or fp['elapsed_seconds'] < 0):
            fail('fingerprint_mismatch')
        timestamp(fp['started_at'])
        timestamp(fp['ended_at'])
    if fingerprints['before']['bytes_read'] != fingerprints['after']['bytes_read']:
        fail('fingerprint_size_mismatch')
    return {'schema_version': '1.0', 'dataset_version': profile['dataset_version'],
            'profile_identity': {'profile_ref': relative(profile_path), 'run_id': profile['run_id'],
                                 'acceptance_ref': relative(acceptance_path)},
            'read_contract_sha256': digest(contract_payload), 'reading_schema': profile['reading_schema'],
            'metric_refs': refs, 'input_manifest': {'schema_version': '1.0', 'files': manifest},
            'acceptance_basis': basis, 'source_kind': 'historical_production' if legacy else 'controlled_fixture',
            'limitations': profile['limitations']}


def question_check(question):
    if question is None:
        return
    exact(question, ('schema_version', 'question_id', 'question_version', 'intent', 'requested_unit'))
    if question['schema_version'] != '1.0':
        fail('unknown_question_version')
    for key in ('question_id', 'question_version', 'intent', 'requested_unit'):
        identifier(question[key])
    if question['intent'] in UNITS and question['requested_unit'] != UNITS[question['intent']]:
        fail('invalid_requested_unit')


def diagnose(question, profile, rules):
    question_check(question)
    result = rules_module.evaluate(question, profile, rules)
    return {'schema_version': '1.0', 'run_id': 'unpublished', 'stage': 'S2',
            'status': 'computed_pending_finalization', 'question_ref': None, 'question_hash': None,
            'question_version': question['question_version'] if question else None,
            'dataset_version': profile['dataset_version'], 'input_manifest_ref': 'input-manifest.json',
            'input_manifest_hash': digest(encoded(profile['input_manifest'])),
            **{k: rules[k] for k in ('ruleset_id', 'ruleset_version', 'ruleset_hash')}, **result}


def manifest_check(manifest):
    exact(manifest, ('schema_version', 'files'))
    if manifest['schema_version'] != '1.0' or type(manifest['files']) is not list:
        fail('manifest_schema')
    seen = set()
    for item in manifest['files']:
        exact(item, ('path', 'sha256'))
        text(item['path'])
        hash_value(item['sha256'])
        if item['path'] in seen:
            fail('duplicate_manifest_path')
        seen.add(item['path'])
        candidate = ROOT / item['path']
        # Saved manifests cannot authorize paths: only fixed inputs/fixture/our question.
        allowed = {ACCEPTANCE, CONTRACT, LEGACY.parent.parent / 'production-commands.json',
                   ROOT / 'configs/w2a-question-v1.json'}
        allowed.update(LEGACY.parent / name for name in ('profile.json', 'fingerprints.json'))
        allowed.update(LEGACY.parent / (m + suffix) for m in FIELDS
                       for suffix in ('-evidence.json', '-result.json'))
        if candidate not in allowed:
            path_check(candidate, FIXTURE)
            if candidate.suffix != '.json':
                fail('manifest_path_not_allowed')
        if digest(read_bytes(candidate)) != item['sha256']:
            fail('input_changed')


def load_diagnosis(path):
    path = path_check(path, OUTPUT)
    if path.name != 'diagnosis.json':
        fail('diagnosis_filename')
    final_check(path.parent, 'diagnose')
    payload = read_bytes(path)
    diagnosis = parse(payload)
    exact(diagnosis, DIAGNOSIS_KEYS)
    if (diagnosis['schema_version'] != '1.0' or diagnosis['stage'] != 'S2'
            or diagnosis['run_id'] != path.parent.name
            or diagnosis['status'] != 'computed_pending_finalization'
            or diagnosis['input_manifest_ref'] != 'input-manifest.json'):
        fail('diagnosis_identity')
    manifest_payload = read_bytes(path.parent / 'input-manifest.json')
    if digest(manifest_payload) != diagnosis['input_manifest_hash']:
        fail('manifest_binding')
    manifest = parse(manifest_payload)
    audit = parse(read_bytes(path.parent / 'reference-check.json'))
    exact(audit, ('schema_version', 'references_resolvable', 'profile_identity', 'acceptance_basis', 'source_kind'))
    identity = audit['profile_identity']
    exact(identity, ('profile_ref', 'run_id', 'acceptance_ref'))
    snapshot = load_accepted_profile(ROOT / identity['profile_ref'], ROOT / identity['acceptance_ref'])
    if (snapshot['profile_identity'] != identity or snapshot['acceptance_basis'] != audit['acceptance_basis']
            or audit['references_resolvable'] is not True or audit['schema_version'] != '1.0'
            or snapshot['source_kind'] != audit['source_kind']):
        fail('profile_binding')
    question = None
    expected_manifest = snapshot['input_manifest']
    if diagnosis['question_ref'] is not None:
        qpath = ROOT / diagnosis['question_ref']
        if qpath != ROOT / 'configs/w2a-question-v1.json':
            path_check(qpath, FIXTURE)
        qpayload = read_bytes(qpath)
        if digest(qpayload) != diagnosis['question_hash']:
            fail('question_changed')
        question = parse(qpayload)
        expected_manifest['files'].append({'path': relative(qpath), 'sha256': digest(qpayload)})
    if encoded(expected_manifest) != manifest_payload:
        fail('manifest_file_set')
    manifest_check(manifest)
    recomputed = diagnose(question, snapshot, rules_module.registered_rules())
    recomputed.update(run_id=diagnosis['run_id'], question_ref=diagnosis['question_ref'],
                      question_hash=diagnosis['question_hash'])
    if encoded(recomputed) != encoded(diagnosis):
        fail('diagnosis_or_rules_changed')
    return diagnosis, payload, manifest


def decision_check(decision, diagnosis):
    exact(decision, ('decision', 'actor', 'confirmed_at'))
    if decision['decision'] not in ('accept', 'request_data', 'reject', 'cancel'):
        fail('invalid_decision')
    identifier(decision['actor'])
    timestamp(decision['confirmed_at'])
    if decision['decision'] == 'accept' and (diagnosis['request_state'] != 'valid'
                                           or diagnosis['capability'] != 'supported'):
        fail('accept_prerequisites_unmet')


def record_s2_decision(diagnosis, decision, output_dir):
    identifier(diagnosis['run_id'])
    source = OUTPUT / diagnosis['run_id'] / 'diagnosis.json'
    checked, payload, manifest = load_diagnosis(source)
    if encoded(checked) != encoded(diagnosis):
        fail('diagnosis_binding')
    decision_check(decision, checked)
    directory = new_run(output_dir)
    receipt = {'schema_version': '1.0', 'run_id': directory.name,
        'diagnosis_run_id': checked['run_id'], 'diagnosis_ref': relative(source),
        'diagnosis_hash': digest(payload), 'dataset_version': checked['dataset_version'],
        'input_manifest_sha256': checked['input_manifest_hash'],
        'question_version': checked['question_version'], 'question_hash': checked['question_hash'],
        **{k: checked[k] for k in ('ruleset_id', 'ruleset_version', 'ruleset_hash')},
        **decision, 'acceptance_scope': 'S2_only'}
    save(directory / 'decision.json', receipt)
    save(directory / 'input-manifest.json', manifest)
    save(directory / 'reference-check.json', {'schema_version': '1.0', 'references_resolvable': True,
         'diagnosis_ref': relative(source), 'diagnosis_hash': digest(payload)})
    return receipt


def verify_decision(path):
    path = path_check(path, OUTPUT)
    if path.name != 'decision.json':
        fail('decision_filename')
    final_check(path.parent, 'decide')
    receipt = parse(read_bytes(path))
    exact(receipt, RECEIPT_KEYS)
    diagnosis, payload, manifest = load_diagnosis(ROOT / receipt['diagnosis_ref'])
    expected = {'schema_version': '1.0', 'run_id': path.parent.name,
        'diagnosis_run_id': diagnosis['run_id'], 'diagnosis_ref': receipt['diagnosis_ref'],
        'diagnosis_hash': digest(payload), 'dataset_version': diagnosis['dataset_version'],
        'input_manifest_sha256': diagnosis['input_manifest_hash'],
        'question_version': diagnosis['question_version'], 'question_hash': diagnosis['question_hash'],
        **{k: diagnosis[k] for k in ('ruleset_id', 'ruleset_version', 'ruleset_hash')},
        **{k: receipt[k] for k in ('decision', 'actor', 'confirmed_at')}, 'acceptance_scope': 'S2_only'}
    decision_check({k: receipt[k] for k in ('decision', 'actor', 'confirmed_at')}, diagnosis)
    if encoded(receipt) != encoded(expected) or read_bytes(path.parent / 'input-manifest.json') != encoded(manifest):
        fail('decision_binding')
    audit = parse(read_bytes(path.parent / 'reference-check.json'))
    if encoded(audit) != encoded({'schema_version': '1.0', 'references_resolvable': True,
            'diagnosis_ref': receipt['diagnosis_ref'], 'diagnosis_hash': digest(payload)}):
        fail('decision_reference_binding')
    return receipt


def new_run(value):
    directory = path_check(value, OUTPUT)
    if directory.parent != OUTPUT:
        fail('run_must_be_direct_child')
    identifier(directory.name)
    if directory.exists():
        fail('output_exists')
    directory.mkdir(parents=True)
    return directory


def save(path, data):
    path_check(path, OUTPUT)
    payload = encoded(data)
    if len(payload) > LIMIT:
        fail('output_size_boundary')
    with path.open('xb') as stream:
        stream.write(payload)
    return digest(payload)


def publish(directory, data):
    target = directory / 'final-status.json'
    staging = directory / ('final-status-' + data['status'] + '.tmp')
    path_check(target, OUTPUT)
    if target.exists():
        fail('terminal_exists')
    save(staging, data)
    with staging.open('r+b') as stream:
        stream.flush()
        os.fsync(stream.fileno())
    if target.exists():
        fail('terminal_exists')
    staging.rename(target)


def environment():
    temp = Path(tempfile.gettempdir())
    if temp != ROOT / '.cache/tmp' or os.environ.get('PYTHONDONTWRITEBYTECODE') != '1':
        fail('effective_environment_outside_contract')
    for key in ('TEMP', 'TMP', 'TMPDIR'):
        if Path(os.environ.get(key, '')) != temp:
            fail('temporary_environment_mismatch')
    if Path(sys.executable).absolute() != ROOT / '.venv/Scripts/python.exe':
        fail('project_interpreter_required')
    return {'schema_version': '1.0', 'executable': sys.executable, 'python_version': sys.version,
            'cwd': os.getcwd(), 'temp_directory': str(temp),
            'variables': {k: os.environ.get(k) for k in
                          ('TEMP', 'TMP', 'TMPDIR', 'PYTHONPATH', 'PYTHONDONTWRITEBYTECODE')},
            'product_model_usage': 'not_applicable'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    diag = sub.add_parser('diagnose')
    diag.add_argument('--question', type=Path)
    diag.add_argument('--output-dir', type=Path, required=True)
    decide = sub.add_parser('decide')
    decide.add_argument('--diagnosis', type=Path, required=True)
    decide.add_argument('--decision', choices=('accept', 'request_data', 'reject', 'cancel'), required=True)
    decide.add_argument('--actor', required=True)
    decide.add_argument('--confirmed-at', required=True)
    decide.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args(argv)
    attempts = []
    def network_guard(event, arguments):
        if event in ('socket.connect', 'socket.connect_ex', 'socket.getaddrinfo', 'socket.sendto'):
            attempts.append(event)
            fail('network_blocked')
    sys.addaudithook(network_guard)
    owned = False
    phase = 'preflight'
    directory = args.output_dir
    try:
        env = environment()
        path_check(directory, OUTPUT)
        if directory.exists():
            fail('output_exists')
        phase = 'input_validation'
        if args.command == 'diagnose':
            snapshot = load_accepted_profile(LEGACY, ACCEPTANCE)
            question = None
            qhash, qref = None, None
            if args.question:
                if args.question != ROOT / 'configs/w2a-question-v1.json':
                    fail('question_path_not_allowed')
                payload = read_bytes(args.question)
                question = parse(payload)
                qhash, qref = digest(payload), relative(args.question)
                snapshot['input_manifest']['files'].append({'path': qref, 'sha256': qhash})
            diagnosis = diagnose(question, snapshot, rules_module.registered_rules())
            diagnosis.update(run_id=directory.name, question_ref=qref, question_hash=qhash)
            directory = new_run(directory)
            owned = True
            phase = 'computation_evidence'
            save(directory / 'diagnosis.json', diagnosis)
            save(directory / 'input-manifest.json', snapshot['input_manifest'])
            phase = 'reference_verification'
            manifest_check(snapshot['input_manifest'])
            save(directory / 'reference-check.json', {'schema_version': '1.0', 'references_resolvable': True,
                **{k: snapshot[k] for k in ('profile_identity', 'acceptance_basis', 'source_kind')}})
        else:
            diagnosis, _, _ = load_diagnosis(args.diagnosis)
            decision = {k: getattr(args, k) for k in ('decision', 'actor', 'confirmed_at')}
            decision_check(decision, diagnosis)
            # Ownership begins only after the callee creates a fresh directory.
            try:
                record_s2_decision(diagnosis, decision, directory)
            finally:
                owned = directory.is_dir()
        phase = 'environment_evidence'
        save(directory / 'environment.json', env)
        phase = 'network_evidence'
        save(directory / 'network-observation.json', {'schema_version': '1.0', 'blocked_events': attempts,
            'scope': 'This Python process audit events only; not system isolation or coordinated tamper defense.',
            'product_model_usage': 'not_applicable', 'duckdb_started': False})
        phase = 'command_evidence'
        save(directory / 'cli-command.json', {'schema_version': '1.0',
            'argv': [sys.executable, '-m', 'datainsight.feasibility', *(argv if argv is not None else sys.argv[1:])],
            'status': 'computed_pending_finalization', 'exit_status': None,
            'exit_status_ref': 'final-status.json#exit_status'})
        phase = 'final_status_publication'
        publish(directory, {'schema_version': '1.0', 'run_id': directory.name, 'command': args.command,
            'status': 'success', 'exit_status': 0, 'completed_at': now(), 'required_evidence_refs': list(REQUIRED)})
    except (ValueError, OSError, KeyError, TypeError, RecursionError) as error:
        reason = str(error) if type(error) is BoundaryError else 'controlled_w2a_operation_failed'
        persisted = False
        if owned:
            try:
                publish(directory, {'schema_version': '1.0', 'run_id': directory.name,
                    'command': args.command, 'status': 'failed', 'exit_status': 2,
                    'failed_at': now(), 'phase': phase, 'reason_code': reason})
                persisted = True
            except (ValueError, OSError, KeyError, TypeError):
                pass
        print(json.dumps({'status': 'failed', 'phase': phase, 'exit_status': 2,
                          'reason_code': reason, 'failure_evidence_persisted': persisted}))
        return 2
    print(json.dumps({'status': 'success', 'exit_status': 0, 'output_dir': str(directory),
                      'acceptance_scope': 'S2_only', 'final_acceptance': 'not_performed'}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
