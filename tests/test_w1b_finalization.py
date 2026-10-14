"""B09 terminal-state tests using synthetic CSV and controlled failures only."""
from contextlib import ExitStack
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from datainsight import profile as p
from datainsight import __main__ as cli
from datainsight.inspection import AccessPolicy, SourceRequest, validate_source, BoundaryError
from w1b_reference import generate


def exercise_finalization(root):
    """Retain actual CLI artifacts for every controlled scenario, not raw rows."""
    with tempfile.TemporaryDirectory(dir=p.ROOT / 'tests/fixtures') as fixture:
        path = Path(fixture) / 'synthetic.csv'
        generate(path)
        source = validate_source(SourceRequest('synthetic', path, 'file', 'fixture'),
            AccessPolicy((), p.ROOT / 'tests/fixtures', p.ROOT / 'outputs/W1-B'))
        original = root / 'synthetic-original'
        p.run_profile(source, p.load_read_contract(), original)
        observed = []
        for command in ('profile', 'replay'):
            for fault in ('none', 'reference_verification', 'reference-check.json',
                          'environment.json', 'network-observation.json', 'cli-command.json',
                          'final_status_publication'):
                target = root / (command + '-' + fault.replace('.json', ''))
                argv = ['datainsight', command, '--output-dir', str(target)]
                if command == 'profile':
                    argv += ['--source', 'textbook_userbehavior']
                else:
                    argv += ['--evidence', str(original / 'summary-evidence.json')]
                real_save = p.save_profile_json
                real_fsync = cli.os.fsync
                real_publish = cli.publish_final_status
                publication_attempts = []

                def save(output, data):
                    if output.name == fault:
                        raise OSError('controlled_sensitive_exception_not_for_logs')
                    return real_save(output, data)

                def publish(directory, data):
                    publication_attempts.append(data['status'])
                    if data['status'] == 'success':
                        for name in ('reference-check.json', 'environment.json',
                                     'network-observation.json', 'cli-command.json'):
                            if not (directory / name).is_file():
                                raise AssertionError('Success published before required evidence')
                        calculation = p.read_evidence_json(directory / ('profile.json' if command == 'profile' else 'replay.json'))
                        if calculation['status'] != 'computed_pending_finalization':
                            raise AssertionError('Computation published success prematurely')
                        if (directory / 'final-status.json').exists():
                            raise AssertionError('Terminal state already exists')
                    return real_publish(directory, data)

                def fsync(handle):
                    if fault == 'final_status_publication' and publication_attempts[-1] == 'success':
                        raise OSError('controlled_final_status_write_failure')
                    return real_fsync(handle)

                with ExitStack() as patches:
                    patches.enter_context(patch.object(cli, 'PRODUCTION', path))
                    patches.enter_context(patch('sys.argv', argv))
                    output = patches.enter_context(patch('sys.stdout', new_callable=io.StringIO))
                    patches.enter_context(patch.object(p, 'save_profile_json', side_effect=save))
                    patches.enter_context(patch.object(cli, 'publish_final_status', side_effect=publish))
                    patches.enter_context(patch.object(cli.os, 'fsync', side_effect=fsync))
                    if fault == 'reference_verification':
                        patches.enter_context(patch.object(p, 'verify_profile_references',
                            side_effect=BoundaryError('controlled_reference_failure')))
                    exit_status = cli.main()
                    stdout = output.getvalue()
                with (target / 'observed-cli-output.json').open('x', encoding='utf-8') as stream:
                    json.dump({'argv': argv, 'exit_status': exit_status, 'stdout': json.loads(stdout)}, stream, indent=2)
                terminal = p.read_evidence_json(target / 'final-status.json')
                calculation = p.read_evidence_json(target / ('profile.json' if command == 'profile' else 'replay.json'))
                observed.append({'command': command, 'fault': fault, 'output_dir': str(target),
                    'exit_status': exit_status, 'stdout': json.loads(stdout),
                    'terminal': terminal, 'calculation_status': calculation['status'],
                    'publication_attempts': list(publication_attempts)})
        return observed


class FinalizationTests(unittest.TestCase):
    def test_profile_and_replay_terminal_states_follow_required_evidence(self):
        with tempfile.TemporaryDirectory(dir=p.ROOT / 'outputs/W1-B') as directory:
            observed = exercise_finalization(Path(directory))
            for case in observed:
                with self.subTest(command=case['command'], fault=case['fault']):
                    success = case['fault'] == 'none'
                    expected_status = 'success' if success else 'failed'
                    expected_exit = 0 if success else 2
                    self.assertEqual(case['exit_status'], expected_exit)
                    self.assertEqual(case['terminal']['exit_status'], expected_exit)
                    self.assertEqual(case['terminal']['status'], expected_status)
                    self.assertEqual(case['stdout']['status'], expected_status)
                    self.assertEqual(case['calculation_status'], 'computed_pending_finalization')
                    self.assertNotIn('controlled_sensitive_exception', json.dumps(case))
                    if success:
                        target = Path(case['output_dir'])
                        for ref in case['terminal']['required_evidence_refs']:
                            self.assertTrue((target / ref).is_file())
                        cmd = p.read_evidence_json(target / 'cli-command.json')
                        file, key = cmd['exit_status_ref'].split('#')
                        self.assertEqual(p.read_evidence_json(target / file)[key], expected_exit)
                        self.assertEqual(case['publication_attempts'], ['success'])
                    else:
                        self.assertTrue(case['stdout']['failure_evidence_persisted'])
                        self.assertIn('reason_code', case['terminal'])
                        self.assertEqual(case['publication_attempts'][-1], 'failed')
                        if case['fault'] != 'final_status_publication':
                            self.assertNotIn('success', case['publication_attempts'])

    def test_existing_output_is_not_changed_on_cli_failure(self):
        with tempfile.TemporaryDirectory(dir=p.ROOT / 'outputs/W1-B') as directory:
            target = Path(directory)
            p.save_profile_json(target / 'final-status.json', {'status': 'success', 'exit_status': 0})
            original = (target / 'final-status.json').read_bytes()
            with patch('sys.argv', ['datainsight', 'replay', '--evidence', str(p.ROOT / 'unapproved.json'), '--output-dir', directory]), patch('sys.stdout', new_callable=io.StringIO):
                self.assertEqual(cli.main(), 2)
            self.assertEqual((target / 'final-status.json').read_bytes(), original)

    def test_unwritable_terminal_record_does_not_leave_success_artifacts(self):
        with tempfile.TemporaryDirectory(dir=p.ROOT / 'outputs/W1-B') as directory, tempfile.TemporaryDirectory(dir=p.ROOT / 'tests/fixtures') as fixture:
            source_path = Path(fixture) / 'synthetic.csv'
            generate(source_path)
            target = Path(directory) / 'unwritable'
            with patch.object(cli, 'PRODUCTION', source_path), patch.object(cli, 'publish_final_status', side_effect=OSError('controlled_unwritable')), patch('sys.argv', ['datainsight', 'profile', '--source', 'textbook_userbehavior', '--output-dir', str(target)]), patch('sys.stdout', new_callable=io.StringIO) as stdout:
                self.assertEqual(cli.main(), 2)
            self.assertFalse((target / 'final-status.json').exists())
            self.assertEqual(p.read_evidence_json(target / 'profile.json')['status'], 'computed_pending_finalization')
            self.assertFalse(json.loads(stdout.getvalue())['failure_evidence_persisted'])
