"""Approved W3 offline runner; never reads production receipts or CSV."""
import argparse
from collections import Counter
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from copy import deepcopy
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import time
import multiprocessing as mp
import socket
from unittest.mock import patch
from datainsight import analysis as a, feasibility as f, planning as p, planning_methods as m
from test_w2a import fixture, put

CASES = []
REFERENCES = []


def terminal(directory, command):
    for name in f.REQUIRED[2:]:
        f.save(directory / name, {'synthetic': True})
    f.publish(directory, {'schema_version': '1.0', 'run_id': directory.name, 'command': command,
        'status': 'success', 'exit_status': 0, 'completed_at': f.now(), 'required_evidence_refs': list(f.REQUIRED)})


def setup_chain(root, source, output):
    stack = ExitStack()
    stack.enter_context(patch.object(f, 'FIXTURE', root))
    stack.enter_context(patch.object(f, 'OUTPUT', root / 'upstream'))
    stack.enter_context(patch.object(p, 'OUTPUT', root / 'upstream'))
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    real_hash = hashlib.sha256
    def fixture_hash(data=b''):
        return real_hash(source.read_bytes() if data == b'controlled-w2a-aggregate-oracle-v1' else data)
    with patch('hashlib.sha256', side_effect=fixture_hash):
        package = fixture(root)
    snapshot = f.load_accepted_profile(package / 'profile.json', package / 'fixture-acceptance.json')
    question = f.parse(a.read(a.QUESTION))
    snapshot['input_manifest']['files'].append({'path': f.relative(a.QUESTION), 'sha256': f.digest(a.read(a.QUESTION))})
    diagnosis_dir = f.new_run(f.OUTPUT / 'diagnosis')
    diagnosis = f.diagnose(question, snapshot, f.rules_module.registered_rules())
    diagnosis.update(run_id=diagnosis_dir.name, question_ref=f.relative(a.QUESTION), question_hash=f.digest(a.read(a.QUESTION)))
    f.save(diagnosis_dir / 'diagnosis.json', diagnosis)
    f.save(diagnosis_dir / 'input-manifest.json', snapshot['input_manifest'])
    f.save(diagnosis_dir / 'reference-check.json', {'schema_version': '1.0', 'references_resolvable': True,
        **{k: snapshot[k] for k in ('profile_identity', 'acceptance_basis', 'source_kind')}})
    terminal(diagnosis_dir, 'diagnose')
    receipt_dir = f.OUTPUT / 's2'
    f.record_s2_decision(diagnosis, {'decision': 'accept', 'actor': 'synthetic_actor', 'confirmed_at': f.now()}, receipt_dir)
    terminal(receipt_dir, 'decide')
    acceptance = root / 'synthetic-acceptance.json'
    put(acceptance, '总判定：通过; synthetic only\n'.encode())
    stack.enter_context(patch.object(p, 'S2', receipt_dir / 'decision.json'))
    stack.enter_context(patch.object(p, 'DIAGNOSIS', diagnosis_dir / 'diagnosis.json'))
    stack.enter_context(patch.object(p, 'ACCEPTANCE', acceptance))
    context = p.load_s2_accept(p.S2)
    candidates = p.OUTPUT / 'candidates'
    candidates.mkdir()
    plans = p.build_candidate_plans(context, m.registered_methods())
    plans['run_id'] = candidates.name
    p.save(candidates / 'candidate-plans.json', plans)
    p.save(candidates / 'accepted-context.json', context)
    manifest = p.planning_manifest(context)
    p.save(candidates / 'input-manifest.json', manifest)
    p.save(candidates / 'reference-check.json', {'schema_version': '1.0', 'references_resolvable': True,
        'context_hash': f.digest(f.encoded(context)), 'manifest_hash': f.digest(f.encoded(manifest))})
    terminal(candidates, 'candidates')
    review_dir = p.OUTPUT / 'review'
    review = {'decision': 'approve', 'selected_plan_id': 'P-BEHAVIOUR-RECORDS', 'selected_plan_version': 'v1',
        'metric_definition_hash': f.digest(f.encoded(m.definition())), 'confirm_metric_definition': True,
        'actor': 'synthetic_actor', 'confirmed_at': f.now()}
    p.record_s3_review(candidates / 'candidate-plans.json', review, review_dir)
    terminal(review_dir, 'review')
    stack.enter_context(patch.object(a, 'S3', review_dir / 's3-review.json'))
    stack.enter_context(patch.object(a, 'SOURCE', source))
    stack.enter_context(patch.object(a, 'OUTPUT', output))
    return stack


def fixture_worker(send, strategy_ref, bindings_hash, strategy_hash, seconds):
    """Test-only fixed spawn target; no production CLI or environment backdoor."""
    strategy_path = Path(strategy_ref)
    bindings = f.parse(a.read(strategy_path.parent / 'bindings.json'))
    review = a.ROOT / bindings['s3_ref']
    upstream = review.parent.parent
    source = Path(bindings['source_path'])
    f.path_check(source, a.ROOT / 'tests/fixtures/w3')
    f.path_check(review, a.ROOT / 'outputs/_scratch')
    with ExitStack() as stack:
        for obj, key, value in ((f, 'FIXTURE', upstream.parent), (f, 'OUTPUT', upstream),
                (p, 'OUTPUT', upstream), (p, 'S2', upstream / 's2/decision.json'),
                (p, 'DIAGNOSIS', upstream / 'diagnosis/diagnosis.json'),
                (p, 'ACCEPTANCE', upstream.parent / 'synthetic-acceptance.json'),
                (a, 'S3', review), (a, 'SOURCE', source), (a, 'OUTPUT', strategy_path.parent.parent)):
            stack.enter_context(patch.object(obj, key, value))
        a._worker(send, strategy_ref, bindings_hash, strategy_hash, seconds)


def blocked_worker(*args):
    time.sleep(30)


def process_factory(blocked=False):
    original = mp.get_context('spawn').Process
    def create(*args, **kwargs):
        kwargs['target'] = blocked_worker if blocked else fixture_worker
        return original(*args, **kwargs)
    return create


def run_case(name, expected, fn):
    a.QUERY_COUNT = 0
    try:
        fn()
        actual = 'ok'
    except (f.BoundaryError, a.profile.BoundaryError) as exc:
        actual = str(exc)
    except BaseException:
        actual = 'unexpected_exception'
    passed = actual == expected
    CASES.append({'case_id': name, 'actual': actual, 'expected': expected,
        'reason_code': actual, 'query_count': a.QUERY_COUNT, 'pass': passed,
        'scope': 'synthetic offline; no real authorization'})
    return passed


def run(batch):
    if batch not in ('w3-e3o-r2-a', 'w3-e3o-r2-b'):
        raise ValueError('unapproved_batch')
    import duckdb
    if sys.version_info[:3] != (3, 12, 9) or duckdb.__version__ != '1.4.1':
        print('{"reason_code":"dependency_version_mismatch"}')
        return 1
    out = a.ROOT / 'outputs/W3' / ('offline-' + batch)
    root = a.ROOT / 'outputs/_scratch' / batch
    fixtures = a.ROOT / 'tests/fixtures/w3' / batch
    document = a.ROOT / 'docs/acceptance/results' / (batch + '.md')
    for target in (out, root, fixtures, document):
        f.path_check(target, a.ROOT)
        if target.exists():
            raise ValueError('output_exists')
    for target in (out, root, fixtures):
        target.mkdir(parents=True)
    source = fixtures / 'behaviours.csv'
    with source.open('x', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        for behaviour in ('pv', 'pv', 'fav', 'cart', 'buy', '', 'PV', ' pv ', 'other'):
            writer.writerow(('synthetic_user', 'synthetic_goods', '', behaviour, ''))
    counts = Counter()
    with source.open(newline='', encoding='utf-8') as stream:
        for row in csv.reader(stream, strict=True):
            value = row[3]
            counts[value if value in a.BUCKETS[:4] else 'missing' if value == '' else 'other'] += 1
    reference = {b: counts[b] for b in a.BUCKETS}
    REFERENCES.append({'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'tool': 'stdlib csv.reader / Counter', 'buckets': reference, 'row_count': sum(counts.values())})
    log = io.StringIO()
    halted = None
    try:
        with redirect_stdout(log), redirect_stderr(log), setup_chain(root, source, out):
            context = a.load_w3_context(a.S3)
            strategy_dir = out / 'strategy-normal'
            strategy = a.record_preservation_decision(context, a.StrategySpec('preserve_all', 'synthetic_actor', 'not_provided'), strategy_dir)
            run_case('D301_actual_synthetic_verifiers', 'ok', lambda: a.load_w3_context(a.S3))
            run_case('D302_receipt_consumer', 'ok', lambda: a.load_strategy(strategy_dir / 'strategy.json'))
            run_case('D302_missing_decision', 'invalid_preservation_decision', lambda: a.record_preservation_decision(context, None, out / 'missing'))
            for decision in ('reject', 'cancel'):
                directory = out / ('strategy-' + decision)
                a.record_preservation_decision(context, a.StrategySpec(decision, 'synthetic_actor', 'not_provided'), directory)
                run_case('D302_' + decision, 'preservation_not_approved', lambda d=directory: a.load_strategy(d / 'strategy.json'))
            run_case('D303_wrong_source', 'source_not_allowed', lambda: a.source_check(fixtures / 'unapproved.csv'))
            computation = a.calculate(context.bindings, strategy.value, str(source))
            run_case('D304_reference', 'ok', lambda: equal(computation['result'], {'buckets': reference, 'row_count': sum(counts.values())}))
            directory = out / 'analysis-direct'
            directory.mkdir()
            a.save(directory / 'result.json', computation['result'])
            fp = a.fingerprint(source, time.monotonic() + 180)
            value = {**computation, 'before': fp, 'after': fp, 'worker': {'exitcode': 0, 'reaped': True},
                'bindings_hash': f.digest(a.payload(context.bindings)), 'strategy_hash': f.digest(a.payload(strategy.value)),
                'read_contract_hash': context.bindings['read_contract_hash'], 'result_hash': f.digest(a.payload(computation['result'])),
                'output_dir': str(directory), 'claims': a.claims_for(None).values}
            baseline = a.CalculationEvidence(value)
            validation = a.validate_s5(context, strategy, baseline)
            run_case('D306_D307_D308_valid', 'ok', lambda: equal([v['state'] for v in validation.value.values()], ['pass'] * 3))
            for layer, field, changed in (('execution', 'status', 'failed'), ('metric', 'parameters', ['unapproved']),
                                           ('boundary', 'claims', [{'text': 'payment conversion'}])):
                altered = deepcopy(value)
                altered[field] = changed
                run_case('S5_' + layer + '_independent', 'ok', lambda v=altered, l=layer:
                    equal(a.validate_s5(context, strategy, a.CalculationEvidence(v)).value[l]['state'], 'fail'))
            value['validation'] = validation.value
            a.save(directory / 'validation.json', validation.value)
            report = a.render_report(a.claims_for(None), baseline)
            a.save(directory / 'report.md', report)
            run_case('D309_deterministic_render', 'ok', lambda: equal(a.read(directory / 'report.md'), report))
            run_case('D308_arbitrary_text', 'unsupported_claim', lambda: a.render_report(a.ValidatedClaims([{'text': 'orders'}]), baseline))
            run_case('D305_document_limit', 'document_byte_boundary', lambda: a.payload({'text': 'x' * a.LIMIT}))
            run_case('D310_existing_directory', 'output_exists', lambda: a.new_run(directory))
            before = a.read(directory / 'report.md')
            run_case('D310_exclusive_file', 'ok', lambda: exclusive_check(directory / 'report.md', before))
            run_case('D305_expired_deadline', 'execution_deadline', lambda: a.remaining(time.monotonic() - 1))
            bad_receipt = dict(strategy.value, decision='cancel')
            run_case('D311_worker_strategy', 'worker_strategy_invalid', lambda: a.calculate(context.bindings, bad_receipt, str(source)))
            bad_bindings = deepcopy(context.bindings)
            bad_bindings['source_path'] = 'https://not-allowed'
            bad_receipt = dict(strategy.value, bindings_hash=f.digest(a.payload(bad_bindings)))
            run_case('D311_worker_source', 'worker_source_invalid', lambda: a.calculate(bad_bindings, bad_receipt, str(source)))
            extended_cases(context, strategy, strategy_dir, baseline, out, source)
            r2_cases(context, strategy, strategy_dir, baseline, out, source)
    except (f.BoundaryError, a.profile.BoundaryError) as exc:
        reason = str(exc)
        halted = reason if reason.replace('_', '').isalnum() and len(reason) < 128 else 'offline_execution_failed'
    except BaseException:
        halted = 'offline_setup_or_execution_failed'
    evidence = {'schema_version': '1.0', 'synthetic': True, 'cases': CASES, 'halted_reason': halted}
    put(out / 'test.log', log.getvalue().encode())
    put(out / 'case-results.json', evidence)
    put(out / 'reference-results.json', REFERENCES)
    result = {'status': 'incomplete', 'exit_status': 1, 'synthetic': True,
        'passed_cases': sum(c['pass'] for c in CASES), 'total_cases': len(CASES),
        'halted_reason': halted, 'technical_acceptance': 'pending',
        'unmet': ['D301 dataset mutation and accurate per-case baseline/reason matrix',
                  'D302 missing terminal and all strategy identity mutations',
                  'D303 link path controlled rejection', 'D305 configuration fault and exact byte boundaries',
                  'D310 required-artifact open/write/flush/fsync matrix (only save failure covered)',
                  'D311 provider-specific direct assertions', 'D312 real proof not authorized'],
        'observed_worker': deepcopy(a.WORKER_OBSERVATION),
        'implemented_test_scope': 'actual fixture worker; R2 independent mutations, strict parse, result/report mismatch, required artifact and double-finalization faults',
        'case_reason_details': CASES_DETAIL}
    put(out / 'batch-result.json', result)
    put(out / 'operation.json', {**a.operation('offline', 'completed_partial'),
        'authorization': 'P-W3-E3-OFFLINE-R2', 'batch_id': batch, 'actual_exit_status': 1})
    text = '# W3 offline execution — ' + batch + '\n\n未验收，待规划／验收方判定。\n\n'
    text += '状态：不完整，退出码1；不得进入真实G3.5／E3。\n\n'
    text += '证据：`outputs/W3/offline-' + batch + '/`。实际命令：`.venv/Scripts/python.exe -B -m test_w3 --w3-evidence --batch-id ' + batch + '`。\n\n'
    text += 'Python3.12.9／DuckDB1.4.1已工具核验。cwd与PYTHONPATH／TEMP／TMP／TMPDIR遵循P-W3-E3-OFFLINE-R2。\n\n'
    text += '|标准|实测状态|\n|---|---|\n'
    descriptions = {'D301': '部分：实际合成核验链；缺完整变化矩阵', 'D302': '部分：明确决定／reject／cancel；缺完整绑定矩阵',
        'D303': '部分：合成源hash／固定路径；缺坏解析矩阵', 'D304': '部分：真实DuckDB与独立csv／Counter一致性测试',
        'D305': '部分：实际spawn成功、阻塞超时终止回收、配置与文档边界；缺结果大小及配置故障矩阵', 'D306': '部分：三层基线与执行层独立拒绝',
        'D307': '部分：参数变化；缺完整口径矩阵', 'D308': '部分：任意text及无依据claim拒绝',
        'D309': '部分：实际完整execute与终态消费、缺校验及报告篡改拒绝；缺完整引用变化矩阵', 'D310': '部分：独占输出及终态open/write/flush/fsync/rename故障；缺必要文件及双收尾故障',
        'D311': '部分：worker策略／来源拒绝；缺泄露／调用直接断言', 'D312': '未测：真实门未授权'}
    for key in descriptions:
        matching = [c for c in CASES if key in c['case_id']]
        text += '| ' + key + ' | ' + ('真实部分未授权、未运行' if key == 'D312' else
            '部分实测；请按case-results核对本ID直接用例，跨层用例另列；不表示完整覆盖') + ' |\n'
    text += '\n实际未闭合项：\n' + '\n'.join('- ' + item for item in result['unmet']) + '\n'
    text += '\n详见case-results.json实际expected／actual；结果不由runner返回值单独认证。\n'
    put(document, text.encode())
    index = a.ROOT / 'docs/acceptance/results/INDEX.md'
    with index.open('a', encoding='utf-8') as stream:
        stream.write('\n## W3离线执行 ' + batch + '\n\n[' + batch + '](' + batch + '.md)：不完整；未验收，待规划／验收方判定。真实门未启动。\n')
    print(json.dumps(result))
    return 1


def extended_cases(context, strategy, strategy_dir, baseline, out, source):
    spawn = mp.get_context('spawn')
    factory = process_factory()
    with patch.object(spawn, 'Process', side_effect=factory):
        run_case('D305_actual_spawn_success', 'ok', lambda: equal(
            a.supervised(context, strategy, time.monotonic() + 180)['result'], baseline.value['result']))
        target = out / 'analysis-complete'
        run_case('D309_complete_execution', 'ok', lambda: a.execute_verified_plan(strategy_dir / 'strategy.json', target))
        run_case('D309_consumed_success', 'ok', lambda: a.terminal(target, 'execute'))
    with patch.object(spawn, 'Process', side_effect=process_factory(True)):
        run_case('D305_actual_timeout', 'worker_timeout_reaped', lambda:
            a.supervised(context, strategy, time.monotonic() + 0.3))
        run_case('D305_actual_reaped_observation', 'ok', lambda: equal(
            [a.WORKER_OBSERVATION['terminated'], a.WORKER_OBSERVATION['reaped']], [True, True]))
    for field in ('global_filter', 'duplicate_policy', 'null_policy', 'text_policy', 'window', 'denominator', 'grain'):
        changed = deepcopy(context.bindings)
        changed['plan']['metric_definition'][field] = 'unsupported_change'
        result = a.validate_s5(a.ExecutionContext(changed), strategy, baseline)
        run_case('D307_' + field, 'ok', lambda r=result: equal(r.value['metric']['state'], 'fail'))
    for field, changed in (('engine_configuration', {}), ('python_version', 'wrong'), ('result_hash', '0' * 64),
                            ('worker', {'exitcode': 1, 'reaped': True}), ('status', 'pending')):
        evidence = deepcopy(baseline.value)
        evidence[field] = changed
        result = a.validate_s5(context, strategy, a.CalculationEvidence(evidence))
        run_case('D306_' + field, 'ok', lambda r=result: equal(r.value['execution']['state'], 'fail'))
    for field in ('before', 'result', 'worker', 'sql', 'claims'):
        evidence = deepcopy(baseline.value)
        evidence.pop(field)
        result = a.validate_s5(context, strategy, a.CalculationEvidence(evidence))
        layer = 'metric' if field == 'sql' else 'boundary' if field == 'claims' else 'execution'
        run_case('S5_missing_' + field, 'ok', lambda r=result, l=layer: equal(r.value[l]['state'], 'fail'))
    for text in ('orders', 'payments', 'conversion', 'date', 'effect', 'ratio'):
        claims = a.ValidatedClaims([{'claim_type': text, 'value': 42}])
        run_case('D308_' + text, 'unsupported_claim', lambda c=claims: a.render_report(c, baseline))
    evidence = deepcopy(baseline.value)
    evidence.pop('validation')
    run_case('D309_no_validation', 'report_validation_required', lambda: a.render_report(a.claims_for(None), a.CalculationEvidence(evidence)))
    report_dir = out / 'analysis-complete'
    raw = a.read(report_dir / 'report.md')
    with patch.object(a, 'read', side_effect=lambda path: raw + b'changed' if Path(path) == report_dir / 'report.md' else ORIGINAL_READ(path)):
        run_case('D309_changed_report', 'artifact_hash_changed', lambda: a.terminal(report_dir, 'execute'))
    for action in ('open', 'write', 'flush', 'fsync', 'rename'):
        fault_case(out, action)
    with patch.object(socket, 'create_connection', side_effect=AssertionError('network_requested')) as network:
        run_case('D311_no_network_claims', 'ok', lambda: a.check_claims(a.claims_for(None)))
        equal(network.call_count, 0)
    captured = io.StringIO()
    with patch.object(a, 'load_w3_context', side_effect=RuntimeError('RAW_SECRET_ROW')), redirect_stderr(captured):
        equal(a.main(['strategy', '--decision', 'preserve_all', '--actor', 'synthetic_actor',
            '--confirmed-at', 'not_provided', '--output-dir', str(out / 'no-output')]), 1)
    run_case('D311_safe_error', 'ok', lambda: equal('RAW_SECRET_ROW' in captured.getvalue(), False))


ORIGINAL_READ = a.read


def fault_case(out, action):
    directory = out / ('fault-' + action)
    directory.mkdir()
    value = {'status': 'success'}
    calls = []
    original_open = Path.open
    original_rename = Path.rename
    original_fsync = os.fsync
    class Stream:
        def __init__(self, stream):
            self.stream = stream
        def __enter__(self):
            self.stream.__enter__()
            return self
        def __exit__(self, *args):
            return self.stream.__exit__(*args)
        def write(self, data):
            if action == 'write':
                calls.append(action)
                raise OSError('controlled')
            return self.stream.write(data)
        def flush(self):
            if action == 'flush':
                calls.append(action)
                raise OSError('controlled')
            return self.stream.flush()
        def fileno(self):
            return self.stream.fileno()
    def opening(path, *args, **kwargs):
        if path.parent == directory and action == 'open':
            calls.append(action)
            raise OSError('controlled')
        stream = original_open(path, *args, **kwargs)
        return Stream(stream) if path.parent == directory else stream
    def syncing(fd):
        if action == 'fsync':
            calls.append(action)
            raise OSError('controlled')
        return original_fsync(fd)
    def renaming(path, target):
        if path.parent == directory and action == 'rename':
            calls.append(action)
            raise OSError('controlled')
        return original_rename(path, target)
    with patch.object(Path, 'open', opening), patch.object(Path, 'rename', renaming), patch.object(os, 'fsync', syncing):
        try:
            a.publish(directory, value)
        except OSError:
            pass
    run_case('D310_fault_' + action, 'ok', lambda: equal(
        [bool(calls), (directory / 'final-status.json').exists()], [True, False]))


def r2_cases(context, strategy, strategy_dir, baseline, out, source):
    def layer_case(name, layer, change):
        def check():
            equal(a.validate_s5(context, strategy, baseline).value[layer]['state'], 'pass')
            value = deepcopy(baseline.value)
            change(value)
            result = a.validate_s5(context, strategy, a.CalculationEvidence(value))
            equal(result.value[layer]['state'], 'fail')
            CASES_DETAIL[name] = result.value[layer]['reason_code']
        run_case(name, 'ok', check)
    for name, change in (
            ('extra_field', lambda v: v['result']['buckets'].update(extra=1)),
            ('negative', lambda v: v['result']['buckets'].update(pv=-1)),
            ('float', lambda v: v['result']['buckets'].update(pv=1.5)),
            ('bool', lambda v: v['result']['buckets'].update(pv=True)),
            ('coverage', lambda v: v['result'].update(row_count=0)),
            ('source_after', lambda v: v['after'].update(sha256='0' * 64)),
            ('source_before', lambda v: v['before'].update(sha256='0' * 64))):
        layer_case('D304_D306_' + name, 'execution', change)
    for name, change in (
            ('sql', lambda v: v['sql'].update(behaviours='SELECT 1')),
            ('template_hash', lambda v: v['sql_hashes'].update(behaviours='0' * 64)),
            ('contract', lambda v: v.update(read_contract_hash='0' * 64))):
        layer_case('D307_' + name, 'metric', change)
    for name, claim in (('value', {'claim_type': a.CLAIM, 'bucket': 'pv', 'value': 1}),
                         ('reference', {'claim_type': a.CLAIM, 'bucket': 'pv', 'value_ref': 'other', 'evidence_ref': 'other'})):
        layer_case('D308_' + name, 'boundary', lambda v, c=claim: v.update(claims=[c]))
    changed = deepcopy(baseline.value)
    changed['result']['buckets']['pv'] += 1
    run_case('D309_memory_disk_mismatch', 'report_result_changed', lambda:
        a.render_report(a.claims_for(None), a.CalculationEvidence(changed)))
    # Actual upstream consumer under one controlled read mutation; published fixtures stay unchanged.
    targets = [(p.S2, 's2_bytes'), (p.DIAGNOSIS, 'diagnosis_bytes'),
               (a.S3, 'review_bytes'), (a.ROOT / context.bindings['question_identity']['ref'], 'question_bytes'),
               (a.ROOT / 'src/datainsight/feasibility_rules.py', 'rules_bytes'),
               (a.ROOT / 'src/datainsight/planning_methods.py', 'registry_bytes')]
    for target, name in targets:
        def check(t=target):
            a.load_w3_context(a.S3)
            original = f.read_bytes
            def changed_read(path, *args, **kwargs):
                data = original(path, *args, **kwargs)
                if Path(path) == t:
                    if t == a.S3:
                        value = f.parse(data)
                        value['actor'] = ''
                        return f.encoded(value)
                    return data + b' '
                return data
            with patch.object(f, 'read_bytes', side_effect=changed_read):
                try:
                    a.load_w3_context(a.S3)
                except (f.BoundaryError, a.profile.BoundaryError):
                    equal(a.QUERY_COUNT, 0)
                    return
            f.fail('mutation_not_rejected')
        run_case('D301_' + name, 'ok', check)
    for name in ('final-status.json', 's3-review.json'):
        target = a.S3.parent / name
        def missing(t=target):
            a.load_w3_context(a.S3)
            original = f.read_bytes
            def blocked(path, *args, **kwargs):
                if Path(path) == t:
                    f.fail('controlled_missing_file')
                return original(path, *args, **kwargs)
            with patch.object(f, 'read_bytes', side_effect=blocked):
                try:
                    a.load_w3_context(a.S3)
                except f.BoundaryError:
                    equal(a.QUERY_COUNT, 0)
                    return
            f.fail('missing_not_rejected')
        run_case('D301_missing_' + name, 'ok', missing)
    for decision in ('reject', 'cancel'):
        def stopped(d=decision):
            a.load_w3_context(a.S3)
            original = p.verify_review
            with patch.object(p, 'verify_review', side_effect=lambda path: dict(original(path), decision=d)):
                a.load_w3_context(a.S3)
        run_case('D301_stop_' + decision, 's3_not_approved', stopped)
    for field, change in (('method', 'UNKNOWN'), ('metric', {'grain': 'changed'})):
        def invalid(field=field, change=change):
            a.load_w3_context(a.S3)
            original = p.load_plan_set
            def plans(path):
                values = list(original(path))
                values[0] = deepcopy(values[0])
                chosen = values[0]['candidates'][0]
                if field == 'method':
                    chosen['method_id'] = change
                else:
                    chosen['metric_definition'] = change
                return tuple(values)
            with patch.object(p, 'load_plan_set', side_effect=plans):
                a.load_w3_context(a.S3)
        run_case('D301_' + field, 'unique_method_required' if field == 'method' else 'metric_definition_changed', invalid)
    def stale():
        a.load_strategy(strategy_dir / 'strategy.json')
        original = a.load_w3_context
        def altered(path):
            value = deepcopy(original(path).bindings)
            value['dataset_version'] = '0' * 64
            return a.ExecutionContext(value)
        with patch.object(a, 'load_w3_context', side_effect=altered):
            a.load_strategy(strategy_dir / 'strategy.json')
    run_case('D302_stale_binding', 'strategy_binding_changed', stale)
    run_case('D302_unknown_strategy', 'invalid_preservation_decision', lambda:
        a.record_preservation_decision(context, a.StrategySpec('deduplicate', 'synthetic_actor', 'not_provided'), out / 'not-created'))
    for label, data in (('columns', b'a,b,c,pv\n'), ('encoding', b'a,b,c,\xff,0\n'), ('quote', b'a,b,c,"pv,0\n')):
        bad = source.parent / ('bad-' + label + '.csv')
        put(bad, data)
        def parse_bad(path=bad):
            equal(a.calculate(context.bindings, strategy.value, str(source))['result'], baseline.value['result'])
            bindings = deepcopy(context.bindings)
            bindings['source_path'] = str(path)
            receipt = dict(strategy.value, bindings_hash=f.digest(a.payload(bindings)))
            with patch.object(a, 'SOURCE', path):
                try:
                    a.calculate(bindings, receipt, str(path))
                except a.profile.duckdb.Error:
                    return
            f.fail('strict_parse_not_rejected')
        run_case('D303_bad_' + label, 'ok', parse_bad)
    run_case('D303_uri', 'invalid_path', lambda: f.path_check(Path('https://invalid'), a.ROOT))
    with patch.object(a, 'RESULT_LIMIT', 1):
        run_case('D305_result_boundary_controlled', 'result_byte_boundary', lambda:
            a.calculate(context.bindings, strategy.value, str(source)))
    # Actual source identity mismatch is injected at the hash result, never by altering a published fixture.
    original_fingerprint = a.fingerprint
    with patch.object(a, 'fingerprint', side_effect=lambda path, end: dict(original_fingerprint(path, end), sha256='0' * 64)):
        run_case('D303_source_version_stop', 'source_version_changed', lambda:
            a.execute_verified_plan(strategy_dir / 'strategy.json', out / 'source-changed'))
    for filename in ('bindings.json', 'result.json', 'calculation-evidence.json', 'validation.json', 'report.md', 'operation.json'):
        required_fault(out, strategy_dir, filename)
    required_fault(out, strategy_dir, 'result.json', double=True)
    # Exercise full in-process execution with network and credential-read tripwires.
    original_open = Path.open
    def guarded_open(path, *args, **kwargs):
        if path.name == '.env' or 'credential' in path.name.lower() or 'secret' in path.name.lower():
            raise AssertionError('credential_requested')
        return original_open(path, *args, **kwargs)
    with patch.object(socket, 'create_connection', side_effect=AssertionError('network')) as network, \
            patch.object(Path, 'open', guarded_open), patch.object(a, 'supervised', side_effect=lambda c, s, e:
                dict(a.calculate(c.bindings, s.value, str(source)), worker={'exitcode': 0, 'reaped': True})):
        run_case('D311_full_local_path', 'ok', lambda: a.execute_verified_plan(strategy_dir / 'strategy.json', out / 'no-network-run'))
        equal(network.call_count, 0)


CASES_DETAIL = {}


def required_fault(out, strategy_dir, filename, double=False):
    directory = out / ('required-' + filename.replace('.', '-') + ('-double' if double else ''))
    original = a.save
    calls = []
    def broken(path, value):
        if path.parent == directory and (path.name == filename or (double and path.name.startswith('final-status'))):
            calls.append(path.name)
            raise OSError('SENSITIVE_CONTROLLED_FAILURE')
        return original(path, value)
    capture = io.StringIO()
    def test():
        with patch.object(a, 'save', side_effect=broken), \
                patch.object(a, 'supervised', side_effect=lambda c, s, e:
                    dict(a.calculate(c.bindings, s.value, str(a.SOURCE)), worker={'exitcode': 0, 'reaped': True})), \
                redirect_stderr(capture):
            code = a.main(['execute', '--strategy', str(strategy_dir / 'strategy.json'), '--output-dir', str(directory)])
        equal(code, 1)
        equal(bool(calls), True)
        equal('SENSITIVE_CONTROLLED_FAILURE' in capture.getvalue(), False)
        final = directory / 'final-status.json'
        if final.exists():
            equal(f.parse(a.read(final))['status'], 'failed')
        elif double:
            equal('"failure_evidence_persisted": false' in capture.getvalue(), True)
        else:
            f.fail('failure_terminal_missing')
    run_case('D310_required_' + filename + ('_double' if double else ''), 'ok', test)


def equal(actual, expected):
    if actual != expected:
        f.fail('assertion_mismatch')


def exclusive_check(path, original):
    try:
        a.save(path, b'not permitted')
    except FileExistsError:
        equal(a.read(path), original)
        return
    f.fail('exclusive_write_failed')


def run_r3(batch):
    """One approved incremental batch; old evidence and old suite remain untouched."""
    import duckdb
    if batch != 'w3-e3o-r3-a':
        raise ValueError('unapproved_batch')
    if sys.version_info[:3] != (3, 12, 9) or duckdb.__version__ != '1.4.1':
        print('{"reason_code":"dependency_version_mismatch"}')
        return 1
    out = a.ROOT / 'outputs/W3' / ('offline-' + batch)
    root = a.ROOT / 'outputs/_scratch' / batch
    fixtures = a.ROOT / 'tests/fixtures/w3' / batch
    document = a.ROOT / 'docs/acceptance/results' / (batch + '.md')
    for path in (out, root, fixtures, document):
        f.path_check(path, a.ROOT)
        if path.exists():
            raise ValueError('output_exists')
    for path in (out, root, fixtures):
        path.mkdir(parents=True)
    started = f.now()
    started_clock = time.perf_counter()
    records = []
    references = []
    log = io.StringIO()
    halted = None
    source = fixtures / 'behaviours.csv'
    with source.open('x', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        for behaviour in ('pv', 'pv', 'fav', 'cart', 'buy', '', 'PV', ' pv ', 'other'):
            writer.writerow(('synthetic_user', 'synthetic_goods', '', behaviour, ''))
    counter = Counter()
    with source.open(newline='', encoding='utf-8') as stream:
        for row in csv.reader(stream, strict=True):
            value = row[3]
            counter[value if value in a.BUCKETS[:4] else 'missing' if not value else 'other'] += 1
    reference = {'buckets': {b: counter[b] for b in a.BUCKETS}, 'row_count': sum(counter.values())}
    references.append({'tool': 'stdlib csv.reader/Counter', 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                       'result': reference})
    def case(name, fn):
        a.QUERY_COUNT = 0
        detail = {'case_id': name, 'baseline_ref': 'analysis-normal', 'synthetic': True}
        try:
            detail.update(fn() or {})
            detail.update(status='passed', assertion_result='passed')
        except BaseException as error:
            detail.update(status='failed', assertion_result='failed', reason_code=a.safe_reason(error))
        detail['query_count'] = a.QUERY_COUNT
        records.append(detail)
        if detail['status'] != 'passed':
            raise RuntimeError('r3_case_failed')
    try:
        with redirect_stdout(log), redirect_stderr(log), setup_chain(root, source, out):
            context = a.load_w3_context(a.S3)
            strategy_dir = out / 'strategy-normal'
            strategy = a.record_preservation_decision(context,
                a.StrategySpec('preserve_all', 'synthetic_actor', 'not_provided'), strategy_dir)
            a.load_strategy(strategy_dir / 'strategy.json')
            spawn = mp.get_context('spawn')
            normal_dir = out / 'analysis-normal'
            factory = process_factory()
            def normal():
                with patch.object(spawn, 'Process', side_effect=factory):
                    result = a.execute_verified_plan(strategy_dir / 'strategy.json', normal_dir)
                a.terminal(normal_dir, 'execute')
                actual = f.parse(a.read(normal_dir / 'result.json'))
                equal(actual, reference)
                validation = f.parse(a.read(normal_dir / 'validation.json'))
                equal([v['state'] for v in validation.values()], ['pass'] * 3)
                evidence = f.parse(a.read(normal_dir / 'calculation-evidence.json'))
                equal(a.read(normal_dir / 'report.md'), a.render_report(a.claims_for(None), a.CalculationEvidence(evidence)))
                equal(result.value['human_review_state'], 'pending')
                equal(evidence['worker']['reaped'], True)
                return {'actual': 'success', 'expected': 'success', 'reason_code': 'ok',
                        'terminal': 'success', 'actual_worker': evidence['worker'],
                        'observed_configuration': evidence['engine_configuration']}
            case('baseline_actual_worker_S5_report_terminal', normal)
            computation = a.calculate(context.bindings, strategy.value, str(source))
            def local_worker(c, s, end):
                return dict(deepcopy(computation), worker={'exitcode': 0, 'reaped': True})
            def missing_terminal():
                directory = out / 'strategy-missing-terminal'
                directory.mkdir()
                # Independent new package: same valid identity for its new run, no terminal.
                receipt = dict(strategy.value, run_id=directory.name)
                a.save(directory / 'strategy.json', receipt)
                a.save(directory / 'bindings.json', context.bindings)
                a.save(directory / 'operation.json', a.operation('strategy', 'synthetic_partial'))
                with patch.object(a, 'source_check', side_effect=AssertionError('source_called')) as checked, \
                        patch.object(a, 'fingerprint', side_effect=AssertionError('fingerprint_called')) as hashed, \
                        patch.object(a, 'calculate', side_effect=AssertionError('calculate_called')) as calculated, \
                        patch.object(a, 'supervised', side_effect=AssertionError('worker_called')) as worker, \
                        patch.object(a, 'success', side_effect=AssertionError('success_called')) as published:
                    try:
                        a.execute_verified_plan(directory / 'strategy.json', out / 'missing-terminal-target')
                    except f.BoundaryError as error:
                        equal(str(error), 'evidence_missing_or_size')
                    else:
                        f.fail('missing_terminal_accepted')
                    equal([checked.call_count, hashed.call_count, calculated.call_count, worker.call_count, published.call_count], [0] * 5)
                equal((out / 'missing-terminal-target').exists(), False)
                return {'actual': 'evidence_missing_or_size', 'expected': 'evidence_missing_or_size',
                        'reason_code': 'evidence_missing_or_size', 'phase': 'strategy_terminal',
                        'direct_calls': {'source_check': 0, 'fingerprint': 0, 'calculate': 0, 'worker': 0, 'success': 0}}
            case('M1_missing_strategy_terminal', missing_terminal)
            def config_mismatch():
                original_connect = duckdb.connect
                observed = {'queries': [], 'closed': False}
                class Cursor:
                    def __init__(self, cursor):
                        self.cursor = cursor
                    def fetchall(self):
                        rows = self.cursor.fetchall()
                        return [(key, '2' if key == 'threads' else value) for key, value in rows]
                class Connection:
                    def __init__(self, connection):
                        self.connection = connection
                    def execute(self, sql, *args):
                        observed['queries'].append(sql)
                        cursor = self.connection.execute(sql, *args)
                        return Cursor(cursor) if 'duckdb_settings()' in sql else cursor
                    def close(self):
                        self.connection.close()
                        observed['closed'] = True
                with patch.object(duckdb, 'connect', side_effect=lambda *args, **kwargs: Connection(original_connect(*args, **kwargs))):
                    try:
                        a.calculate(context.bindings, strategy.value, str(source))
                    except f.BoundaryError as error:
                        equal(str(error), 'resource_configuration_mismatch')
                    else:
                        f.fail('configuration_accepted')
                equal(len(observed['queries']), 1)
                equal('duckdb_settings()' in observed['queries'][0], True)
                equal(observed['closed'], True)
                return {'actual': 'resource_configuration_mismatch', 'expected': 'resource_configuration_mismatch',
                        'reason_code': 'resource_configuration_mismatch', 'changed_field': 'threads',
                        'configuration_select_count': 1, 'business_query_count': 0, 'connection_closed': True}
            case('M2_configuration_mismatch', config_mismatch)
            def deadline_test(label, phase):
                directory = out / label
                clock = [1000.0]
                original_check = a.check_context
                original_save = a.save
                original_publish = a.publish
                observations = {'success_publish_calls': 0, 'failed_publish_calls': 0, 'expired_in': None}
                def checking(c):
                    original_check(c)
                    if phase == 'post_hash_check':
                        clock[0] = 1181.0
                        observations['expired_in'] = phase
                def saving(path, value):
                    result = original_save(path, value)
                    if path.parent == directory and path.name == 'final-status-success.tmp' and phase == 'success_staging':
                        clock[0] = 1181.0
                        observations['expired_in'] = phase
                    return result
                def publishing(path, value, end=None):
                    observations['success_publish_calls' if value['status'] == 'success' else 'failed_publish_calls'] += 1
                    return original_publish(path, value, end=end)
                with patch.object(a.time, 'monotonic', side_effect=lambda: clock[0]), \
                        patch.object(a, 'check_context', side_effect=checking), \
                        patch.object(a, 'save', side_effect=saving), \
                        patch.object(a, 'publish', side_effect=publishing), \
                        patch.object(a, 'supervised', side_effect=local_worker):
                    try:
                        a.execute_verified_plan(strategy_dir / 'strategy.json', directory)
                    except f.BoundaryError as error:
                        equal(str(error), 'execution_deadline')
                    else:
                        f.fail('expired_execution_accepted')
                equal(observations['expired_in'], phase)
                final = f.parse(a.read(directory / 'final-status.json'))
                equal(final['status'], 'failed')
                if phase == 'post_hash_check':
                    equal(observations['success_publish_calls'], 0)
                else:
                    equal((directory / 'result.json').exists(), True)
                    equal((directory / 'report.md').exists(), True)
                    equal((directory / 'final-status-success.tmp').exists(), True)
                return {'actual': 'execution_deadline', 'expected': 'execution_deadline',
                        'reason_code': 'execution_deadline', 'phase': phase, 'terminal': 'failed',
                        'function_result': 'raised', **observations}
            case('M3_post_hash_expiry', lambda: deadline_test('expired-post-hash', 'post_hash_check'))
            case('M3_success_staging_expiry', lambda: deadline_test('expired-success-staging', 'success_staging'))
            def no_overwrite():
                original = a.read(normal_dir / 'final-status.json')
                try:
                    a.execute_verified_plan(strategy_dir / 'strategy.json', normal_dir)
                except f.BoundaryError as error:
                    equal(str(error), 'output_exists')
                else:
                    f.fail('existing_output_accepted')
                try:
                    a.publish(normal_dir, {'status': 'success'})
                except f.BoundaryError as error:
                    equal(str(error), 'terminal_exists')
                else:
                    f.fail('existing_terminal_accepted')
                equal(a.read(normal_dir / 'final-status.json'), original)
                return {'actual': 'output_exists/terminal_exists', 'expected': 'output_exists/terminal_exists',
                        'reason_code': 'output_exists/terminal_exists', 'target_bytes_unchanged': True}
            case('regression_no_overwrite', no_overwrite)
            def write_failure():
                directory = out / 'required-write-failure'
                original_save = a.save
                calls = []
                captured = io.StringIO()
                def saving(path, value):
                    if path.parent == directory and path.name == 'result.json':
                        calls.append('result.json')
                        raise OSError('RAW_SENSITIVE_ERROR')
                    return original_save(path, value)
                with patch.object(a, 'save', side_effect=saving), patch.object(a, 'supervised', side_effect=local_worker), redirect_stderr(captured):
                    equal(a.main(['execute', '--strategy', str(strategy_dir / 'strategy.json'), '--output-dir', str(directory)]), 1)
                equal(calls, ['result.json'])
                equal('RAW_SENSITIVE_ERROR' in captured.getvalue(), False)
                equal(f.parse(a.read(directory / 'final-status.json'))['status'], 'failed')
                return {'actual': 'nonzero_failed_terminal', 'expected': 'nonzero_failed_terminal',
                        'reason_code': 'w3_internal_failure', 'exit_status': 1, 'terminal': 'failed', 'raw_error_absent': True}
            case('regression_required_write_failure_safe_cleanup', write_failure)
    except BaseException:
        halted = 'r3_execution_halted'
    passed = halted is None and len(records) == 7 and all(r['status'] == 'passed' for r in records)
    result = {'schema_version': '1.0', 'batch_id': batch, 'synthetic': True,
        'offline_test_status': 'passed' if passed else 'failed' if records else 'halted',
        'exit_status': 0 if passed else 1, 'halted_reason': halted,
        'passed_cases': sum(r['status'] == 'passed' for r in records), 'total_cases': len(records),
        'technical_acceptance': 'pending', 'stage_acceptance': 'not_performed',
        'inherited_evidence': {'root': 'outputs/W3/offline-w3-e3o-r2-b/',
            'categories': ['upstream_and_strategy_binding', 'strict_csv_and_bucket_reference', 'S5_three_layers',
                           'claims_and_report_binding', 'worker_timeout', 'artifact_and_terminal_faults', 'safe_local_path'],
            'basis': 'ADR-009 / W3-v2 / W3-r2-evidence-calibration-v1'},
        'remaining_offline': [] if passed else ['R3 incomplete or failed; inspect actual cases'],
        'deferred_real': {'D301': 'not_run; real fixed chain not authorized',
                          'D302': 'not_run; real G3.5 not authorized',
                          'D303': 'not_run; real source hashing not authorized',
                          'D312': 'not_run; real execution not authorized'}}
    put(out / 'test.log', log.getvalue().encode())
    put(out / 'case-results.json', {'cases': records, 'halted_reason': halted})
    put(out / 'reference-results.json', references)
    put(out / 'batch-result.json', result)
    put(out / 'operation.json', {**a.operation('r3-offline', 'completed' if passed else 'failed'),
        'authorization': 'P-W3-E3-OFFLINE-R3', 'confirmation_actor': '用户',
        'confirmation_basis': '用户对精确R3候选回复批准', 'confirmed_at': 'not_provided',
        'started_at': started, 'elapsed_seconds': time.perf_counter() - started_clock,
        'exit_status': result['exit_status'], 'development_tokens': 'unknown', 'development_cost': 'unknown'})
    lines = ['# W3 R3 offline execution', '', '未验收，待high技术判定；W3总验收未进行。',
        '', 'Authorization: P-W3-E3-OFFLINE-R3; actor=用户; confirmed_at=not_provided.',
        'Command: .venv/Scripts/python.exe -B -m test_w3 --w3-r3-evidence --batch-id w3-e3o-r3-a',
        'cwd: D:\\MyPythonProjects\\datainsight',
        'Environment: PYTHONDONTWRITEBYTECODE=1; PYTHONPATH=project src;tests; TEMP/TMP/TMPDIR=project .cache/tmp.',
        'Python: ' + sys.version.split()[0] + '; DuckDB: ' + duckdb.__version__,
        'Actual exit: ' + str(result['exit_status']) + '; offline_test_status=' + result['offline_test_status'],
        '', '|case|actual|expected|assertion|', '|---|---|---|---|']
    for record in records:
        lines.append('| ' + record['case_id'] + ' | ' + record.get('actual', record.get('reason_code', 'unknown')) +
                     ' | ' + record.get('expected', 'assertions pass') + ' | ' + record['status'] + ' |')
    lines += ['', 'Evidence: outputs/W3/offline-w3-e3o-r3-a/; actual details in case-results.json.',
        'Inherited: outputs/W3/offline-w3-e3o-r2-b/ under ADR-009 and W3-v2; old results unchanged.',
        'remaining_offline: ' + json.dumps(result['remaining_offline']),
        'Deferred: real fixed chain, G3.5 decision, real source hash and D312 not authorized/not_run.',
        'Deadline is cooperative checks plus supervised worker, not OS hard realtime or total-memory isolation.',
        'No model/network/credential action requested; existing R2 evidence and unchanged paths inherited.',
        'recorded_at from operation.json: Python UTC tool time; development tokens/cost unknown.']
    put(document, ('\n'.join(lines) + '\n').encode())
    with (a.ROOT / 'docs/acceptance/results/INDEX.md').open('a', encoding='utf-8') as stream:
        stream.write('\n## W3 R3离线执行\n\n[w3-e3o-r3-a](w3-e3o-r3-a.md)：' + result['offline_test_status'] +
                     '（仅本批合成测试）；未验收，待high判定；真实门未启动。\n')
    print(json.dumps(result))
    return result['exit_status']


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--w3-evidence', action='store_true')
    mode.add_argument('--w3-r3-evidence', action='store_true')
    parser.add_argument('--batch-id', required=True)
    args = parser.parse_args()
    raise SystemExit(run_r3(args.batch_id) if args.w3_r3_evidence else run(args.batch_id))
