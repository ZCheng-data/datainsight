"""W1-B fixed strict CSV contract. No raw-row product output interface."""
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import hashlib
import sys
from .inspection import fingerprint_file, output_target, inside, AccessPolicy, SourceRequest, now
import duckdb
from .inspection import BoundaryError, ValidatedSource, normalized, check_components, validate_source

ROOT = Path(__file__).resolve().parents[2]
COLUMNS = ('user_id', 'goods_id', 'category_id', 'behaviour', 'timestamp')
CONTRACT_PATH = ROOT / 'configs/w1b-read-contract-v1.json'
EXPECTED = {
    'version': '1.0', 'source_id': 'textbook_userbehavior', 'header': False,
    'columns': {name: 'VARCHAR' for name in COLUMNS}, 'delimiter': ',',
    'encoding': 'utf-8', 'quote': '"', 'escape': '"', 'nullstr': '',
    'allow_quoted_nulls': True, 'auto_detect': False, 'ignore_errors': False,
    'strict_mode': True, 'null_padding': False, 'trim': False,
    'bad_rows': 'error_and_stop', 'time_unit': 'unknown', 'timezone': 'unknown',
}


@dataclass(frozen=True)
class ReadContract:
    values: dict


@dataclass(frozen=True)
class ValidatedReadContract:
    canonical_json: str


def validate_read_contract(contract: ReadContract) -> ValidatedReadContract:
    if type(contract) is not ReadContract or type(contract.values) is not dict:
        raise BoundaryError('invalid_read_contract')
    try:
        encoded = json.dumps(contract.values, sort_keys=True, separators=(',', ':'), allow_nan=False)
    except (ValueError, TypeError):
        raise BoundaryError('invalid_read_contract') from None
    expected = json.dumps(EXPECTED, sort_keys=True, separators=(',', ':'))
    if encoded != expected or list(contract.values['columns']) != list(COLUMNS):
        raise BoundaryError('read_contract_mismatch')
    return ValidatedReadContract(expected)


def load_read_contract():
    check_components(normalized(CONTRACT_PATH))
    try:
        data = json.loads(CONTRACT_PATH.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        raise BoundaryError('read_contract_load_failed') from None
    return validate_read_contract(ReadContract(data))


def check_contract(contract):
    if type(contract) is not ValidatedReadContract or contract != validate_read_contract(ReadContract(dict(EXPECTED))):
        raise BoundaryError('invalid_validated_contract')


def connect_profile():
    if duckdb.__version__ != '1.4.1':
        raise BoundaryError('duckdb_version_mismatch')
    config = {
        'temp_directory': str(ROOT / '.cache/duckdb/tmp'),
        'extension_directory': str(ROOT / '.cache/duckdb/extensions'),
        'autoinstall_known_extensions': 'false',
        'autoload_known_extensions': 'false',
        'allow_unsigned_extensions': 'false',
        'enable_external_access': 'true',
    }
    for key in ('temp_directory', 'extension_directory'):
        path = normalized(config[key])
        check_components(path)
        path.mkdir(parents=True, exist_ok=True)
    try:
        connection = duckdb.connect(database=':memory:', config=config)
        observed = dict(connection.execute("SELECT name, value FROM duckdb_settings() WHERE name IN ('temp_directory','extension_directory','autoinstall_known_extensions','autoload_known_extensions','allow_unsigned_extensions','enable_external_access')").fetchall())
        if observed != config:
            connection.close()
            raise BoundaryError('duckdb_configuration_mismatch')
        return connection, observed
    except duckdb.Error:
        raise BoundaryError('duckdb_connection_failed') from None


READ_RELATION = """read_csv(?, header=false, auto_detect=false,
columns={'user_id':'VARCHAR','goods_id':'VARCHAR','category_id':'VARCHAR','behaviour':'VARCHAR','timestamp':'VARCHAR'},
delim=',', encoding='utf-8', quote='"', escape='"', nullstr='', allow_quoted_nulls=true,
ignore_errors=false, strict_mode=true, null_padding=false)"""


def validate_profile_source(source: ValidatedSource, contract: ValidatedReadContract):
    check_contract(contract)
    if type(source) is not ValidatedSource:
        raise BoundaryError('invalid_profile_source')
    # Revalidate actual path; caller-created policy cannot grant new access.
    from .inspection import AccessPolicy
    production = Path('D:/大数据项目/电商用户行为分析/第9章/UserBehavior.csv')
    policy = AccessPolicy((production,), ROOT / 'tests/fixtures', ROOT / 'outputs/W1-B')
    checked = validate_source(source.request, policy)
    if checked.path != source.path or source.request.mode != 'file' or source.path.suffix.lower() != '.csv':
        raise BoundaryError('profile_source_mismatch')
    return checked


def strict_csv_check(source: ValidatedSource, contract: ValidatedReadContract):
    """Aggregate every field to force full strict parsing, never return records."""
    checked = validate_profile_source(source, contract)
    connection, observed = connect_profile()
    try:
        sql = 'SELECT COUNT(*) AS row_count, ' + ', '.join('COUNT(' + name + ') AS ' + name + '_nonnull' for name in COLUMNS) + ' FROM ' + READ_RELATION
        row = connection.execute(sql, [str(checked.path)]).fetchone()
        schema = connection.execute('SELECT * FROM ' + READ_RELATION + ' LIMIT 0', [str(checked.path)]).description
        return {'row_count': row[0], 'nonnull': dict(zip(COLUMNS, row[1:])),
                'read_schema': [{'name': item[0], 'type': str(item[1])} for item in schema],
                'engine_configuration': observed}
    except duckdb.Error:
        raise BoundaryError('strict_csv_parse_failed') from None
    finally:
        connection.close()


@dataclass(frozen=True)
class ValidatedResult:
    rows: list


@dataclass(frozen=True)
class TemplateEvidence:
    template_id: str
    template_version: str
    template_sha256: str
    sql: str
    parameters: list
    result: ValidatedResult
    engine_configuration: dict


def validate_profile_result(template_id, result: object) -> ValidatedResult:
    from .profile_templates import ProfileTemplateId, FIELDS, COLUMNS as names
    if type(template_id) is not ProfileTemplateId:
        raise BoundaryError('unknown_profile_template')
    if type(result) is not list or len(result) > 100:
        raise BoundaryError('profile_result_row_boundary')
    try:
        encoded = json.dumps(result, allow_nan=False, ensure_ascii=True).encode('utf-8')
    except (ValueError, TypeError):
        raise BoundaryError('profile_result_invalid') from None
    if len(encoded) > 64 * 1024:
        raise BoundaryError('profile_result_byte_boundary')
    expected_rows = len(names) if template_id == ProfileTemplateId.COLUMNS else 1
    if len(result) != expected_rows:
        raise BoundaryError('profile_result_structure')
    for index, row in enumerate(result):
        if type(row) is not dict or set(row) != set(FIELDS[template_id]):
            raise BoundaryError('profile_result_structure')
        for key, value in row.items():
            if key == 'column_name':
                if value != names[index]:
                    raise BoundaryError('profile_result_structure')
            elif key in ('minimum', 'maximum'):
                if value is not None and (type(value) is not int or not -(2**63) <= value < 2**63):
                    raise BoundaryError('profile_result_type')
            elif type(value) is not int or value < 0:
                raise BoundaryError('profile_result_type')
        if template_id == ProfileTemplateId.TIMESTAMP:
            if row['valid_integer'] == 0:
                if row['minimum'] is not None or row['maximum'] is not None:
                    raise BoundaryError('profile_result_structure')
            elif row['minimum'] is None or row['maximum'] is None or row['minimum'] > row['maximum']:
                raise BoundaryError('profile_result_structure')
    return ValidatedResult(result)


def execute_profile_template(template_id, source: ValidatedSource,
                             contract: ValidatedReadContract) -> TemplateEvidence:
    from .profile_templates import build_template, template_hash, FIELDS, VERSION
    sql = build_template(template_id)
    checked = validate_profile_source(source, contract)
    connection, settings = connect_profile()
    try:
        cursor = connection.execute(sql, [str(checked.path)])
        fields = tuple(item[0] for item in cursor.description)
        if fields != FIELDS[template_id]:
            raise BoundaryError('profile_result_schema')
        rows = [dict(zip(fields, row)) for row in cursor.fetchmany(101)]
        result = validate_profile_result(template_id, rows)
        return TemplateEvidence(template_id.value, VERSION, template_hash(template_id),
                                sql, [str(checked.path)], result, settings)
    except duckdb.Error:
        raise BoundaryError('profile_template_failed') from None
    finally:
        connection.close()


OUTPUT_POLICY = AccessPolicy((), ROOT / 'tests/fixtures', ROOT / 'outputs/W1-B')
BASELINE = '7095a57fbd6eb1292bec5ccde4713ac256678b8551eb478d3b5aaad89612cfb4'


@dataclass(frozen=True)
class ProfileRun:
    run_id: str
    status: str
    profile_ref: str


@dataclass(frozen=True)
class ReplayResult:
    status: str
    consistent: bool
    result_ref: str


def json_bytes(data):
    return (json.dumps(data, ensure_ascii=True, sort_keys=True, indent=2, allow_nan=False) + '\n').encode('utf-8')


def save_profile_json(path, data):
    path = output_target(path, OUTPUT_POLICY)
    payload = json_bytes(data)
    with path.open('xb') as stream:
        stream.write(payload)
    return hashlib.sha256(payload).hexdigest()


def new_output(directory):
    directory = normalized(directory)
    if not inside(directory, OUTPUT_POLICY.output_root) or directory == OUTPUT_POLICY.output_root:
        raise BoundaryError('output_outside_policy')
    check_components(directory)
    if directory.exists():
        raise BoundaryError('output_exists')
    directory.mkdir(parents=True)
    return directory


def contract_identity(contract):
    check_contract(contract)
    loaded = load_read_contract()
    if loaded != contract:
        raise BoundaryError('contract_changed')
    return hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest()


def run_profile(source: ValidatedSource, contract: ValidatedReadContract, output_dir: Path) -> ProfileRun:
    from .profile_templates import ProfileTemplateId, VERSION
    source = validate_profile_source(source, contract)
    contract_hash = contract_identity(contract)
    before = fingerprint_file(source)
    production = source.path == Path('D:/大数据项目/电商用户行为分析/第9章/UserBehavior.csv')
    if production and before.sha256 != BASELINE:
        raise BoundaryError('source_version_changed')
    directory = new_output(output_dir)
    run_id = directory.name
    try:
        metrics = {}
        for template in ProfileTemplateId:
            started = now()
            evidence = execute_profile_template(template, source, contract)
            evidence_id = run_id + ':' + template.value
            result_ref = template.value + '-result.json'
            result_hash = save_profile_json(directory / result_ref, evidence.result.rows)
            data = {'schema_version': '1.0', 'evidence_id': evidence_id, 'run_id': run_id,
                'dataset_version': before.sha256, 'source_id': source.request.source_id,
                'source_path': str(source.path), 'read_config_ref': 'configs/w1b-read-contract-v1.json',
                'read_config_version': '1.0', 'read_config_sha256': contract_hash,
                'template_id': template.value, 'template_version': VERSION,
                'template_sha256': evidence.template_sha256, 'sql': evidence.sql,
                'parameters': evidence.parameters, 'python_version': sys.version,
                'duckdb_version': duckdb.__version__, 'status': 'success',
                'started_at': started, 'ended_at': now(), 'result_ref': result_ref,
                'result_sha256': result_hash, 'metric_definition_version': '1.0',
                'engine_configuration': evidence.engine_configuration}
            save_profile_json(directory / (template.value + '-evidence.json'), data)
            metrics[template.value] = {'evidence_id': evidence_id, 'result_ref': result_ref,
                                       'values': evidence.result.rows}
        after = fingerprint_file(source)
        save_profile_json(directory / 'fingerprints.json', {'before': asdict(before), 'after': asdict(after),
            'consistent': before.sha256 == after.sha256})
        if before.sha256 != after.sha256:
            raise BoundaryError('source_changed_during_profile')
        save_profile_json(directory / 'profile.json', {'schema_version': '1.0', 'run_id': run_id,
            'stage': 'S1', 'status': 'computed_pending_finalization', 'dataset_version': before.sha256,
            'reading_schema': [{'name': name, 'type': 'VARCHAR'} for name in COLUMNS],
            'metrics': metrics, 'product_model_usage': 'not_applicable',
            'limitations': ['specified reading schema, not inferred natural types',
                'duplicate candidates are not errors; no deletion',
                'timestamp unit and timezone unknown; no dates', 'no business conclusions']})
        return ProfileRun(run_id, 'computed_pending_finalization', str(directory / 'profile.json'))
    except (BoundaryError, OSError):
        save_profile_json(directory / 'failure.json', {'status': 'failed', 'reason_code': 'profile_run_failed'})
        raise


def read_evidence_bytes(path):
    path = normalized(path)
    if not inside(path, OUTPUT_POLICY.output_root):
        raise BoundaryError('evidence_outside_policy')
    check_components(path)
    try:
        if path.stat().st_size > 128 * 1024:
            raise BoundaryError('evidence_size_boundary')
        payload = path.read_bytes()
        if len(payload) > 128 * 1024:
            raise BoundaryError('evidence_size_boundary')
        return payload
    except OSError:
        raise BoundaryError('evidence_read_failed') from None


def parse_evidence_bytes(payload):
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise BoundaryError('duplicate_evidence_key')
            result[key] = value
        return result
    try:
        return json.loads(payload.decode('utf-8'), object_pairs_hook=unique_pairs,
            parse_constant=lambda value: (_ for _ in ()).throw(BoundaryError('nonfinite_evidence_value')))
    except (ValueError, UnicodeError):
        raise BoundaryError('evidence_parse_failed') from None


def read_evidence_json(path):
    return parse_evidence_bytes(read_evidence_bytes(path))


def verify_profile_references(directory):
    """Contract-specific reference audit; IDs resolve separately from file refs."""
    from .profile_templates import ProfileTemplateId
    directory = normalized(directory)
    check_components(directory)
    checked = []
    if (directory / 'profile.json').exists():
        profile = read_evidence_json(directory / 'profile.json')
        for template in ProfileTemplateId:
            evidence_path = directory / (template.value + '-evidence.json')
            evidence = read_evidence_json(evidence_path)
            metric = profile['metrics'][template.value]
            if metric['evidence_id'] != evidence['evidence_id']:
                raise BoundaryError('metric_evidence_reference_mismatch')
            result_path = directory / evidence['result_ref']
            payload = read_evidence_bytes(result_path)
            if hashlib.sha256(payload).hexdigest() != evidence['result_sha256'] or parse_evidence_bytes(payload) != metric['values']:
                raise BoundaryError('metric_result_reference_mismatch')
            if metric['result_ref'] != evidence['result_ref']:
                raise BoundaryError('metric_result_reference_mismatch')
            contract_path = ROOT / evidence['read_config_ref']
            if contract_path != CONTRACT_PATH:
                raise BoundaryError('contract_reference_mismatch')
            check_components(contract_path)
            if hashlib.sha256(contract_path.read_bytes()).hexdigest() != evidence['read_config_sha256']:
                raise BoundaryError('contract_reference_mismatch')
            checked += [str(evidence_path), str(result_path), str(contract_path)]
    if (directory / 'replay.json').exists():
        replay = read_evidence_json(directory / 'replay.json')
        original_path = Path(replay['original_evidence_ref'])
        original = read_evidence_json(original_path)
        if original['evidence_id'] != replay['original_evidence_id']:
            raise BoundaryError('replay_reference_mismatch')
        checked.append(str(original_path))
    fingerprints = read_evidence_json(directory / 'fingerprints.json')
    for phase in ('before', 'after'):
        fp = fingerprints[phase]
        if fp['evidence_ref'] != 'fingerprints.json':
            raise BoundaryError('fingerprint_reference_mismatch')
        if (directory / 'replay.json').exists() and replay['fingerprints'][phase] != fp:
            raise BoundaryError('fingerprint_reference_mismatch')
        checked.append(str(directory / fp['evidence_ref']))
    return {'references_resolvable': True, 'checked_targets': checked}


def replay_profile_evidence(evidence_ref: Path, output_dir: Path) -> ReplayResult:
    from .profile_templates import ProfileTemplateId, build_template, template_hash, VERSION
    data = read_evidence_json(evidence_ref)
    fields = {'schema_version','evidence_id','run_id','dataset_version','source_id','source_path',
        'read_config_ref','read_config_version','read_config_sha256','template_id','template_version',
        'template_sha256','sql','parameters','python_version','duckdb_version','status','started_at',
        'ended_at','result_ref','result_sha256','metric_definition_version','engine_configuration'}
    if type(data) is not dict or set(data) != fields:
        raise BoundaryError('invalid_evidence_structure')
    for key in fields - {'parameters', 'engine_configuration'}:
        if type(data[key]) is not str or not data[key]:
            raise BoundaryError('invalid_evidence_type')
    if type(data['parameters']) is not list or data['parameters'] != [data['source_path']]:
        raise BoundaryError('invalid_evidence_parameters')
    if type(data['engine_configuration']) is not dict:
        raise BoundaryError('invalid_engine_evidence')
    try:
        template = ProfileTemplateId(data['template_id'])
    except ValueError:
        raise BoundaryError('unknown_profile_template') from None
    contract = load_read_contract()
    if (data['schema_version'] != '1.0' or data['read_config_ref'] != 'configs/w1b-read-contract-v1.json'
        or data['read_config_version'] != '1.0' or data['read_config_sha256'] != contract_identity(contract)
        or data['template_version'] != VERSION or data['template_sha256'] != template_hash(template)
        or data['sql'] != build_template(template) or data['duckdb_version'] != duckdb.__version__
        or data['python_version'] != sys.version or data['status'] != 'success'
        or data['metric_definition_version'] != '1.0'):
        raise BoundaryError('evidence_identity_mismatch')
    if data['run_id'] != Path(evidence_ref).parent.name or data['evidence_id'] != data['run_id'] + ':' + template.value:
        raise BoundaryError('evidence_run_mismatch')
    for key in ('dataset_version', 'read_config_sha256', 'template_sha256', 'result_sha256'):
        if len(data[key]) != 64 or any(c not in '0123456789abcdef' for c in data[key]):
            raise BoundaryError('invalid_evidence_digest')
    ref = data['result_ref']
    if ref != template.value + '-result.json':
        raise BoundaryError('invalid_result_reference')
    result_path = Path(evidence_ref).parent / ref
    payload = read_evidence_bytes(result_path)
    if hashlib.sha256(payload).hexdigest() != data['result_sha256']:
        raise BoundaryError('result_digest_mismatch')
    saved = parse_evidence_bytes(payload)
    validate_profile_result(template, saved)
    policy = AccessPolicy((Path('D:/大数据项目/电商用户行为分析/第9章/UserBehavior.csv'),),
                          ROOT / 'tests/fixtures', OUTPUT_POLICY.output_root)
    source = validate_source(SourceRequest(data['source_id'], Path(data['source_path']), 'file', data['read_config_ref']), policy)
    before = fingerprint_file(source)
    if before.sha256 != data['dataset_version']:
        raise BoundaryError('replay_source_changed')
    directory = new_output(output_dir)
    evidence = execute_profile_template(template, source, contract)
    after = fingerprint_file(source)
    consistent = before.sha256 == after.sha256 and evidence.result.rows == saved
    save_profile_json(directory / 'replay.json', {'status': 'computed_pending_finalization' if consistent else 'failed',
        'consistent': consistent, 'original_evidence_id': data['evidence_id'],
        'original_evidence_ref': str(normalized(evidence_ref)),
        'result': evidence.result.rows, 'fingerprints': {'before': asdict(before), 'after': asdict(after)}})
    save_profile_json(directory / 'fingerprints.json', {'before': asdict(before), 'after': asdict(after),
        'consistent': before.sha256 == after.sha256})
    if not consistent:
        raise BoundaryError('replay_mismatch')
    return ReplayResult('computed_pending_finalization', True, str(directory / 'replay.json'))
