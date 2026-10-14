"""W2-B1 tests. No implicit real-input run; evidence runner requires approval.

This initial definition is incomplete until synthetic upstream-chain generation,
publication matrices and bounded reports are implemented. Do not treat static
assertions or patched contexts as real S2 receipt verification.
"""
from copy import deepcopy
from contextlib import ExitStack
import io
import os
from pathlib import Path
import unittest
from test_w2a import fixture, put, publication_fault, observed_calls, MARKERS
import json
import sys
import uuid
from test_w2a import bounded_inventory, READ_EVENTS
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch
from datainsight import feasibility as f
from datainsight import planning as p
from datainsight import planning_methods as m


def logical_context():
    """Controlled logical-only snapshot; never accepted by a production CLI."""
    return p.AcceptedContext(schema_version='1.0', dataset_version=f.digest(b'logical-fixture'),
        s2_receipt_ref=f.relative(p.S2), question_ref='controlled-question',
        question_version='v1', question_hash=f.digest(b'controlled-question'),
        diagnostic_rules_id='W2-A', diagnostic_rules_version='v1',
        diagnostic_rules_hash=f.digest(b'logical-rules'),
        eligible_method_ids=[m.METHOD], prerequisite_checks=[
            {'rule_id': m.METHOD, 'rule_version': 'v1', 'state': 'met',
             'premise': 'controlled logical prerequisite', 'evidence': 'controlled-reference'}],
        evidence_refs=['controlled-reference'])


def review_spec(decision='approve'):
    return {'decision': decision, 'selected_plan_id': 'P-BEHAVIOUR-RECORDS' if decision == 'approve' else None,
        'selected_plan_version': 'v1' if decision == 'approve' else None,
        'metric_definition_hash': f.digest(f.encoded(m.definition())) if decision == 'approve' else None,
        'confirm_metric_definition': decision == 'approve',
        'actor': 'controlled_test_actor', 'confirmed_at': f.now()}


class PlanningLogicTests(unittest.TestCase):
    def plans(self, context=None):
        context = context if context is not None else logical_context()
        with patch.object(p, 'load_s2_accept', return_value=deepcopy(context)):
            return p.build_candidate_plans(context, m.registered_methods())

    def test_B104_stable_and_closed(self):
        context = logical_context()
        first = self.plans(context)
        self.assertEqual(first, self.plans(context))
        self.assertEqual([c['method_id'] for c in first['candidates']], [m.METHOD])
        empty = deepcopy(context)
        empty['eligible_method_ids'] = []
        self.assertEqual(self.plans(empty)['candidates'], [])
        unknown = deepcopy(context)
        unknown['eligible_method_ids'] = ['UNKNOWN']
        with self.assertRaisesRegex(f.BoundaryError, '^unknown_eligible_method$'):
            self.plans(unknown)
        with self.assertRaisesRegex(f.BoundaryError, '^unverified_context$'):
            p.build_candidate_plans(dict(context), m.registered_methods())
        with patch.object(p, 'load_s2_accept', return_value=deepcopy(context)):
            with self.assertRaisesRegex(f.BoundaryError, '^unregistered_planning_methods$'):
                p.build_candidate_plans(context, dict(m.registered_methods(), sql='untrusted'))

    def test_B105_B106_definition_not_results(self):
        candidate = self.plans()['candidates'][0]
        self.assertEqual(candidate['metric_definition'], m.definition())
        self.assertEqual(candidate['metric_definition_hash'], f.digest(f.encoded(m.definition())))
        self.assertEqual(candidate['expected_output_schema'], m.OUTPUT_SCHEMA)
        self.assertEqual(m.METRIC['denominator'], 'not_applicable')
        self.assertEqual(m.METRIC['time_unit'], 'unknown')
        self.assertEqual(m.METRIC['timezone'], 'unknown')
        self.assertEqual(m.METRIC['global_filter'], 'none; no record exclusion')
        self.assertEqual(m.METRIC['transformation'], 'raw_preserved_no_transformation')
        self.assertEqual(m.METRIC['buckets'], ['pv', 'fav', 'cart', 'buy', 'missing', 'other'])
        self.assertFalse(any(k in candidate for k in ('values', 'gmv', 'conversion_rate', 'confidence', 'business_effect')))
        self.assertEqual(self.plans()['human_review_state'], 'pending')

    def test_B107_independent_review_errors(self):
        plans = self.plans()
        p.review_check(review_spec(), plans)
        for decision in ('reject', 'cancel'):
            self.assertIsNone(p.review_check(review_spec(decision), plans))
        cases = [('selected_plan_id', None, 'selected_plan_not_found'),
                 ('selected_plan_version', 'unknown', 'selected_plan_not_found'),
                 ('metric_definition_hash', f.digest(b'wrong'), 'metric_hash_mismatch'),
                 ('confirm_metric_definition', False, 'metric_confirmation_required'),
                 ('confirm_metric_definition', 'true', 'invalid_metric_confirmation_type'),
                 ('actor', '', 'invalid_identifier'), ('confirmed_at', '', 'invalid_text')]
        for key, value, reason in cases:
            spec = review_spec()
            spec[key] = value
            with self.subTest(key=key):
                with self.assertRaisesRegex(f.BoundaryError, '^' + reason + '$'):
                    p.review_check(spec, plans)
        with self.assertRaisesRegex(f.BoundaryError, '^selected_plan_not_found$'):
            p.review_check(review_spec(), dict(plans, candidates=[]))
        with self.assertRaisesRegex(f.BoundaryError, '^invalid_object_keys$'):
            p.review_check(dict(review_spec(), metric_definition={'amount': True}), plans)


CASE_RESULTS = []
FAULT_RESULTS = []
T1_RESULTS = []
T2_RESULTS = []
STREAMS = []


def upstream_terminal(directory, command):
    for name in f.REQUIRED[2:]:
        f.save(directory / name, {'controlled_fixture': True})
    f.publish(directory, {'schema_version': '1.0', 'run_id': directory.name, 'command': command,
        'status': 'success', 'exit_status': 0, 'completed_at': f.now(), 'required_evidence_refs': list(f.REQUIRED)})


class PlanningChainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = os.environ.get('W2B1_TEST_RUN')
        if not raw:
            raise RuntimeError('P-B1-SYN required: W2B1_TEST_RUN missing')
        cls.batch = f.path_check(Path(raw), p.OUTPUT)
        if cls.batch.parent != p.OUTPUT or not cls.batch.is_dir():
            raise RuntimeError('approved batch required')
        cls.scratch = f.ROOT / 'outputs/_scratch' / cls.batch.name
        if cls.scratch.exists():
            raise RuntimeError('scratch_exists')
        cls.scratch.mkdir(parents=True)

    def setUp(self):
        self.work = self.scratch / self._testMethodName
        self.work.mkdir()
        self.cases = 0

    def chain(self, case, decision='accept', omitted=None):
        root = self.work / case
        with ExitStack() as stack:
            stack.enter_context(patch.object(f, 'FIXTURE', root))
            stack.enter_context(patch.object(f, 'OUTPUT', p.OUTPUT))
            package = fixture(root, omit=(omitted,) if omitted else (), probes=True)
            if omitted:
                return package, stack.pop_all()
            snapshot = f.load_accepted_profile(package / 'profile.json', package / 'fixture-acceptance.json')
            question = {'schema_version': '1.0', 'question_id': 'controlled', 'question_version': 'v1',
                        'intent': 'behaviour_record_counts', 'requested_unit': 'raw_record'}
            qpath = root / 'question.json'
            qhash = put(qpath, question)
            snapshot['input_manifest']['files'].append({'path': f.relative(qpath), 'sha256': qhash})
            aliases = {
                'test_B101_real_verifiers_and_other_decisions': 'b101',
                'test_B103_candidate_and_review_restore': 'b103-restore',
                'test_B103_independent_upstream_mutations': 'b103-mutate',
                'test_B102_B103_real_missing_files': 'b103-missing',
                'test_B108_independent_plan_and_receipt_bindings': 'b108',
                'test_B110_real_publish_and_finalize_faults': 'b110',
                'test_B107_approve_and_cli_rejection': 'b107',
                'test_B102_types_versions_and_reparse': 'b102',
                'test_T1_dependency_changes': 't1',
                'test_T2_existing_output_protection': 't2',
            }
            alias = aliases[self._testMethodName]
            prefix = self.batch.name + '-' + alias + '-' + case
            for suffix in ('-s2diagnosis', '-s2receipt', '-source-candidates', '-candidates', '-review', '-target'):
                f.identifier(prefix + suffix)
            CASE_RESULTS.append({'test': self._testMethodName, 'case_id': case,
                'record_type': 'run_name_mapping', 'method_alias': alias,
                'run_prefix': prefix, 'scratch_ref': f.relative(root)})
            diagnosis_dir = f.new_run(p.OUTPUT / (prefix + '-s2diagnosis'))
            diagnosis = f.diagnose(question, snapshot, f.rules_module.registered_rules())
            diagnosis.update(run_id=diagnosis_dir.name, question_ref=f.relative(qpath), question_hash=qhash)
            f.save(diagnosis_dir / 'diagnosis.json', diagnosis)
            f.save(diagnosis_dir / 'input-manifest.json', snapshot['input_manifest'])
            f.save(diagnosis_dir / 'reference-check.json', {'schema_version': '1.0', 'references_resolvable': True,
                **{k: snapshot[k] for k in ('profile_identity', 'acceptance_basis', 'source_kind')}})
            upstream_terminal(diagnosis_dir, 'diagnose')
            receipt_dir = p.OUTPUT / (prefix + '-s2receipt')
            f.record_s2_decision(diagnosis, {'decision': decision, 'actor': 'controlled_test_actor',
                                          'confirmed_at': f.now()}, receipt_dir)
            upstream_terminal(receipt_dir, 'decide')
            acceptance = root / 'stage-acceptance.json'
            put(acceptance, '总判定：通过; controlled synthetic stage marker only\n'.encode('utf-8'))
            stack.enter_context(patch.object(p, 'S2', receipt_dir / 'decision.json'))
            stack.enter_context(patch.object(p, 'DIAGNOSIS', diagnosis_dir / 'diagnosis.json'))
            stack.enter_context(patch.object(p, 'ACCEPTANCE', acceptance))
            return {'root': root, 'package': package, 'diagnosis_dir': diagnosis_dir,
                    'receipt_dir': receipt_dir, 'prefix': prefix}, stack.pop_all()

    def run_cli(self, argv):
        with patch('sys.stdout', new_callable=io.StringIO) as stdout:
            status = p.main(argv)
        return status, stdout.getvalue()

    def test_B101_real_verifiers_and_other_decisions(self):
        for case in ('accept', 'request_data', 'reject', 'cancel'):
            chain, patches = self.chain(case, case)
            with patches:
                if case == 'accept':
                    context = p.load_s2_accept(p.S2)
                    self.assertEqual(context['acceptance_basis'], 'verified_s2_accept')
                    actual = 'accepted'
                else:
                    with self.assertRaisesRegex(f.BoundaryError, '^s2_not_accepted$'):
                        p.load_s2_accept(p.S2)
                    actual = 's2_not_accepted'
                CASE_RESULTS.append({'case_id': case, 'test': self._testMethodName,
                    'actual': actual, 'input': f.relative(chain['receipt_dir']),
                    'scope': 'real upstream verifiers; constants patched to synthetic paths'})

    def test_B103_candidate_and_review_restore(self):
        chain, patches = self.chain('normal')
        with patches:
            candidate_dir = p.OUTPUT / (chain['prefix'] + '-candidates')
            status, stdout = self.run_cli(['candidates', '--output-dir', str(candidate_dir)])
            self.assertEqual(status, 0)
            plan_path = candidate_dir / 'candidate-plans.json'
            plans, payload, context, manifest = p.load_plan_set(plan_path)
            before = f.digest(payload)
            review_dir = p.OUTPUT / (chain['prefix'] + '-review')
            spec = review_spec('cancel')
            status, output = self.run_cli(['review', '--plan-set', str(plan_path), '--decision', 'cancel',
                '--actor', spec['actor'], '--confirmed-at', spec['confirmed_at'], '--output-dir', str(review_dir)])
            self.assertEqual(status, 0)
            receipt = p.verify_review(review_dir / 's3-review.json')
            self.assertEqual(receipt['decision'], 'cancel')
            self.assertEqual(receipt['acceptance_scope'], 'S3_plan_and_metric_only')
            self.assertEqual(before, f.digest(f.read_bytes(plan_path)))
            CASE_RESULTS.append({'case_id': 'normal', 'test': self._testMethodName,
                'candidate_stdout': stdout, 'review_stdout': output, 'source_before': before,
                'source_after': f.digest(f.read_bytes(plan_path)), 'receipt': receipt})

    def test_B103_independent_upstream_mutations(self):
        cases = (('receipt-extra', 'decision.json', 'invalid_object_keys'),
                 ('receipt-version', 'decision.json', 'decision_binding'),
                 ('diagnosis-extra', 'diagnosis.json', 'invalid_object_keys'),
                 ('terminal-status', 'final-status.json', 'invalid_success_terminal'),
                 ('question-version', 'question.json', 'question_changed'))
        for case, name, expected in cases:
            chain, patches = self.chain(case)
            with patches:
                p.load_s2_accept(p.S2)
                target = (chain['root'] / name if name == 'question.json' else
                          chain['diagnosis_dir'] / name if name == 'diagnosis.json' else chain['receipt_dir'] / name)
                value = f.parse(target.read_bytes())
                if case.endswith('extra'):
                    value['extra'] = True
                elif case == 'terminal-status':
                    value['status'] = 'failed'
                else:
                    value['question_version' if name == 'question.json' else 'schema_version'] = 'unknown'
                # The mutated output is a deliberately controlled test input, not a real run.
                # Do not mutate completed runs: present changed bytes via a narrowly scoped reader.
                original_read = f.read_bytes
                changed = f.encoded(value)
                with patch.object(f, 'read_bytes', side_effect=lambda path, root=f.ROOT:
                                  changed if path == target else original_read(path, root)):
                    actual = None
                    try:
                        p.load_s2_accept(p.S2)
                    except f.BoundaryError as error:
                        actual = str(error)
                CASE_RESULTS.append({'case_id': case, 'test': self._testMethodName,
                    'input': f.relative(target), 'expected': expected, 'actual': actual,
                    'patch': 'one file byte reader; other verification real'})
                self.assertEqual(actual, expected)


    def test_B102_B103_real_missing_files(self):
        for case, omitted in (('missing-result', 'summary-result.json'),
                              ('missing-evidence', 'summary-evidence.json')):
            baseline, baseline_patches = self.chain(case + '-baseline')
            with baseline_patches:
                p.load_s2_accept(p.S2)
            package, patches = self.chain(case, omitted=omitted)
            with patches, observed_calls('w2b1:' + case):
                with self.assertRaisesRegex(f.BoundaryError, '^file_missing_or_size_boundary$'):
                    f.load_accepted_profile(package / 'profile.json', package / 'fixture-acceptance.json')
            CASE_RESULTS.append({'test': self._testMethodName, 'case_id': case,
                'omitted_at_creation': omitted, 'input': f.relative(package),
                'expected': 'file_missing_or_size_boundary', 'baseline': 'verified'})

    def test_B108_independent_plan_and_receipt_bindings(self):
        cases = ('candidate-value', 'metric-definition', 'registry-hash', 'receipt-dataset', 'receipt-scope')
        for case in cases:
            chain, patches = self.chain(case)
            with patches:
                candidate_dir = p.OUTPUT / (chain['prefix'] + '-candidates')
                status, _ = self.run_cli(['candidates', '--output-dir', str(candidate_dir)])
                self.assertEqual(status, 0)
                plan_path = candidate_dir / 'candidate-plans.json'
                plans, payload, context, manifest = p.load_plan_set(plan_path)
                review_dir = p.OUTPUT / (chain['prefix'] + '-review')
                status, _ = self.run_cli(['review', '--plan-set', str(plan_path), '--decision', 'cancel',
                    '--actor', 'controlled_test_actor', '--confirmed-at', f.now(), '--output-dir', str(review_dir)])
                self.assertEqual(status, 0)
                review_path = review_dir / 's3-review.json'
                p.verify_review(review_path)
                target = review_path if case.startswith('receipt-') else plan_path
                value = f.parse(target.read_bytes())
                if case == 'candidate-value':
                    value['candidates'][0]['gmv'] = 'untrusted'
                elif case == 'metric-definition':
                    value['candidates'][0]['metric_definition']['duplicate_policy'] = 'deduplicate'
                elif case == 'registry-hash':
                    value['registry_hash'] = f.digest(b'changed-registry')
                elif case == 'receipt-dataset':
                    value['dataset_version'] = f.digest(b'changed-dataset')
                else:
                    value['acceptance_scope'] = 'S4'
                original_read = f.read_bytes
                with patch.object(f, 'read_bytes', side_effect=lambda path, root=f.ROOT:
                                  f.encoded(value) if path == target else original_read(path, root)):
                    actual = None
                    try:
                        p.verify_review(review_path)
                    except f.BoundaryError as error:
                        actual = str(error)
                expected = 's3_receipt_binding_changed' if case.startswith('receipt-') else 'candidate_plan_changed'
                self.assertEqual(actual, expected)
                CASE_RESULTS.append({'test': self._testMethodName, 'case_id': case,
                    'input': f.relative(target), 'expected': expected, 'actual': actual,
                    'patch': 'single byte reader; original completed evidence retained'})

    def test_B110_real_publish_and_finalize_faults(self):
        for command in ('candidates', 'review'):
            faults = ('normal', 'tmp-open', 'tmp-write', 'tmp-flush', 'tmp-fsync', 'tmp-rename',
                      'environment.json', 'network-observation.json', 'cli-command.json',
                      'input-manifest.json', 'reference-check.json',
                      'candidate-plans.json' if command == 'candidates' else 's3-review.json')
            if command == 'candidates':
                faults += ('accepted-context.json',)
            for fault in faults:
                case = command + '-' + fault.replace('.', '-')
                chain, patches = self.chain(case)
                with patches:
                    source = p.OUTPUT / (chain['prefix'] + '-source-candidates')
                    source_hash = None
                    if command == 'review':
                        status, _ = self.run_cli(['candidates', '--output-dir', str(source)])
                        self.assertEqual(status, 0)
                        source_hash = f.digest(f.read_bytes(source / 'candidate-plans.json'))
                    target = p.OUTPUT / (chain['prefix'] + '-target')
                    argv = [command, '--output-dir', str(target)]
                    if command == 'review':
                        argv += ['--plan-set', str(source / 'candidate-plans.json'), '--decision', 'cancel',
                                 '--actor', 'controlled_test_actor', '--confirmed-at', f.now()]
                    events = []
                    original_save = p.save
                    def save(path, value):
                        if path.parent == target and path.name == fault:
                            events.append({'operation': 'evidence-write', 'path': f.relative(path)})
                            raise OSError('controlled_evidence_fault')
                        return original_save(path, value)
                    stdout, stderr = io.StringIO(), io.StringIO()
                    escaped = None
                    with patch.object(p, 'save', side_effect=save), publication_fault(target, fault, events), \
                            observed_calls('w2b1:' + case), redirect_stdout(stdout), redirect_stderr(stderr):
                        try:
                            status = p.main(argv)
                        except Exception as error:
                            status, escaped = None, type(error).__name__
                    terminal = f.parse(f.read_bytes(target / 'final-status.json')) if (target / 'final-status.json').exists() else None
                    residual = [f.relative(path) for path in target.iterdir() if path.suffix == '.tmp'] if target.exists() else []
                    record = {'case_id': case, 'command': command, 'argv': argv, 'exit_status': status,
                        'stdout': stdout.getvalue(), 'stderr': stderr.getvalue(), 'exception_type': escaped,
                        'events': events, 'terminal': terminal, 'tmp_remaining': residual,
                        'source_before': source_hash,
                        'source_after': f.digest(f.read_bytes(source / 'candidate-plans.json')) if source_hash else None,
                        'scope': 'same-process synthetic chain; real main/publish and upstream verifiers'}
                    FAULT_RESULTS.append(record)
                    STREAMS.append({'case_id': case, 'stdout': stdout.getvalue(), 'stderr': stderr.getvalue()})
                    self.assertIsNone(escaped)
                    self.assertEqual(status, 0 if fault == 'normal' else 2)
                    if fault == 'normal':
                        self.assertEqual(terminal['status'], 'success')
                    elif fault.startswith('tmp-'):
                        self.assertIsNone(terminal)
                        self.assertGreaterEqual(len(events), 2)
                        self.assertFalse(json.loads(stdout.getvalue())['failure_evidence_persisted'])
                    else:
                        self.assertEqual(terminal['status'], 'failed')
                    self.assertEqual(record['source_before'], record['source_after'])


    def test_B107_approve_and_cli_rejection(self):
        for case in ('approve', 'unconfirmed', 'unknown-selection', 'missing-actor'):
            chain, patches = self.chain(case)
            with patches:
                source = p.OUTPUT / (chain['prefix'] + '-candidates')
                status, _ = self.run_cli(['candidates', '--output-dir', str(source)])
                self.assertEqual(status, 0)
                plan_path = source / 'candidate-plans.json'
                p.load_plan_set(plan_path)
                before = f.digest(f.read_bytes(plan_path))
                target = p.OUTPUT / (chain['prefix'] + '-review')
                spec = review_spec()
                argv = ['review', '--plan-set', str(plan_path), '--decision', 'approve',
                    '--selected-plan-id', 'UNKNOWN' if case == 'unknown-selection' else spec['selected_plan_id'],
                    '--selected-plan-version', spec['selected_plan_version'],
                    '--metric-definition-hash', spec['metric_definition_hash'],
                    '--actor', '' if case == 'missing-actor' else spec['actor'],
                    '--confirmed-at', spec['confirmed_at'], '--output-dir', str(target)]
                if case != 'unconfirmed':
                    argv.append('--confirm-metric-definition')
                status, stdout = self.run_cli(argv)
                self.assertEqual(status, 0 if case == 'approve' else 2)
                if case == 'approve':
                    receipt = p.verify_review(target / 's3-review.json')
                    self.assertEqual(receipt['decision'], 'approve')
                else:
                    self.assertFalse((target / 's3-review.json').exists())
                self.assertEqual(before, f.digest(f.read_bytes(plan_path)))
                CASE_RESULTS.append({'test': self._testMethodName, 'case_id': case,
                    'argv': argv, 'exit_status': status, 'stdout': stdout,
                    'synthetic_actor': True, 'not_user_business_approval': True})
                STREAMS.append({'case_id': case, 'stdout': stdout, 'stderr': ''})

    def test_B102_independent_json_and_path_boundaries(self):
        cases = (('duplicate-key', b'{"a":1,"a":2}', 'duplicate_json_key'),
                 ('nonfinite', b'{"a":NaN}', 'nonfinite_json'))
        for case, payload, reason in cases:
            with self.assertRaisesRegex(f.BoundaryError, '^' + reason + '$'):
                f.parse(payload)
            CASE_RESULTS.append({'test': self._testMethodName, 'case_id': case, 'expected': reason})
        with patch.object(Path, 'open', side_effect=AssertionError('dangerous_open')):
            with self.assertRaisesRegex(f.BoundaryError, '^s2_source_not_allowed$'):
                p.load_s2_accept(f.ROOT / 'unapproved.json')
            with self.assertRaisesRegex(f.BoundaryError, '^invalid_path$'):
                p.load_s2_accept(f.ROOT / '..' / 'unapproved.json')
        oversized = self.work / 'oversized.json'
        put(oversized, b' ' * (f.LIMIT + 1))
        with patch.object(Path, 'open', side_effect=AssertionError('dangerous_open')):
            with self.assertRaisesRegex(f.BoundaryError, '^file_missing_or_size_boundary$'):
                f.read_bytes(oversized)


    def test_B102_types_versions_and_reparse(self):
        for case, key, value, reason in (
                ('version', 'schema_version', 'unknown', 'decision_binding'),
                ('type', 'confirm_metric_definition', 1, 'invalid_metric_confirmation_type')):
            if case == 'type':
                plans = PlanningLogicTests().plans()
                spec = review_spec()
                spec[key] = value
                with self.assertRaisesRegex(f.BoundaryError, '^' + reason + '$'):
                    p.review_check(spec, plans)
            else:
                chain, patches = self.chain(case)
                with patches:
                    p.load_s2_accept(p.S2)
                    original = f.read_bytes
                    target = p.S2
                    document = f.parse(original(target))
                    document[key] = value
                    with patch.object(f, 'read_bytes', side_effect=lambda path, root=f.ROOT:
                                      f.encoded(document) if path == target else original(path, root)):
                        with self.assertRaisesRegex(f.BoundaryError, '^' + reason + '$'):
                            p.load_s2_accept(target)
            CASE_RESULTS.append({'test': self._testMethodName, 'case_id': case, 'expected': reason})
        from types import SimpleNamespace
        import stat
        original = Path.lstat
        def linked(path, *args, **kwargs):
            if path == self.work:
                return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
            return original(path, *args, **kwargs)
        with patch.object(Path, 'lstat', linked), patch.object(Path, 'open', side_effect=AssertionError('opened')):
            with self.assertRaisesRegex(f.BoundaryError, '^reparse_denied$'):
                f.read_bytes(self.work / 'probe.json')

    def test_B105_template_and_contract_consistency(self):
        from datainsight.profile_templates import ProfileTemplateId, FIELDS, BODIES
        contract = f.parse(f.read_bytes(f.CONTRACT))
        self.assertFalse(contract['trim'])
        self.assertEqual(contract['time_unit'], 'unknown')
        self.assertEqual(contract['timezone'], 'unknown')
        self.assertEqual(list(FIELDS[ProfileTemplateId.BEHAVIOURS]), m.METRIC['buckets'])
        body = BODIES[ProfileTemplateId.BEHAVIOURS]
        self.assertIn('behaviour IS NULL', body)
        self.assertIn('behaviour IS NOT NULL', body)
        self.assertNotIn('DISTINCT', body)
        self.assertEqual(m.METRIC['dimensions'], ['fixed_behaviour_bucket'])


    def successful_plans_and_review(self, chain):
        candidate_dir = p.OUTPUT / (chain['prefix'] + '-candidates')
        status, _ = self.run_cli(['candidates', '--output-dir', str(candidate_dir)])
        self.assertEqual(status, 0)
        path = candidate_dir / 'candidate-plans.json'
        plans, _, _, _ = p.load_plan_set(path)
        target = p.OUTPUT / (chain['prefix'] + '-review')
        status, _ = self.run_cli(['review', '--plan-set', str(path), '--decision', 'cancel',
            '--actor', 'controlled_test_actor', '--confirmed-at', f.now(), '--output-dir', str(target)])
        self.assertEqual(status, 0)
        receipt_path = target / 's3-review.json'
        receipt = p.verify_review(receipt_path)
        return path, receipt_path, plans, receipt

    def test_T1_dependency_changes(self):
        for case in ('data', 'rules', 'registry'):
            chain, patches = self.chain(case)
            with patches:
                context = p.load_s2_accept(p.S2)
                registry = m.registered_methods()
                plan_path, review_path, plans, receipt = self.successful_plans_and_review(chain)
                protected = [(plan_path.parent, 'new_synthetic'), (review_path.parent, 'new_synthetic')]
                before = bounded_inventory(protected)
                original_reader = f.read_bytes
                dependency = None
                with ExitStack() as change:
                    if case == 'data':
                        target = chain['package'] / 'profile.json'
                        value = f.parse(original_reader(target))
                        value['dataset_version'] = f.digest(b'T1-new-controlled-data-version')
                        change.enter_context(patch.object(f, 'read_bytes', side_effect=lambda path, root=f.ROOT:
                            f.encoded(value) if path == target else original_reader(path, root)))
                        dependency = {'path': f.relative(target), 'field': 'dataset_version',
                                      'new_identity': value['dataset_version'], 'patch': 'single input byte reader'}
                        expected = 'fixture_acceptance'
                    elif case == 'rules':
                        value = dict(f.rules_module.registered_rules(), ruleset_version='t1-new',
                                     ruleset_hash=f.digest(b'T1-new-controlled-rules'))
                        change.enter_context(patch.object(f.rules_module, 'registered_rules', return_value=value))
                        dependency = {'function': 'feasibility.rules_module.registered_rules',
                                      'identity': value, 'patch': 'current identity only; real evaluate/diagnose'}
                        expected = 'diagnosis_or_rules_changed'
                    else:
                        value = dict(registry, registry_version='t1-new',
                                     registry_hash=f.digest(b'T1-new-controlled-registry'))
                        change.enter_context(patch.object(m, 'registered_methods', return_value=value))
                        dependency = {'function': 'planning_methods.registered_methods',
                                      'identity': value, 'patch': 'current identity only; real plan generation'}
                        expected = 'candidate_plan_changed'
                    checks = []
                    entries = [('old-context', lambda: p.build_candidate_plans(context, registry),
                                'unregistered_planning_methods' if case == 'registry' else expected),
                               ('candidate-restore', lambda: p.load_plan_set(plan_path), expected),
                               ('review-restore', lambda: p.verify_review(review_path), expected)]
                    for entry, action, reason in entries:
                        actual = None
                        try:
                            action()
                        except f.BoundaryError as error:
                            actual = str(error)
                        checks.append({'entry': entry, 'expected': reason, 'actual': actual,
                                       'matches': reason == actual})
                    after = bounded_inventory(protected)
                report = {'case_id': case, 'baseline_context': context,
                    'baseline_plan': plans, 'baseline_receipt': receipt,
                    'dependency': dependency, 'checks': checks, 'before': before, 'after': after,
                    'unchanged': before == after, 'synthetic_test_input': True,
                    'not_user_confirmation': True}
                T1_RESULTS.append(report)
                self.assertEqual(before, after)
                self.assertTrue(all(v['matches'] for v in checks), 'dependency_reason_mismatch')

    def test_T2_existing_output_protection(self):
        for case in ('candidates', 'review', 'newrun'):
            chain, patches = self.chain(case)
            with patches:
                source, _, _, _ = self.successful_plans_and_review(chain)
                source_before = bounded_inventory([(source.parent, 'new_synthetic')])
                target = p.new_run(p.OUTPUT / (chain['prefix'] + '-target'))
                p.save(target / 'marker.json', {'controlled_preserve': True})
                before = bounded_inventory([(target, 'new_synthetic')])
                argv = [case, '--output-dir', str(target)]
                if case == 'review':
                    argv += ['--plan-set', str(source), '--decision', 'cancel',
                             '--actor', 'controlled_test_actor', '--confirmed-at', f.now()]
                events = []
                original_open = Path.open
                def opened(path, *args, **kwargs):
                    mode = args[0] if args else kwargs.get('mode', 'r')
                    if target == path or target in path.parents:
                        events.append({'path': f.relative(path), 'mode': mode})
                    return original_open(path, *args, **kwargs)
                stdout, stderr = io.StringIO(), io.StringIO()
                reason, status = None, None
                with patch.object(Path, 'open', opened), redirect_stdout(stdout), redirect_stderr(stderr):
                    if case == 'newrun':
                        try:
                            p.new_run(target)
                        except f.BoundaryError as error:
                            reason, status = str(error), 2
                    else:
                        status = p.main(argv)
                        reason = json.loads(stdout.getvalue())['reason_code']
                after = bounded_inventory([(target, 'new_synthetic')])
                source_after = bounded_inventory([(source.parent, 'new_synthetic')])
                writes = [v for v in events if any(c in v['mode'] for c in ('w', 'a', 'x', '+'))]
                T2_RESULTS.append({'case_id': case, 'argv': argv if case != 'newrun' else None,
                    'direct_call': 'planning.new_run' if case == 'newrun' else None,
                    'exit_status': status, 'actual': reason, 'expected': 'output_exists',
                    'stdout': stdout.getvalue(), 'stderr': stderr.getvalue(), 'open_events': events,
                    'write_events': writes, 'before': before, 'after': after,
                    'source_before': source_before, 'source_after': source_after,
                    'terminal_exists': (target / 'final-status.json').exists()})
                STREAMS.append({'case_id': 'T2:' + case, 'stdout': stdout.getvalue(), 'stderr': stderr.getvalue()})
                self.assertEqual(status, 2)
                self.assertEqual(reason, 'output_exists')
                self.assertEqual(before, after)
                self.assertEqual(source_before, source_after)
                self.assertEqual(writes, [])
                self.assertFalse((target / 'final-status.json').exists())


ACTIVE_BATCH = None


def evidence_runner(supplement=False):
    global ACTIVE_BATCH
    env = f.environment()
    if Path.cwd() != f.ROOT:
        raise RuntimeError('project_cwd_required')
    batch = p.new_run(p.OUTPUT / (('w2b1-t1t2-' if supplement else 'w2b1-syn-') + uuid.uuid4().hex))
    ACTIVE_BATCH = batch
    os.environ['W2B1_TEST_RUN'] = str(batch)
    started = f.now()
    protected_paths = [f.ROOT / name for name in ('src/datainsight/feasibility.py',
        'src/datainsight/feasibility_rules.py', 'src/datainsight/planning.py',
        'src/datainsight/planning_methods.py', 'docs/acceptance/W2-B1-v1.md',
        'docs/decisions/ADR-003-directory-and-evidence-layout.md',
        'docs/decisions/ADR-004-W2B-candidate-and-review-boundary.md',
        'docs/decisions/ADR-005-approval-responsibility-and-confirmation-time.md',
        'configs/w1b-read-contract-v1.json', 'configs/w2a-question-v1.json')]
    def protection():
        return [{'path': f.relative(path), 'sha256': f.digest(f.read_bytes(path))} for path in protected_paths]
    before = protection()
    put(batch / 'protected-files-before.json', before)
    source = f.path_check(Path(__file__).absolute(), f.ROOT / 'tests')
    put(batch / 'source-snapshots/test_w2b1.py', source.read_bytes())
    put(batch / 'source-identity.json', {'protected': before,
        'test_sha256': f.digest(source.read_bytes()), 'helper_sha256': f.digest(f.read_bytes(f.ROOT / 'tests/test_w2a.py'))})
    shell = "cd /d/MyPythonProjects/datainsight && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH='D:\\MyPythonProjects\\datainsight\\src;D:\\MyPythonProjects\\datainsight\\tests' TEMP='D:\\MyPythonProjects\\datainsight\\.cache\\tmp' TMP='D:\\MyPythonProjects\\datainsight\\.cache\\tmp' TMPDIR='D:\\MyPythonProjects\\datainsight\\.cache\\tmp' .venv/Scripts/python.exe -B -m test_w2b1 --w2b1-evidence"
    if supplement:
        shell = shell.replace('--w2b1-evidence', '--w2b1-t1t2-evidence')
        put(batch / 'authorization-record.json', {
            'confirmation_actor': 'user', 'confirmed_at': 'not_provided',
            'confirmation_basis': 'explicit approval of P-B1-TRUN single synthetic batch',
            'recorded_at': f.now(), 'recorded_at_source': 'Python datetime.now(timezone.utc) via feasibility.now',
            'recorded_at_status': 'available',
            'authorization_scope': 'T1/T2 tests and reports only; no real business review or implementation change',
            'bound_versions': ['W2-B1-v1 frozen', 'W2-B1-T1-T2-sol61-low-v1', 'ADR-005'],
            'technical_responsibility': '技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。'})
    put(batch / 'batch-command.json', {'argv': sys.argv, 'shell_transcript': shell,
        'executable': sys.executable, 'cwd': str(Path.cwd()), 'batch_id': batch.name})
    put(batch / 'batch-environment.json', env)
    log = io.StringIO()
    suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(PlanningLogicTests),
        unittest.defaultTestLoader.loadTestsFromTestCase(PlanningChainTests),
        unittest.defaultTestLoader.loadTestsFromNames([
            'test_w1b_profile.ProfileReferenceTests.test_unknown_template_before_connection',
            'test_w1b_profile.ProfileReferenceTests.test_result_boundaries_and_nested_types'])])
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    put(batch / 'test.log', log.getvalue().encode())
    put(batch / 'case-results.json', CASE_RESULTS)
    put(batch / 'fault-results.json', FAULT_RESULTS)
    if supplement:
        put(batch / 't1-dependency-results.json', T1_RESULTS)
        put(batch / 't2-existing-output-results.json', T2_RESULTS)
    put(batch / 'read-observation.json', {'events': READ_EVENTS,
        'scope': 'selected chain/matrix wrappers only; not native or system isolation'})
    after = protection()
    put(batch / 'protected-files-after.json', after)
    roots = [(batch, 'new_synthetic')]
    roots += [(path, 'new_synthetic') for path in sorted(p.OUTPUT.iterdir()) if path.name.startswith(batch.name + '-')]
    scratch = f.ROOT / 'outputs/_scratch' / batch.name
    if scratch.exists():
        roots.append((scratch, 'fixture_input'))
    # Local inventory duplicates the read-only helper semantics, allowing our own snapshot filename.
    def inventory():
        items = []
        def visit(path, category):
            f.path_check(path, f.ROOT)
            if path.is_dir():
                for child in sorted(path.iterdir()):
                    visit(child, category)
            else:
                if path.suffix not in ('.json', '.log', '.tmp', '.py'):
                    raise RuntimeError('unexpected_artifact_family')
                payload = path.read_bytes()
                items.append({'path': f.relative(path), 'category': category,
                              'size': len(payload), 'sha256': f.digest(payload)})
        for root, category in roots:
            visit(root, category)
        return items
    files = inventory()
    findings, exclusions, scanned = [], [], []
    for item in files:
        path = f.ROOT / item['path']
        if item['category'] == 'fixture_input' or 'source-snapshots/' in item['path']:
            exclusions.append({'path': item['path'], 'reason': 'intentional_fixture/test_source'})
            continue
        scanned.append(item['path'])
        data = path.read_bytes()
        for marker_id, marker in MARKERS.items():
            count = data.count(marker.encode())
            if count:
                findings.append({'marker_id': marker_id, 'path': item['path'], 'count': count})
    for stream in STREAMS:
        for channel in ('stdout', 'stderr'):
            for marker_id, marker in MARKERS.items():
                count = stream[channel].count(marker)
                if count:
                    findings.append({'marker_id': marker_id, 'stream': stream['case_id'] + ':' + channel, 'count': count})
    put(batch / 'privacy-scan.json', {'scanned_files': scanned,
        'streams': [v['case_id'] for v in STREAMS], 'exclusions': exclusions, 'findings': findings,
        'trace_scope': 'no separate trace'})
    self_reports = ('artifact-inventory.json', 'privacy-scan.json', 'batch-result.json', 'batch-status.json')
    put(batch / 'artifact-inventory.json', {'files': files, 'self_reports': list(self_reports),
        'reason': 'self-referential reports explicitly excluded from self-hash'})
    covered = {v['path'] for v in files} | {f.relative(batch / name) for name in self_reports}
    missing = {v['path'] for v in inventory()} - covered
    required_cases = {(command, command + '-' + fault.replace('.', '-'))
        for command in ('candidates', 'review')
        for fault in ('normal', 'tmp-open', 'tmp-write', 'tmp-flush', 'tmp-fsync', 'tmp-rename',
                      'environment.json', 'network-observation.json', 'cli-command.json',
                      'input-manifest.json', 'reference-check.json',
                      'candidate-plans.json' if command == 'candidates' else 's3-review.json')}
    required_cases.add(('candidates', 'candidates-accepted-context-json'))
    missing_faults = required_cases - {(v['command'], v['case_id']) for v in FAULT_RESULTS}
    t_complete = (not supplement or (
        {v['case_id'] for v in T1_RESULTS} == {'data', 'rules', 'registry'}
        and all(v['unchanged'] and len(v['checks']) == 3 and all(c['matches'] for c in v['checks']) for v in T1_RESULTS)
        and {v['case_id'] for v in T2_RESULTS} == {'candidates', 'review', 'newrun'}
        and all(v['actual'] == 'output_exists' and v['before'] == v['after']
                and v['source_before'] == v['source_after'] and not v['write_events'] for v in T2_RESULTS)))
    success = result.wasSuccessful() and before == after and not findings and not missing and not missing_faults and t_complete
    status = 0 if success else 2
    put(batch / 'batch-result.json', {'tests_run': result.testsRun, 'failures': len(result.failures),
        'errors': len(result.errors), 'exit_status': status, 'uncovered_paths': sorted(missing),
        'missing_fault_cases': sorted(missing_faults), 'protection_unchanged': before == after,
        't1_t2_complete': t_complete,
        'final_acceptance': 'not_performed'})
    put(batch / 'batch-status.json', {'status': 'success' if success else 'failed', 'exit_status': status,
        'started_at': started, 'completed_at': f.now(), 'self_exclusion': list(self_reports),
        'final_acceptance': 'not_performed'})
    print(json.dumps({'batch': str(batch), 'exit_status': status}))
    return status


if __name__ == '__main__':
    if sys.argv[1:] in (['--w2b1-evidence'], ['--w2b1-t1t2-evidence']):
        try:
            status = evidence_runner(supplement=sys.argv[1:] == ['--w2b1-t1t2-evidence'])
        except Exception as error:
            persisted = False
            if ACTIVE_BATCH is not None:
                try:
                    path = ACTIVE_BATCH / 'batch-status.json'
                    if not path.exists():
                        put(path, {'status': 'failed', 'exit_status': 2, 'exception_type': type(error).__name__,
                            'final_acceptance': 'not_performed'})
                        persisted = True
                except Exception:
                    pass
            print(json.dumps({'status': 'failed', 'exit_status': 2,
                'exception_type': type(error).__name__, 'failure_evidence_persisted': persisted}))
            status = 2
        raise SystemExit(status)
    unittest.main()

