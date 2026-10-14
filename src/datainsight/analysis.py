"""W3: one fixed method, explicit preservation receipt and local pending draft."""
import argparse
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import sys
import time
from . import feasibility as f, planning as p, planning_methods as methods
from . import profile, profile_templates as templates
from .inspection import AccessPolicy, SourceRequest, validate_source

ROOT = f.ROOT
OUTPUT = ROOT / 'outputs/W3'
S3 = p.OUTPUT / 'w2b1-review-219e79901d08444bab62c6e61f6e2211/s3-review.json'
SOURCE = Path('D:/大数据项目/电商用户行为分析/第9章/UserBehavior.csv')
QUESTION = ROOT / 'configs/w2a-question-v1.json'
LIMIT = 1024 * 1024
RESULT_LIMIT = 64 * 1024
DEADLINE = 180
BUCKETS = ('pv', 'fav', 'cart', 'buy', 'missing', 'other')
CLAIM = 'behaviour_bucket_raw_record_count'
STRATEGY_VERSION = 'preserve-all-v1'
QUERY_COUNT = 0
WORKER_OBSERVATION = {}
SAFE_REASONS = set()


@dataclass(frozen=True)
class ExecutionContext:
    bindings: dict


@dataclass(frozen=True)
class StrategySpec:
    decision: str
    actor: str
    confirmed_at: str


@dataclass(frozen=True)
class StrategyReceipt:
    value: dict


@dataclass(frozen=True)
class CalculationEvidence:
    value: dict


@dataclass(frozen=True)
class ValidationResult:
    value: dict


@dataclass(frozen=True)
class ValidatedClaims:
    values: list


@dataclass(frozen=True)
class W3Run:
    value: dict


def fail(reason):
    SAFE_REASONS.add(reason)
    f.fail(reason)


def safe_reason(error):
    reason = str(error)
    known = {'invalid_object_keys', 'profile_result_structure', 'profile_result_type',
             'profile_result_byte_boundary', 'profile_result_row_boundary', 'profile_result_invalid',
             'file_missing_or_size_boundary', 'invalid_success_terminal', 'planning_terminal_invalid',
             's3_receipt_binding_changed', 'candidate_plan_changed', 'planning_manifest_changed',
             'stored_context_changed', 'invalid_identifier', 'invalid_hash'}
    return reason if reason in SAFE_REASONS or reason in known else 'w3_internal_failure'


def expected_configuration():
    return {'memory_limit': '256.0 MiB', 'threads': '1',
        'temp_directory': str(ROOT / '.cache/duckdb/tmp'),
        'extension_directory': str(ROOT / '.cache/duckdb/extensions'),
        'autoinstall_known_extensions': 'false', 'autoload_known_extensions': 'false',
        'allow_unsigned_extensions': 'false', 'enable_external_access': 'true'}


def payload(value):
    data = f.encoded(value)
    if len(data) > LIMIT:
        fail('document_byte_boundary')
    return data


def read(path):
    path = f.path_check(Path(path), ROOT)
    if not path.is_file() or path.stat().st_size > LIMIT:
        fail('evidence_missing_or_size')
    data = path.read_bytes()
    if len(data) > LIMIT:
        fail('document_byte_boundary')
    return data


def save(path, value):
    data = value if type(value) is bytes else payload(value)
    if len(data) > LIMIT:
        fail('document_byte_boundary')
    f.path_check(path, OUTPUT)
    with path.open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    return f.digest(data)


def new_run(directory):
    directory = f.path_check(Path(directory), OUTPUT)
    if directory.parent != OUTPUT:
        fail('run_direct_child_required')
    f.identifier(directory.name)
    if directory.exists():
        fail('output_exists')
    directory.mkdir(parents=True)
    return directory


def publish(directory, value, end=None):
    target = directory / 'final-status.json'
    stage = directory / ('final-status-' + value['status'] + '.tmp')
    if target.exists():
        fail('terminal_exists')
    if end is not None:
        remaining(end)
    save(stage, value)
    if end is not None:
        remaining(end)
    if target.exists():
        fail('terminal_exists')
    # Windows rename is no-replace; refuse a different host rather than weaken it.
    if os.name != 'nt':
        fail('no_replace_publication_unavailable')
    if end is not None:
        remaining(end)
    stage.rename(target)


def terminal(directory, command):
    value = f.parse(read(directory / 'final-status.json'))
    f.exact(value, ('schema_version', 'run_id', 'command', 'status', 'exit_status',
                    'completed_at', 'required_hashes', 'human_review_state'))
    if (value['schema_version'] != '1.0' or value['run_id'] != directory.name or
            value['command'] != command or value['status'] != 'success' or
            type(value['exit_status']) is not int or value['exit_status'] != 0 or
            value['human_review_state'] != 'pending'):
        fail('invalid_success_terminal')
    f.timestamp(value['completed_at'])
    required = ('strategy.json', 'bindings.json', 'operation.json') if command == 'strategy' else (
        'bindings.json', 'calculation-evidence.json', 'result.json', 'validation.json', 'report.md', 'operation.json')
    if type(value['required_hashes']) is not dict or set(value['required_hashes']) != set(required):
        fail('terminal_references')
    for name in required:
        if f.digest(read(directory / name)) != value['required_hashes'][name]:
            fail('artifact_hash_changed')
    return value


def load_w3_context(s3_review_ref):
    path = f.path_check(Path(s3_review_ref), ROOT)
    if path != S3:
        fail('s3_source_not_allowed')
    review = p.verify_review(path)
    if review['decision'] != 'approve':
        fail('s3_not_approved')
    plans, raw, accepted, manifest = p.load_plan_set(ROOT / review['plan_set_ref'])
    chosen = p.review_check({k: review[k] for k in p.REVIEW_KEYS}, plans)
    if (len(plans['candidates']) != 1 or chosen['method_id'] != methods.METHOD or
            chosen['plan_id'] != 'P-BEHAVIOUR-RECORDS'):
        fail('unique_method_required')
    if chosen['metric_definition'] != methods.definition():
        fail('metric_definition_changed')
    question = f.parse(read(QUESTION))
    if (question.get('intent') != 'behaviour_record_counts' or question.get('requested_unit') != 'raw_record' or
            ROOT / plans['question_identity']['ref'] != QUESTION):
        fail('question_not_allowed')
    contract = profile.load_read_contract()
    files = deepcopy(manifest['files'])
    for folder, names in ((path.parent, ('s3-review.json', 'final-status.json', *p.REQUIRED)),
                          ((ROOT / review['plan_set_ref']).parent,
                           ('candidate-plans.json', 'accepted-context.json', 'final-status.json', *p.REQUIRED))):
        for name in names:
            target = folder / name
            files.append({'path': f.relative(target), 'sha256': f.digest(read(target))})
    files.append({'path': f.relative(profile.CONTRACT_PATH), 'sha256': f.digest(read(profile.CONTRACT_PATH))})
    return ExecutionContext({'schema_version': '1.0', 's3_ref': f.relative(path),
        's3_hash': f.digest(read(path)), 'dataset_version': review['dataset_version'],
        'source_path': str(SOURCE), 'question_identity': plans['question_identity'],
        'diagnostic_rules_identity': plans['diagnostic_rules_identity'],
        'registry_identity': review['registry_identity'], 'plan': chosen,
        'read_contract_hash': f.digest(read(profile.CONTRACT_PATH)),
        'read_contract_canonical': contract.canonical_json, 'files': files})


def check_context(context):
    if type(context) is not ExecutionContext:
        fail('invalid_execution_context')
    current = load_w3_context(ROOT / context.bindings['s3_ref'])
    if payload(current.bindings) != payload(context.bindings):
        fail('context_binding_changed')


def operation(command, phase, reason='ok'):
    import duckdb
    return {'schema_version': '1.0', 'command': command, 'phase': phase, 'reason_code': reason,
        'argv': sys.argv[1:], 'cwd': str(ROOT), 'recorded_at': f.now(),
        'recorded_at_source': 'python_datetime_utc', 'python_version': sys.version.split()[0],
        'duckdb_version': duckdb.__version__, 'model_usage': 'not_applicable',
        'network': 'not_requested', 'human_review_state': 'pending',
        'authorization_scope': 'local_fixed_method_only; source_read_requires_separate_permission'}


def success(directory, command, hashes, end=None):
    value = {'schema_version': '1.0', 'run_id': directory.name, 'command': command,
        'status': 'success', 'exit_status': 0, 'completed_at': f.now(),
        'required_hashes': hashes, 'human_review_state': 'pending'}
    if end is not None:
        remaining(end)
    publish(directory, value, end=end)
    return value


def record_preservation_decision(context, decision, output_dir):
    check_context(context)
    if type(decision) is not StrategySpec or decision.decision not in ('preserve_all', 'reject', 'cancel'):
        fail('invalid_preservation_decision')
    f.identifier(decision.actor)
    if decision.confirmed_at != 'not_provided':
        f.timestamp(decision.confirmed_at)
    directory = new_run(output_dir)
    value = {'schema_version': '1.0', 'run_id': directory.name, 'decision': decision.decision,
        'actor': decision.actor, 'confirmation_basis': 'explicit_strategy_argument',
        'confirmed_at': decision.confirmed_at, 'recorded_at': f.now(),
        'recorded_at_source': 'python_datetime_utc', 'scope': 'S3.5_preserve_all_only',
        'strategy_version': STRATEGY_VERSION, 'bindings_hash': f.digest(payload(context.bindings))}
    hashes = {'bindings.json': save(directory / 'bindings.json', context.bindings),
              'strategy.json': save(directory / 'strategy.json', value),
              'operation.json': save(directory / 'operation.json', operation('strategy', 'recorded'))}
    success(directory, 'strategy', hashes)
    return StrategyReceipt(value)


def load_strategy(path):
    path = f.path_check(Path(path), OUTPUT)
    if path.name != 'strategy.json' or path.parent.parent != OUTPUT:
        fail('strategy_source_not_allowed')
    terminal(path.parent, 'strategy')
    value = f.parse(read(path))
    f.exact(value, ('schema_version', 'run_id', 'decision', 'actor', 'confirmation_basis', 'confirmed_at',
        'recorded_at', 'recorded_at_source', 'scope', 'strategy_version', 'bindings_hash'))
    if value['decision'] != 'preserve_all':
        fail('preservation_not_approved')
    f.identifier(value['actor'])
    f.timestamp(value['recorded_at'])
    if value['confirmed_at'] != 'not_provided':
        f.timestamp(value['confirmed_at'])
    if (value['run_id'] != path.parent.name or value['scope'] != 'S3.5_preserve_all_only' or
            value['strategy_version'] != STRATEGY_VERSION or value['schema_version'] != '1.0' or
            value['confirmation_basis'] != 'explicit_strategy_argument' or
            value['recorded_at_source'] != 'python_datetime_utc'):
        fail('strategy_identity_changed')
    bindings = f.parse(read(path.parent / 'bindings.json'))
    context = load_w3_context(ROOT / bindings['s3_ref'])
    if payload(bindings) != payload(context.bindings) or value['bindings_hash'] != f.digest(payload(bindings)):
        fail('strategy_binding_changed')
    return context, StrategyReceipt(value)


def source_check(path):
    if Path(path) != SOURCE:
        fail('source_not_allowed')
    source = validate_source(SourceRequest('textbook_userbehavior', Path(path), 'file',
        f.relative(profile.CONTRACT_PATH)),
        AccessPolicy((SOURCE,), ROOT / 'tests/fixtures/w3', OUTPUT))
    return profile.validate_profile_source(source, profile.load_read_contract())


def remaining(end):
    seconds = end - time.monotonic()
    if seconds <= 0:
        fail('execution_deadline')
    return seconds


def fingerprint(path, end):
    source_check(path)
    started = f.now()
    h = hashlib.sha256()
    count = 0
    with Path(path).open('rb') as stream:
        while True:
            remaining(end)
            block = stream.read(1024 * 1024)
            if not block:
                break
            count += len(block)
            h.update(block)
    return {'sha256': h.hexdigest(), 'bytes_read': count, 'started_at': started, 'ended_at': f.now()}


def fixed_sql():
    return {'strict': 'SELECT COUNT(*) AS row_count, ' + ', '.join(
        'COUNT(' + name + ') AS ' + name + '_nonnull' for name in profile.COLUMNS) + ' FROM ' + profile.READ_RELATION,
        'schema': 'SELECT * FROM ' + profile.READ_RELATION + ' LIMIT 0',
        'behaviours': templates.build_template(templates.ProfileTemplateId.BEHAVIOURS),
        'summary': templates.build_template(templates.ProfileTemplateId.SUMMARY)}


def calculate(bindings, receipt, source_path):
    """Worker rechecks source, bound files and strategy before opening DuckDB."""
    global QUERY_COUNT
    import duckdb
    if sys.version_info[:3] != (3, 12, 9) or duckdb.__version__ != '1.4.1':
        fail('dependency_version_mismatch')
    if (receipt.get('decision') != 'preserve_all' or receipt.get('scope') != 'S3.5_preserve_all_only' or
            receipt.get('strategy_version') != STRATEGY_VERSION or
            receipt.get('bindings_hash') != f.digest(payload(bindings))):
        fail('worker_strategy_invalid')
    if bindings['plan']['metric_definition'] != methods.definition():
        fail('worker_metric_invalid')
    for item in bindings['files']:
        if f.digest(read(ROOT / item['path'])) != item['sha256']:
            fail('worker_binding_changed')
    if str(source_path) != bindings['source_path']:
        fail('worker_source_invalid')
    source = source_check(source_path)
    settings = {'memory_limit': '256MiB', 'threads': '1',
        'temp_directory': str(ROOT / '.cache/duckdb/tmp'),
        'extension_directory': str(ROOT / '.cache/duckdb/extensions'),
        'autoinstall_known_extensions': 'false', 'autoload_known_extensions': 'false',
        'allow_unsigned_extensions': 'false', 'enable_external_access': 'true'}
    for key in ('temp_directory', 'extension_directory'):
        f.path_check(Path(settings[key]), ROOT).mkdir(parents=True, exist_ok=True)
    sqls = fixed_sql()
    connection = duckdb.connect(':memory:', config=settings)
    try:
        QUERY_COUNT += 1
        observed = dict(connection.execute("SELECT name, value FROM duckdb_settings() WHERE name IN ('memory_limit','threads','temp_directory','extension_directory','autoinstall_known_extensions','autoload_known_extensions','allow_unsigned_extensions','enable_external_access')").fetchall())
        expected = dict(settings, memory_limit='256.0 MiB')
        if observed != expected:
            fail('resource_configuration_mismatch')
        def query(key):
            global QUERY_COUNT
            QUERY_COUNT += 1
            return connection.execute(sqls[key], [str(source.path)])
        strict = query('strict').fetchone()
        schema = query('schema').description
        if [(i[0], str(i[1])) for i in schema] != [(n, 'VARCHAR') for n in profile.COLUMNS]:
            fail('read_schema_mismatch')
        cursor = query('behaviours')
        if tuple(i[0] for i in cursor.description) != BUCKETS:
            fail('result_schema')
        rows = [dict(zip(BUCKETS, row)) for row in cursor.fetchmany(2)]
        profile.validate_profile_result(templates.ProfileTemplateId.BEHAVIOURS, rows)
        count = query('summary').fetchone()[0]
        if count != strict[0] or sum(rows[0].values()) != count:
            fail('bucket_coverage_mismatch')
        result = {'buckets': rows[0], 'row_count': count}
        if len(payload(result)) > RESULT_LIMIT:
            fail('result_byte_boundary')
        return {'status': 'success', 'result': result, 'sql': sqls, 'parameters': [str(source.path)],
            'sql_hashes': {k: f.digest(v.encode()) for k, v in sqls.items()},
            'engine_configuration': observed, 'query_count': QUERY_COUNT,
            'read_schema': [{'name': i[0], 'type': str(i[1])} for i in schema],
            'strict_row_count': strict[0], 'python_version': sys.version.split()[0], 'duckdb_version': duckdb.__version__}
    finally:
        connection.close()


def _worker(send, strategy_ref, bindings_hash, strategy_hash, seconds):
    try:
        end = time.monotonic() + seconds
        context, strategy = load_strategy(Path(strategy_ref))
        if (f.digest(payload(context.bindings)) != bindings_hash or
                f.digest(payload(strategy.value)) != strategy_hash):
            fail('worker_consumed_binding_changed')
        remaining(end)
        before = fingerprint(SOURCE, end)
        if before['sha256'] != context.bindings['dataset_version']:
            fail('worker_source_version_changed')
        value = calculate(context.bindings, strategy.value, str(SOURCE))
        remaining(end)
        send.send_bytes(payload(value))
    except BaseException as error:
        send.send_bytes(payload({'status': 'failed', 'reason_code': safe_reason(error)}))
    finally:
        send.close()


def supervised(context, strategy, end):
    global QUERY_COUNT, WORKER_OBSERVATION
    WORKER_OBSERVATION = {'started': False, 'terminated': False, 'reaped': False}
    # Consume a receipt path again in the fixed worker; a self-hashed dict is not approval.
    receiver, sender = mp.get_context('spawn').Pipe(duplex=False)
    process = mp.get_context('spawn').Process(target=_worker,
        args=(sender, str(OUTPUT / strategy.value['run_id'] / 'strategy.json'),
              f.digest(payload(context.bindings)), f.digest(payload(strategy.value)), remaining(end)))
    process.start()
    WORKER_OBSERVATION.update(started=True, pid=process.pid)
    sender.close()
    terminated = False
    try:
        if not receiver.poll(remaining(end)):
            terminated = True
            process.terminate()
            process.join(5)
            if process.is_alive():
                process.kill()
                process.join(5)
            fail('worker_timeout_reaped' if not process.is_alive() else 'worker_reap_failed')
        raw = receiver.recv_bytes(LIMIT)
        process.join(min(5, remaining(end)))
        if process.is_alive():
            fail('worker_exit_timeout')
        if process.exitcode != 0:
            fail('worker_exit_failed')
        value = f.parse(raw)
        if value.get('status') != 'success':
            allowed = {'worker_source_version_changed', 'worker_consumed_binding_changed',
                       'execution_deadline', 'resource_configuration_mismatch',
                       'worker_strategy_invalid', 'worker_source_invalid', 'worker_binding_changed'}
            reason = value.get('reason_code')
            fail(reason if reason in allowed else 'worker_computation_failed')
        QUERY_COUNT = value['query_count']
        value['worker'] = {'exitcode': process.exitcode, 'reaped': True, 'terminated': terminated}
        return value
    finally:
        if process.is_alive():
            process.terminate()
            process.join(5)
            if process.is_alive():
                process.kill()
                process.join(5)
        receiver.close()
        WORKER_OBSERVATION.update(terminated=terminated, reaped=not process.is_alive(), exitcode=process.exitcode)
        if not process.is_alive():
            process.close()


def claims_for(result):
    return ValidatedClaims([{'claim_type': CLAIM, 'bucket': b,
        'value_ref': 'result.json#/buckets/' + b, 'evidence_ref': 'calculation-evidence.json#/sql/behaviours'} for b in BUCKETS])


def check_claims(claims):
    if type(claims) is not ValidatedClaims or claims.values != claims_for(None).values:
        fail('unsupported_claim')


def validate_s5(context, strategy, calculation):
    value = calculation.value
    states = {}
    def layer(name, function):
        try:
            function()
            states[name] = {'state': 'pass', 'reason_code': 'ok', 'evidence_ref': 'calculation-evidence.json'}
        except (f.BoundaryError, profile.BoundaryError) as error:
            states[name] = {'state': 'fail', 'reason_code': safe_reason(error), 'evidence_ref': 'calculation-evidence.json'}
        except (KeyError, TypeError, ValueError, AttributeError):
            states[name] = {'state': 'fail', 'reason_code': name + '_evidence_structure', 'evidence_ref': 'calculation-evidence.json'}
    def execution():
        if (value['engine_configuration'] != expected_configuration() or
                value['python_version'] != '3.12.9' or value['duckdb_version'] != '1.4.1'):
            fail('execution_environment_mismatch')
        if (value['status'] != 'success' or value['before']['sha256'] != context.bindings['dataset_version'] or
                value['after']['sha256'] != value['before']['sha256'] or
                value['before']['bytes_read'] != value['after']['bytes_read'] or
                value['bindings_hash'] != f.digest(payload(context.bindings)) or
                value['strategy_hash'] != f.digest(payload(strategy.value))):
            fail('execution_binding')
        result = value['result']
        f.exact(result, ('buckets', 'row_count'))
        profile.validate_profile_result(templates.ProfileTemplateId.BEHAVIOURS, [result['buckets']])
        if type(result['row_count']) is not int or result['row_count'] < 0 or sum(result['buckets'].values()) != result['row_count']:
            fail('result_coverage')
        if (len(payload(result)) > RESULT_LIMIT or value['result_hash'] != f.digest(payload(result)) or
                value['strict_row_count'] != result['row_count'] or value['worker']['exitcode'] != 0 or not value['worker']['reaped']):
            fail('result_evidence')
        directory = Path(value['output_dir'])
        if f.digest(read(directory / 'result.json')) != value['result_hash']:
            fail('result_bytes_changed')
        if value['read_schema'] != [{'name': n, 'type': 'VARCHAR'} for n in profile.COLUMNS]:
            fail('read_schema')
    def metric():
        if (context.bindings['plan']['metric_definition'] != methods.definition() or
                context.bindings['plan']['metric_definition_hash'] != f.digest(payload(methods.definition())) or
                strategy.value['decision'] != 'preserve_all' or value['sql'] != fixed_sql() or
                value['parameters'] != [context.bindings['source_path']] or
                value['sql_hashes'] != {k: f.digest(v.encode()) for k, v in fixed_sql().items()} or
                value['read_contract_hash'] != context.bindings['read_contract_hash']):
            fail('metric_binding')
    def boundary():
        check_claims(ValidatedClaims(value['claims']))
    for name, fn in (('execution', execution), ('metric', metric), ('boundary', boundary)):
        layer(name, fn)
    return ValidationResult(states)


def render_report(claims, evidence):
    check_claims(claims)
    value = evidence.value
    if (type(value.get('validation')) is not dict or set(value['validation']) != {'execution', 'metric', 'boundary'} or
            any(v.get('state') != 'pass' for v in value['validation'].values())):
        fail('report_validation_required')
    directory = Path(value['output_dir'])
    if f.parse(read(directory / 'validation.json')) != value['validation']:
        fail('report_validation_changed')
    result_bytes = read(directory / 'result.json')
    if (f.digest(result_bytes) != value['result_hash'] or
            f.parse(result_bytes) != value['result']):
        fail('report_result_changed')
    if value['claims'] != claims.values:
        fail('claim_binding_changed')
    result = value['result']['buckets']
    profile.validate_profile_result(templates.ProfileTemplateId.BEHAVIOURS, [result])
    lines = ['# W3 local draft', '', 'human_review_state=pending',
        'Question: behaviour_record_counts / raw_record',
        'Scope: entire bound file; preserve all raw records; exact text, no trim or case normalization.',
        'NULL behaviour enters missing; other non-NULL codes enter other.',
        'S5: execution=pass; metric=pass; boundary=pass.', '', '| bucket | raw record count | evidence |', '|---|---:|---|']
    for b in BUCKETS:
        lines.append('| ' + b + ' | ' + str(result[b]) + ' | result.json#/buckets/' + b +
                     '; calculation-evidence.json#/sql/behaviours |')
    lines += ['', 'Not orders, payments, unique users, ratios, conversion, dates, effects or causal claims.',
        'Local draft only. Independent S6 human interpretation and external publication permission remain required.',
        'Metric evidence: bindings.json#/plan/metric_definition; calculation-evidence.json#/sql/behaviours.']
    data = ('\n'.join(lines) + '\n').encode()
    if len(data) > LIMIT:
        fail('document_byte_boundary')
    return data


def execute_verified_plan(strategy_ref, output_dir):
    global QUERY_COUNT
    QUERY_COUNT = 0
    end = time.monotonic() + DEADLINE
    context, strategy = load_strategy(strategy_ref)
    remaining(end)
    source_check(SOURCE)
    directory = new_run(output_dir)
    try:
        before = fingerprint(SOURCE, end)
        if before['sha256'] != context.bindings['dataset_version']:
            fail('source_version_changed')
        computation = supervised(context, strategy, end)
        after = fingerprint(SOURCE, end)
        remaining(end)
        check_context(context)
        remaining(end)
        latest_context, latest_strategy = load_strategy(strategy_ref)
        remaining(end)
        if payload(latest_strategy.value) != payload(strategy.value):
            fail('strategy_changed_during_execution')
        result = computation['result']
        remaining(end)
        hashes = {'bindings.json': save(directory / 'bindings.json', context.bindings)}
        remaining(end)
        hashes['result.json'] = save(directory / 'result.json', result)
        remaining(end)
        evidence = CalculationEvidence({**computation, 'before': before, 'after': after,
            'bindings_hash': f.digest(payload(context.bindings)), 'strategy_hash': f.digest(payload(strategy.value)),
            'strategy_ref': f.relative(Path(strategy_ref)), 'read_contract_hash': context.bindings['read_contract_hash'],
            'result_hash': hashes['result.json'], 'output_dir': str(directory),
            'claims': claims_for(result).values, 'deadline_seconds': DEADLINE})
        validation = validate_s5(context, strategy, evidence)
        remaining(end)
        evidence.value['validation'] = validation.value
        hashes['calculation-evidence.json'] = save(directory / 'calculation-evidence.json', evidence.value)
        remaining(end)
        hashes['validation.json'] = save(directory / 'validation.json', validation.value)
        remaining(end)
        if any(v['state'] != 'pass' for v in validation.value.values()):
            fail('s5_failed')
        report = render_report(claims_for(result), evidence)
        remaining(end)
        hashes['report.md'] = save(directory / 'report.md', report)
        remaining(end)
        if read(directory / 'report.md') != render_report(claims_for(result), evidence):
            fail('report_changed')
        remaining(end)
        hashes['operation.json'] = save(directory / 'operation.json', operation('execute', 'completed'))
        remaining(end)
        # Consumer checks before final publication, rather than trusting write returns.
        for name, digest in hashes.items():
            if f.digest(read(directory / name)) != digest:
                fail('artifact_changed_before_publication')
            remaining(end)
        remaining(end)
        value = success(directory, 'execute', hashes, end=end)
        return W3Run(value)
    except BaseException as error:
        reason = safe_reason(error)
        persisted = False
        operation_persisted = (directory / 'operation.json').exists()
        try:
            if not operation_persisted:
                save(directory / 'operation.json', operation('execute', 'failed', reason))
                operation_persisted = True
        except BaseException:
            pass
        try:
            publish(directory, {'schema_version': '1.0', 'run_id': directory.name, 'command': 'execute',
                'status': 'failed', 'exit_status': 1, 'completed_at': f.now(), 'required_hashes': {},
                'human_review_state': 'pending'})
            persisted = True
        except BaseException:
            pass
        print(json.dumps({'phase': 'execute', 'reason_code': reason,
                          'failure_evidence_persisted': persisted and operation_persisted,
                          'failure_terminal_persisted': persisted,
                          'failure_operation_persisted': operation_persisted}), file=sys.stderr)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    strategy = sub.add_parser('strategy')
    strategy.add_argument('--decision', choices=('preserve_all', 'reject', 'cancel'), required=True)
    strategy.add_argument('--actor', required=True)
    strategy.add_argument('--confirmed-at', required=True)
    strategy.add_argument('--output-dir', required=True)
    execute = sub.add_parser('execute')
    execute.add_argument('--strategy', required=True)
    execute.add_argument('--output-dir', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'strategy':
            record_preservation_decision(load_w3_context(S3),
                StrategySpec(args.decision, args.actor, args.confirmed_at), Path(args.output_dir))
        else:
            execute_verified_plan(Path(args.strategy), Path(args.output_dir))
        print(json.dumps({'phase': args.command, 'reason_code': 'ok', 'human_review_state': 'pending'}))
        return 0
    except (Exception, KeyboardInterrupt):
        print(json.dumps({'phase': args.command, 'reason_code': 'w3_failed'}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
