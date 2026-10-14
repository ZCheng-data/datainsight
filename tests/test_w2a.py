"""Controlled W2-A tests; no CSV, engine, external service or automatic cleanup.

Requires a separately approved P-SYN with W2A_TEST_RUN pointing to a fresh
outputs/W2-A/<run_id>. Generated fixtures stay under that batch's _scratch
identity; they are retained, not static repository fixtures or production truth.
"""
from copy import deepcopy
from contextlib import ExitStack
import io
from pathlib import Path
import hashlib
import json
import os
import sys
import builtins
import socket
import stat
import time
import uuid
import unittest
from contextlib import contextmanager, redirect_stdout, redirect_stderr
from unittest.mock import patch
from datainsight import feasibility as f
from datainsight import feasibility_rules as r


def put(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = data if type(data) is bytes else f.encoded(data)
    with path.open('xb') as stream:
        stream.write(payload)
    return f.digest(payload)


MARKERS = {key: 'W2A_R1R4_' + key + '_SENTINEL'
           for key in ('SOURCE', 'ROW', 'IDENTIFIER', 'SECRET', 'INSTRUCTION')}
CASE_RESULTS = []
PUBLICATION_RESULTS = []
READ_EVENTS = []
PRODUCT_STREAMS = []
ACTIVE_BATCH = None


def fixture(root, omit=(), probes=False):
    """Tool-generated aggregate oracle, not copied production metrics or hashes."""
    directory = root / 'profile-package'
    version = hashlib.sha256(b'controlled-w2a-aggregate-oracle-v1').hexdigest()
    instant = f.now()
    profile = {'schema_version': '1.0', 'run_id': directory.name, 'stage': 'S1',
        'status': 'computed_pending_finalization', 'dataset_version': version,
        'reading_schema': [{'name': n, 'type': 'VARCHAR'} for n in f.COLUMNS],
        'metrics': {}, 'product_model_usage': 'not_applicable', 'limitations': ['controlled small fixture only']}
    values = {m: [{k: (n if k == 'column_name' else None if k in ('minimum', 'maximum') else 0)
                       for k in f.FIELDS[m]} for n in (f.COLUMNS if m == 'columns' else (None,))]
              for m in f.FIELDS}
    contract_hash = f.digest(f.read_bytes(f.CONTRACT))
    for metric, rows in values.items():
        result_payload = f.encoded(rows)
        result_hash = f.digest(result_payload)
        if metric + '-result.json' not in omit:
            put(directory / (metric + '-result.json'), result_payload)
        evidence = {'schema_version': '1.0', 'evidence_id': directory.name + ':' + metric,
            'run_id': directory.name, 'dataset_version': version, 'source_id': 'controlled_fixture',
            'source_path': 'SENTINEL_SOURCE_MUST_NOT_OPEN', 'read_config_ref': f.relative(f.CONTRACT),
            'read_config_version': '1.0', 'read_config_sha256': contract_hash,
            'template_id': metric, 'template_version': '1.0',
            'template_sha256': f.digest(('controlled:' + metric).encode()),
            'sql': 'SENTINEL_SQL_MUST_NOT_EXECUTE', 'parameters': ['SENTINEL_PARAMETER'],
            'python_version': 'controlled', 'duckdb_version': 'not_started', 'status': 'success',
            'started_at': instant, 'ended_at': instant, 'result_ref': metric + '-result.json',
            'result_sha256': result_hash, 'metric_definition_version': '1.0',
            'engine_configuration': {k: 'controlled' for k in ('allow_unsigned_extensions',
                'autoinstall_known_extensions', 'autoload_known_extensions', 'enable_external_access',
                'extension_directory', 'temp_directory')}}
        if probes:
            evidence.update(source_path=MARKERS['SOURCE'], sql=MARKERS['INSTRUCTION'],
                            parameters=[MARKERS[k] for k in ('ROW', 'IDENTIFIER', 'SECRET')])
        if metric + '-evidence.json' not in omit:
            put(directory / (metric + '-evidence.json'), evidence)
        profile['metrics'][metric] = {'evidence_id': evidence['evidence_id'],
                                     'result_ref': evidence['result_ref'], 'values': rows}
    fp = {'algorithm': 'SHA-256', 'bytes_read': 0, 'elapsed_seconds': 0,
          'started_at': instant, 'ended_at': instant, 'evidence_ref': 'fingerprints.json', 'sha256': version}
    put(directory / 'fingerprints.json', {'before': fp, 'after': fp, 'consistent': True})
    put(directory / 'profile.json', profile)
    put(directory / 'fixture-acceptance.json', {'schema_version': '1.0', 'kind': 'controlled_fixture',
                                             'dataset_version': version})
    for name in f.REQUIRED[1:]:
        put(directory / name, {'controlled_fixture': True})
    put(directory / 'final-status.json', {'run_id': directory.name, 'command': 'profile',
        'status': 'success', 'exit_status': 0, 'completed_at': instant,
        'required_evidence_refs': list(f.REQUIRED[1:])})
    return directory


def fixture_manifest(root, purpose):
    files = bounded_inventory([(root, 'fixture_input')])
    put(root / 'fixture-manifest.json', {'purpose': purpose, 'files': files,
        'self_exclusion': 'fixture-manifest.json', 'synthetic_only': True})


class W2ATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('W2A_TEST_RUN')
        if not value:
            raise RuntimeError('P-SYN required: missing W2A_TEST_RUN')
        cls.batch = f.path_check(Path(value), f.OUTPUT)
        if cls.batch.parent != f.OUTPUT or not cls.batch.is_dir():
            raise RuntimeError('approved existing batch directory required')
        cls.fixture_root = f.ROOT / 'outputs/_scratch' / cls.batch.name
        if cls.fixture_root.exists():
            raise RuntimeError('scratch batch already exists; no reuse')
        cls.fixture_root.mkdir(parents=True)

    def setUp(self):
        self.work = self.fixture_root / self._testMethodName
        self.work.mkdir()
        self.package = fixture(self.work)
        self.fixture_patch = patch.object(f, 'FIXTURE', self.work)
        self.fixture_patch.start()
        self.addCleanup(self.fixture_patch.stop)
        self.question = {'schema_version': '1.0', 'question_id': 'controlled',
            'question_version': 'v1', 'intent': 'behaviour_record_counts', 'requested_unit': 'raw_record'}

    def snapshot(self):
        return f.load_accepted_profile(self.package / 'profile.json', self.package / 'fixture-acceptance.json')

    def mutate(self, name, change):
        # Only this test's generated, unpublished input; never a completed run.
        path = self.package / name
        value = f.parse(path.read_bytes())
        change(value)
        path.write_bytes(f.encoded(value))

    def completed_diagnosis(self):
        snapshot = self.snapshot()
        qpath = self.work / 'question.json'
        qhash = put(qpath, self.question)
        snapshot['input_manifest']['files'].append({'path': f.relative(qpath), 'sha256': qhash})
        directory = f.new_run(f.OUTPUT / (self.batch.name + '-' + self._testMethodName))
        diagnosis = f.diagnose(self.question, snapshot, r.registered_rules())
        diagnosis.update(run_id=directory.name, question_ref=f.relative(qpath), question_hash=qhash)
        f.save(directory / 'diagnosis.json', diagnosis)
        f.save(directory / 'input-manifest.json', snapshot['input_manifest'])
        f.save(directory / 'reference-check.json', {'schema_version': '1.0', 'references_resolvable': True,
            **{k: snapshot[k] for k in ('profile_identity', 'acceptance_basis', 'source_kind')}})
        for name in f.REQUIRED[2:]:
            f.save(directory / name, {'controlled': True})
        f.publish(directory, {'schema_version': '1.0', 'run_id': directory.name, 'command': 'diagnose',
            'status': 'success', 'exit_status': 0, 'completed_at': f.now(), 'required_evidence_refs': list(f.REQUIRED)})
        return diagnosis, directory

    def test_A01_current_protocol_and_old_success_rejection(self):
        self.assertEqual(self.snapshot()['acceptance_basis'], 'current_protocol_success')
        self.mutate('profile.json', lambda v: v.update(status='success'))
        with self.assertRaises(f.BoundaryError):
            self.snapshot()

    def test_A01_pending_failed_missing_terminal(self):
        for status in ('pending', 'failed'):
            self.mutate('final-status.json', lambda v: v.update(status=status))
            with self.assertRaises(f.BoundaryError):
                self.snapshot()
        with patch.object(f, 'read_bytes', side_effect=f.BoundaryError('missing')):
            with self.assertRaises(f.BoundaryError):
                self.snapshot()

    def test_A02_json_strictness(self):
        for payload in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e999}', b'not-json'):
            with self.assertRaises(f.BoundaryError):
                f.parse(payload)
        cases = (('extra-key', 'invalid_object_keys', {'extra': True}),
                 ('unknown-profile-version', 'profile_identity', {'schema_version': 'unknown'}),
                 ('bad-reading-schema', 'reading_schema', {'reading_schema': []}))
        for case, expected, change in cases:
            package = fixture(self.work / case)
            baseline = f.load_accepted_profile(package / 'profile.json', package / 'fixture-acceptance.json')
            path = package / 'profile.json'
            value = f.parse(path.read_bytes())
            value.update(change)
            path.write_bytes(f.encoded(value))
            fixture_manifest(self.work / case, 'R1:' + case)
            actual = None
            try:
                f.load_accepted_profile(path, package / 'fixture-acceptance.json')
            except f.BoundaryError as error:
                actual = str(error)
            CASE_RESULTS.append({'group': 'R1', 'case_id': case, 'input': f.relative(path),
                'baseline': baseline, 'expected': expected, 'actual': actual, 'matches': actual == expected})
            self.assertEqual(actual, expected)

    def test_A02_paths_and_size_before_open(self):
        for path in (self.work / '..' / 'unsafe.json', f.ROOT / 'unapproved.json'):
            with self.assertRaises(f.BoundaryError), patch.object(Path, 'open', side_effect=AssertionError('opened')):
                f.read_bytes(path, self.work)
        oversized = self.work / 'oversized.json'
        put(oversized, b' ' * (f.LIMIT + 1))
        with self.assertRaises(f.BoundaryError), patch.object(Path, 'open', side_effect=AssertionError('opened')):
            f.read_bytes(oversized)
        with patch.object(Path, 'resolve', return_value=f.ROOT / 'different'):
            with self.assertRaises(f.BoundaryError):
                f.path_check(self.work, f.ROOT)

    def test_A03_result_reference_and_hash(self):
        self.mutate('summary-evidence.json', lambda v: v.update(result_ref='../outside.json'))
        with self.assertRaises(f.BoundaryError):
            self.snapshot()
        self.mutate('summary-evidence.json', lambda v: v.update(result_ref='summary-result.json'))
        self.mutate('summary-result.json', lambda v: v[0].update(row_count=1))
        with self.assertRaises(f.BoundaryError):
            self.snapshot()

    def test_A03_dataset_and_fingerprint_binding(self):
        self.mutate('fingerprints.json', lambda v: v['before'].update(sha256='0' * 64))
        with self.assertRaises(f.BoundaryError):
            self.snapshot()

    def test_A04_missing_unknown_extra_inputs(self):
        snapshot = self.snapshot()
        self.assertEqual(f.diagnose(None, snapshot, r.registered_rules())['request_state'], 'needs_question')
        unknown = dict(self.question, intent='unknown')
        result = f.diagnose(unknown, snapshot, r.registered_rules())
        self.assertEqual(result['request_state'], 'unsupported_request')
        self.assertEqual(result['eligible_method_ids'], [])
        for key in ('sql', 'path', 'rules', 'field_mapping'):
            with self.assertRaises(f.BoundaryError):
                f.diagnose(dict(self.question, **{key: 'injection'}), snapshot, r.registered_rules())

    def test_A05_A08_supported_quality_without_business_inference(self):
        result = f.diagnose(self.question, self.snapshot(), r.registered_rules())
        self.assertEqual(result['capability'], 'supported')
        self.assertEqual(result['eligible_method_ids'], ['M-BEHAVIOUR-RECORDS'])
        self.assertEqual(result['human_decision_state'], 'pending')
        self.assertTrue(all(v['rule_version'] == 'v1' for v in result['quality_observations']))
        self.assertNotIn('SENTINEL_SOURCE', f.encoded(result).decode())
        self.assertNotIn('gmv_value', result)

    def test_A06_A07_negative_and_unknown_prerequisites(self):
        snapshot = self.snapshot()
        for intent in ('gmv', 'strict_funnel'):
            question = dict(self.question, intent=intent, requested_unit=f.UNITS[intent])
            result = f.diagnose(question, snapshot, r.registered_rules())
            self.assertEqual(result['capability'], 'unsupported')
            self.assertEqual(result['eligible_method_ids'], [])
        unknown = deepcopy(snapshot)
        unknown['metric_refs'].pop('behaviours')
        self.assertEqual(f.diagnose(self.question, unknown, r.registered_rules())['capability'], 'conditional')
        unknown['reading_schema'] = []
        self.assertEqual(f.diagnose(self.question, unknown, r.registered_rules())['capability'], 'unsupported')

    def test_A09_stable_and_closed_rules(self):
        snapshot = self.snapshot()
        self.assertEqual(f.diagnose(self.question, snapshot, r.registered_rules()),
                         f.diagnose(self.question, snapshot, r.registered_rules()))
        with self.assertRaises(ValueError):
            f.diagnose(self.question, snapshot, dict(r.registered_rules(), rule_ids=['UNKNOWN']))

    def test_A10_decision_gate(self):
        diagnosis = f.diagnose(self.question, self.snapshot(), r.registered_rules())
        for decision in ('accept', 'request_data', 'reject', 'cancel'):
            f.decision_check({'decision': decision, 'actor': 'user', 'confirmed_at': f.now()}, diagnosis)
        for capability in ('conditional', 'unsupported'):
            with self.assertRaises(f.BoundaryError):
                f.decision_check({'decision': 'accept', 'actor': 'user', 'confirmed_at': f.now()},
                                 dict(diagnosis, capability=capability))
        for actor, time in (('', f.now()), ('user', ''), ('user', '2026-01-01')):
            with self.assertRaises(f.BoundaryError):
                f.decision_check({'decision': 'accept', 'actor': actor, 'confirmed_at': time}, diagnosis)

    def test_A11_restored_diagnosis_and_changed_question(self):
        diagnosis, directory = self.completed_diagnosis()
        self.assertEqual(f.load_diagnosis(directory / 'diagnosis.json')[0], diagnosis)
        (self.work / 'question.json').write_bytes(f.encoded(dict(self.question, question_version='v2')))
        with self.assertRaises(f.BoundaryError):
            f.load_diagnosis(directory / 'diagnosis.json')

    def test_A11_independent_decision_record(self):
        diagnosis, directory = self.completed_diagnosis()
        before = f.read_bytes(directory / 'diagnosis.json')
        output = f.OUTPUT / (directory.name + '-decision')
        receipt = f.record_s2_decision(diagnosis,
            {'decision': 'cancel', 'actor': 'controlled_test_actor', 'confirmed_at': f.now()}, output)
        self.assertEqual(receipt['acceptance_scope'], 'S2_only')
        self.assertEqual(f.read_bytes(directory / 'diagnosis.json'), before)
        self.assertFalse((output / 'final-status.json').exists())

    def test_A12_publication_failure_keeps_tmp_not_success(self):
        directory = f.new_run(f.OUTPUT / (self.batch.name + '-' + self._testMethodName))
        terminal = {'status': 'success'}
        with patch.object(Path, 'rename', side_effect=OSError('controlled')):
            with self.assertRaises(OSError):
                f.publish(directory, terminal)
        self.assertFalse((directory / 'final-status.json').exists())
        self.assertTrue((directory / 'final-status-success.tmp').exists())

    def test_A13_no_source_open_or_sql_execution(self):
        original = Path.open
        opened = []
        def observed(path, *args, **kwargs):
            opened.append(str(path))
            self.assertNotIn('SENTINEL', str(path))
            self.assertNotEqual(path.suffix.lower(), '.csv')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'open', observed):
            result = f.diagnose(self.question, self.snapshot(), r.registered_rules())
        put(self.batch / (self._testMethodName + '-reads.json'), {'opened_paths': opened,
            'scope': 'controlled adapter calls only', 'product_model_usage': 'not_applicable'})
        self.assertEqual(result['capability'], 'supported')

    def test_A12_cli_normal_and_each_finalization_failure(self):
        snapshot = self.snapshot()
        phases = (None, 'diagnosis.json', 'input-manifest.json', 'reference-check.json',
                  'environment.json', 'network-observation.json', 'cli-command.json', 'publication')
        for index, fault in enumerate(phases):
            directory = f.OUTPUT / (self.batch.name + '-cli-' + str(index))
            argv = ['diagnose', '--output-dir', str(directory)]
            original_save = f.save
            def guarded_save(path, value):
                if path.name == fault:
                    raise OSError('controlled_write_fault')
                return original_save(path, value)
            with ExitStack() as stack:
                stack.enter_context(patch.object(f, 'load_accepted_profile', return_value=deepcopy(snapshot)))
                stack.enter_context(patch.object(f, 'environment', return_value={'controlled': True}))
                stack.enter_context(patch.object(f, 'save', side_effect=guarded_save))
                if fault == 'publication':
                    stack.enter_context(patch.object(f, 'publish', side_effect=OSError('controlled_publication_fault')))
                stdout = stack.enter_context(patch('sys.stdout', new_callable=io.StringIO))
                exit_status = f.main(argv)
            terminal = f.parse(f.read_bytes(directory / 'final-status.json')) if (directory / 'final-status.json').exists() else None
            self.assertEqual(exit_status, 0 if fault is None else 2)
            self.assertEqual(terminal['status'] if terminal else None,
                             'success' if fault is None else None if fault == 'publication' else 'failed')
            put(self.batch / ('cli-finalization-' + str(index) + '.json'),
                {'argv': argv, 'exit_status': exit_status, 'stdout': stdout.getvalue(),
                 'fault': fault, 'terminal': terminal, 'scope': 'controlled mocked CLI; not production'})

    def test_A11_binding_changes_and_receipt_restore(self):
        diagnosis, directory = self.completed_diagnosis()
        receipt_dir = f.OUTPUT / (directory.name + '-receipt')
        receipt = f.record_s2_decision(diagnosis, {'decision': 'reject', 'actor': 'controlled_test_actor',
                                                 'confirmed_at': f.now()}, receipt_dir)
        for name in f.REQUIRED[2:]:
            f.save(receipt_dir / name, {'controlled': True})
        f.publish(receipt_dir, {'schema_version': '1.0', 'run_id': receipt_dir.name, 'command': 'decide',
            'status': 'success', 'exit_status': 0, 'completed_at': f.now(), 'required_evidence_refs': list(f.REQUIRED)})
        self.assertEqual(f.verify_decision(receipt_dir / 'decision.json'), receipt)
        changed_rules = dict(r.registered_rules(), ruleset_version='v2')
        with patch.object(r, 'registered_rules', return_value=changed_rules):
            with self.assertRaises((f.BoundaryError, ValueError)):
                f.load_diagnosis(directory / 'diagnosis.json')
        self.mutate('profile.json', lambda v: v.update(dataset_version='1' * 64))
        with self.assertRaises(f.BoundaryError):
            f.verify_decision(receipt_dir / 'decision.json')

    def test_A12_decide_cli_and_failure_preserve_diagnosis(self):
        diagnosis, source = self.completed_diagnosis()
        original = f.read_bytes(source / 'diagnosis.json')
        for index, fault in enumerate((None, 'decision.json', 'input-manifest.json', 'reference-check.json',
                                       'environment.json', 'network-observation.json', 'cli-command.json')):
            directory = f.OUTPUT / (source.name + '-cli-decide-' + str(index))
            argv = ['decide', '--diagnosis', str(source / 'diagnosis.json'), '--decision', 'cancel',
                    '--actor', 'controlled_test_actor', '--confirmed-at', f.now(), '--output-dir', str(directory)]
            original_save = f.save
            def guarded(path, value):
                if path.name == fault:
                    raise OSError('controlled')
                return original_save(path, value)
            with patch.object(f, 'environment', return_value={'controlled': True}), \
                    patch.object(f, 'save', side_effect=guarded), \
                    patch('sys.stdout', new_callable=io.StringIO) as stdout:
                status = f.main(argv)
            self.assertEqual(status, 0 if fault is None else 2)
            terminal = f.parse(f.read_bytes(directory / 'final-status.json'))
            self.assertEqual(terminal['status'], 'success' if fault is None else 'failed')
            self.assertEqual(f.read_bytes(source / 'diagnosis.json'), original)
            put(self.batch / ('decide-fault-' + str(index) + '.json'),
                {'argv': argv, 'exit_status': status, 'stdout': stdout.getvalue(), 'terminal': terminal})

    def test_A02_reparse_and_wrong_types(self):
        import stat
        from types import SimpleNamespace
        original = Path.lstat
        def reparse(path, *args, **kwargs):
            if path == self.work:
                return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
            return original(path, *args, **kwargs)
        with patch.object(Path, 'lstat', reparse), patch.object(Path, 'open', side_effect=AssertionError('opened')):
            with self.assertRaises(f.BoundaryError):
                f.read_bytes(self.package / 'profile.json')
        for value in (True, -1, '0', 0.0):
            with self.assertRaises(f.BoundaryError):
                f.result_check('summary', [{'row_count': value}])

    def test_A11_binding_field_mutations(self):
        diagnosis, directory = self.completed_diagnosis()
        for key, value in (('run_id', 'different'), ('dataset_version', '2' * 64),
                           ('input_manifest_hash', '2' * 64), ('question_hash', '2' * 64),
                           ('question_version', 'v2'), ('ruleset_hash', '2' * 64)):
            changed = dict(diagnosis, **{key: value})
            with patch.object(f, 'read_bytes', wraps=f.read_bytes) as reader:
                original_reader = reader._mock_wraps
                def read(path, root=f.ROOT):
                    return f.encoded(changed) if path == directory / 'diagnosis.json' else original_reader(path, root)
                reader.side_effect = read
                with self.assertRaises(f.BoundaryError):
                    f.load_diagnosis(directory / 'diagnosis.json')

    def test_R2_independent_binding_cases(self):
        cases = ('contract-digest-mismatch', 'contract-version-mismatch', 'missing-result',
                 'missing-evidence', 'evidence-run-mismatch', 'evidence-dataset-mismatch',
                 'evidence-reference-mismatch')
        for case in cases:
            root = self.work / case
            contract = root / 'read-contract.json'
            put(contract, f.read_bytes(f.CONTRACT))
            with patch.object(f, 'CONTRACT', contract):
                baseline_package = fixture(root / 'baseline')
                baseline = f.load_accepted_profile(baseline_package / 'profile.json',
                                                   baseline_package / 'fixture-acceptance.json')
                missing = {'missing-result': ('summary-result.json',),
                           'missing-evidence': ('summary-evidence.json',)}.get(case, ())
                package = fixture(root, omit=missing, probes=True)
                expected = 'evidence_reference_mismatch'
                changed_key = None
                if case == 'contract-version-mismatch':
                    path, changed_key, value = contract, 'version', 'unknown'
                    expected = 'read_contract_mismatch'
                elif case == 'contract-digest-mismatch':
                    path, changed_key, value = package / 'summary-evidence.json', 'read_config_sha256', '0' * 64
                elif case == 'evidence-run-mismatch':
                    path, changed_key, value = package / 'summary-evidence.json', 'run_id', 'different'
                elif case == 'evidence-dataset-mismatch':
                    path, changed_key, value = package / 'summary-evidence.json', 'dataset_version', '0' * 64
                elif case == 'evidence-reference-mismatch':
                    path, changed_key, value = package / 'profile.json', 'metrics.summary.evidence_id', 'different'
                else:
                    expected = 'file_missing_or_size_boundary'
                if changed_key:
                    document = f.parse(path.read_bytes())
                    if changed_key == 'metrics.summary.evidence_id':
                        document['metrics']['summary']['evidence_id'] = value
                    else:
                        document[changed_key] = value
                    path.write_bytes(f.encoded(document))
                fixture_manifest(root, 'R2:' + case)
                actual = None
                with observed_calls(case):
                    try:
                        f.load_accepted_profile(package / 'profile.json', package / 'fixture-acceptance.json')
                    except f.BoundaryError as error:
                        actual = str(error)
                CASE_RESULTS.append({'group': 'R2', 'case_id': case, 'input': f.relative(package),
                    'baseline': baseline, 'changed_key': changed_key, 'omitted': list(missing),
                    'patches': ['CONTRACT: independent copy', 'FIXTURE: current test scratch'],
                    'expected': expected, 'actual': actual, 'matches': expected == actual})
                self.assertEqual(actual, expected)

    def test_R3_real_publication_matrix(self):
        original_load = f.load_accepted_profile
        self.package = fixture(self.work / 'source-probes', probes=True)
        source_diagnosis, source = self.completed_diagnosis()
        source_before = f.digest(f.read_bytes(source / 'diagnosis.json'))
        for command in ('diagnose', 'decide'):
            for case in ('normal', 'tmp-open', 'tmp-write', 'tmp-flush', 'tmp-fsync', 'tmp-rename'):
                target = f.OUTPUT / (self.batch.name + '-' + self._testMethodName + '-' + command + '-' + case)
                argv = [command, '--output-dir', str(target)]
                if command == 'decide':
                    argv += ['--diagnosis', str(source / 'diagnosis.json'), '--decision', 'cancel',
                             '--actor', 'controlled_test_actor', '--confirmed-at', f.now()]
                stdout, stderr = io.StringIO(), io.StringIO()
                snapshot = self.snapshot()
                probes_package = fixture(self.work / (command + '-' + case), probes=True)
                snapshot = f.load_accepted_profile(probes_package / 'profile.json',
                                                   probes_package / 'fixture-acceptance.json')
                events = []
                escaped = None
                with patch.object(f, 'load_accepted_profile', side_effect=lambda p, a: deepcopy(snapshot)
                         if p == f.LEGACY else original_load(p, a)), \
                        publication_fault(target, case, events), observed_calls(command + ':' + case), \
                        redirect_stdout(stdout), redirect_stderr(stderr):
                    try:
                        status = f.main(argv)
                    except Exception as error:
                        status, escaped = None, type(error).__name__
                terminal = f.parse(f.read_bytes(target / 'final-status.json')) if (target / 'final-status.json').exists() else None
                remnants = [f.relative(p) for p in target.iterdir() if p.suffix == '.tmp'] if target.exists() else []
                source_after = f.digest(f.read_bytes(source / 'diagnosis.json'))
                calculation = f.parse(f.read_bytes(target / 'diagnosis.json'))['status'] if (target / 'diagnosis.json').exists() else None
                receipt_available = (target / 'decision.json').is_file()
                record = {'command': command, 'case_id': case, 'argv': argv, 'exit_status': status,
                    'stdout': stdout.getvalue(), 'stderr': stderr.getvalue(), 'terminal': terminal,
                    'injection_events': events, 'exception_type': escaped, 'calculation_status': calculation,
                    'receipt_available': receipt_available, 'source_before': source_before, 'source_after': source_after,
                    'tmp_remaining': remnants, 'output_dir': f.relative(target),
                    'scope': 'synthetic same-process CLI; real main/publish; fixed input adapter substitution'}
                PUBLICATION_RESULTS.append(record)
                PRODUCT_STREAMS.append({'id': command + ':' + case, 'stdout': stdout.getvalue(), 'stderr': stderr.getvalue()})
                self.assertIsNone(escaped)
                self.assertEqual(source_before, source_after)
                self.assertEqual(status, 0 if case == 'normal' else 2)
                if case == 'normal':
                    self.assertEqual(terminal['status'], 'success')
                else:
                    self.assertIsNone(terminal)
                    self.assertGreaterEqual(len(events), 2)
                    self.assertFalse(json.loads(stdout.getvalue())['failure_evidence_persisted'])

    def test_A14_existing_output_unchanged(self):
        directory = f.new_run(f.OUTPUT / (self.batch.name + '-' + self._testMethodName))
        f.save(directory / 'marker.json', {'retain': True})
        before = f.read_bytes(directory / 'marker.json')
        with self.assertRaises(f.BoundaryError):
            f.new_run(directory)
        self.assertEqual(f.read_bytes(directory / 'marker.json'), before)


@contextmanager
def observed_calls(case):
    original = Path.open
    def opened(path, *args, **kwargs):
        mode = args[0] if args else kwargs.get('mode', 'r')
        READ_EVENTS.append({'case_id': case, 'path': f.relative(path) if f.ROOT in path.parents else str(path), 'mode': mode})
        if path.suffix.lower() == '.csv' or any(v in str(path) for v in MARKERS.values()):
            raise AssertionError('forbidden_source_open')
        return original(path, *args, **kwargs)
    original_import = builtins.__import__
    def imported(name, *args, **kwargs):
        if name.split('.')[0] in ('duckdb', 'openai', 'anthropic', 'deepseek'):
            READ_EVENTS.append({'case_id': case, 'blocked_import': name})
            raise AssertionError('forbidden_engine_or_model_import')
        return original_import(name, *args, **kwargs)
    with ExitStack() as stack:
        engine = sys.modules.get('duckdb')
        if engine is not None:
            for name in ('connect', 'execute', 'sql', 'query'):
                if hasattr(engine, name):
                    stack.enter_context(patch.object(engine, name, side_effect=AssertionError('engine_call')))
        with patch.object(builtins, '__import__', imported), patch.object(Path, 'open', opened), \
                patch.object(socket.socket, 'connect', side_effect=AssertionError('network_call')), \
                patch.object(socket, 'getaddrinfo', side_effect=AssertionError('network_resolution')):
            yield


@contextmanager
def publication_fault(target, case, events):
    original_open, original_rename, original_fsync = Path.open, Path.rename, os.fsync
    descriptors = {}
    def matches(path):
        return path.parent == target and path.name in ('final-status-success.tmp', 'final-status-failed.tmp')
    def hit(operation, path):
        events.append({'operation': operation, 'path': f.relative(path)})
        raise OSError('controlled_publication_fault')
    class Stream:
        def __init__(self, stream, path):
            self.stream, self.path = stream, path
        def __enter__(self):
            self.stream.__enter__()
            descriptors[self.stream.fileno()] = self.path
            return self
        def __exit__(self, *args):
            descriptors.pop(self.stream.fileno(), None)
            return self.stream.__exit__(*args)
        def write(self, data):
            if case == 'tmp-write':
                hit('write', self.path)
            return self.stream.write(data)
        def flush(self):
            if case == 'tmp-flush':
                hit('flush', self.path)
            return self.stream.flush()
        def fileno(self):
            return self.stream.fileno()
        def __getattr__(self, name):
            return getattr(self.stream, name)
    def opened(path, *args, **kwargs):
        if matches(path) and case == 'tmp-open':
            hit('open', path)
        stream = original_open(path, *args, **kwargs)
        return Stream(stream, path) if matches(path) else stream
    def renamed(path, dest):
        if matches(path) and case == 'tmp-rename':
            hit('rename', path)
        return original_rename(path, dest)
    def synced(fd):
        if fd in descriptors and case == 'tmp-fsync':
            hit('fsync', descriptors[fd])
        return original_fsync(fd)
    with patch.object(Path, 'open', opened), patch.object(Path, 'rename', renamed), patch.object(os, 'fsync', synced):
        yield


def bounded_inventory(roots):
    items = []
    def visit(path, category):
        f.path_check(path, f.ROOT)
        if path.is_dir():
            for child in sorted(path.iterdir()):
                visit(child, category)
        else:
            if category in ('historical_profile_diagnosis', 'real_s2_decision') and path.suffix != '.json':
                raise RuntimeError('unexpected_real_run_file')
            if path.suffix not in ('.json', '.log', '.tmp', '.py'):
                raise RuntimeError('unknown_inventory_file_family')
            if path.suffix == '.py' and path.name != 'test_w2a.py':
                raise RuntimeError('unexpected_source_snapshot')
            payload = path.read_bytes()
            items.append({'path': f.relative(path), 'category': category,
                          'size': len(payload), 'sha256': f.digest(payload)})
    for root, category in roots:
        visit(root, category)
    return items


def supplement():
    global ACTIVE_BATCH
    env = f.environment()
    if Path.cwd() != f.ROOT:
        raise RuntimeError('project_cwd_required')
    batch = f.new_run(f.OUTPUT / ('r1r4-' + uuid.uuid4().hex))
    ACTIVE_BATCH = batch
    os.environ['W2A_TEST_RUN'] = str(batch)
    started = f.now()
    old_prefix = 'syn-3178ad8b677e49edb91de623be0c3905'
    old_roots = []
    for path in sorted(f.OUTPUT.iterdir()):
        if path.name == old_prefix or path.name.startswith(old_prefix + '-'):
            old_roots.append((path, 'old_synthetic'))
        elif path.name == 'local-' + old_prefix:
            old_roots.append((path, 'historical_profile_diagnosis'))
        elif path.name == 's2-accept-3178ad8b677e49edb91de623be0c3905':
            old_roots.append((path, 'real_s2_decision'))
    protected = [f.ROOT / name for name in ('src/datainsight/feasibility.py',
        'src/datainsight/feasibility_rules.py', 'docs/acceptance/W2-A-v1.md',
        'docs/decisions/ADR-003-directory-and-evidence-layout.md',
        'configs/w1b-read-contract-v1.json', 'configs/w2a-question-v1.json')]
    def protection():
        return bounded_inventory(old_roots) + [
            {'path': f.relative(p), 'sha256': f.digest(f.read_bytes(p)), 'category': 'protected_source'}
            for p in protected]
    before = protection()
    put(batch / 'protected-files-before.json', before)
    source = f.path_check(Path(__file__).absolute(), f.ROOT / 'tests')
    payload = source.read_bytes()
    put(batch / 'source-snapshots/test_w2a.py', payload)
    put(batch / 'batch-source-identity.json', {'python_version': sys.version,
        'test_source_sha256': f.digest(payload), 'old_test_snapshot': 'unknown'})
    shell = "cd /d/MyPythonProjects/datainsight && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH='D:\\MyPythonProjects\\datainsight\\src;D:\\MyPythonProjects\\datainsight\\tests' TEMP='D:\\MyPythonProjects\\datainsight\\.cache\\tmp' TMP='D:\\MyPythonProjects\\datainsight\\.cache\\tmp' TMPDIR='D:\\MyPythonProjects\\datainsight\\.cache\\tmp' .venv/Scripts/python.exe -B -m test_w2a --w2a-supplement"
    put(batch / 'batch-command.json', {'argv': sys.argv, 'executable': sys.executable,
        'shell_transcript': shell, 'cwd': str(Path.cwd()), 'batch_id': batch.name})
    put(batch / 'batch-environment.json', env)
    log = io.StringIO()
    names = ['test_w2a', 'test_w1b_profile.ProfileReferenceTests.test_unknown_template_before_connection',
             'test_w1b_profile.ProfileReferenceTests.test_result_boundaries_and_nested_types']
    suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(W2ATests),
        unittest.defaultTestLoader.loadTestsFromNames(names[1:])])
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    put(batch / 'test.log', log.getvalue().encode('utf-8'))
    put(batch / 'case-results.json', CASE_RESULTS)
    put(batch / 'r3-publication-results.json', PUBLICATION_RESULTS)
    put(batch / 'r4-read-observation.json', {'events': READ_EVENTS,
        'scope': 'R2/R3 Path.open and socket connect/getaddrinfo wrappers; not system isolation',
        'model_sql_engine_observation': 'provider/engine imports blocked in R2/R3; loaded DuckDB connect/execute/sql/query patched to reject; socket calls rejected; no universal Python execution monitor',
        'unobserved': 'existing tests outside R2/R3 wrappers; no system/native isolation'})
    after = protection()
    put(batch / 'protected-files-after.json', after)
    new_roots = [(batch, 'new_synthetic')]
    new_roots += [(p, 'new_synthetic') for p in sorted(f.OUTPUT.iterdir()) if p.name.startswith(batch.name + '-')]
    scratch = f.ROOT / 'outputs/_scratch' / batch.name
    if scratch.exists():
        new_roots.append((scratch, 'fixture_input'))
    inventory = bounded_inventory(old_roots + new_roots)
    findings, exclusions, scanned = [], [], []
    for item in inventory:
        path = f.ROOT / item['path']
        if item['category'] == 'fixture_input' or 'source-snapshots/' in item['path']:
            exclusions.append({'path': item['path'], 'reason': 'intentional_fixture or test_source'})
            continue
        scanned.append(item['path'])
        data = path.read_bytes()
        for marker_id, value in MARKERS.items():
            count = data.count(value.encode())
            if count:
                findings.append({'marker_id': marker_id, 'path': item['path'], 'count': count})
    for stream in PRODUCT_STREAMS:
        for channel in ('stdout', 'stderr'):
            for marker_id, value in MARKERS.items():
                count = stream[channel].count(value)
                if count:
                    findings.append({'marker_id': marker_id, 'stream': stream['id'] + ':' + channel, 'count': count})
    put(batch / 'r4-privacy-scan.json', {'scanned_files': scanned,
        'scanned_streams': [v['id'] for v in PRODUCT_STREAMS], 'exclusions': exclusions,
        'findings': findings, 'trace_scope': 'no separate product trace exists'})
    put(batch / 'artifact-inventory.json', {'files': inventory,
        'excluded_self_reports': ['artifact-inventory.json', 'r4-privacy-scan.json', 'batch-result.json', 'batch-status.json'],
        'reason': 'self-referential report; final coverage check below'})
    # A missing observation is failure, not a silently waived requirement.
    reports_complete = len(CASE_RESULTS) == 10 and len(PUBLICATION_RESULTS) == 12
    observations_complete = bool(READ_EVENTS) and not any('blocked_import' in v for v in READ_EVENTS)
    success = result.wasSuccessful() and before == after and not findings and reports_complete and observations_complete
    status = 0 if success else 2
    final_inventory = bounded_inventory(old_roots + new_roots)
    covered = {v['path'] for v in inventory}
    allowed = {f.relative(batch / name) for name in
               ('artifact-inventory.json', 'r4-privacy-scan.json', 'batch-result.json')}
    missing = {v['path'] for v in final_inventory} - covered - allowed
    status = 0 if success and not missing else 2
    put(batch / 'batch-result.json', {'tests_run': result.testsRun, 'failures': len(result.failures),
        'errors': len(result.errors), 'exit_status': status, 'reports_complete': reports_complete,
        'observations_complete': observations_complete, 'uncovered_paths': sorted(missing),
        'final_acceptance': 'not_performed'})
    put(batch / 'batch-status.json', {'status': 'success' if success and not missing else 'failed',
        'exit_status': status, 'started_at': started, 'completed_at': f.now(),
        'uncovered_paths': sorted(missing), 'self_exclusion': 'batch-status.json',
        'final_acceptance': 'not_performed'})
    print(json.dumps({'batch': str(batch), 'exit_status': status}))
    return status


if __name__ == '__main__':
    if sys.argv[1:] == ['--w2a-supplement']:
        try:
            exit_status = supplement()
        except Exception as error:
            persisted = False
            if ACTIVE_BATCH is not None:
                try:
                    target = ACTIVE_BATCH / 'batch-status.json'
                    if not target.exists():
                        put(target, {'status': 'failed', 'exit_status': 2,
                            'exception_type': type(error).__name__, 'completed_at': f.now(),
                            'reports_complete': False, 'final_acceptance': 'not_performed'})
                        persisted = True
                except Exception:
                    pass
            print(json.dumps({'status': 'failed', 'exit_status': 2,
                'exception_type': type(error).__name__, 'failure_evidence_persisted': persisted}))
            exit_status = 2
        raise SystemExit(exit_status)
    unittest.main()
