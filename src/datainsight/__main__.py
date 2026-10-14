"""Fixed-policy W1-A CLI. Network guard covers this Python process only."""
import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import sys
import tempfile
import uuid
from .inspection import (AccessPolicy, SourceRequest, InspectionReport, BoundaryError,
    validate_source, inspect_file, fingerprint_file, write_inspection, output_target,
    check_components, normalized, now)

ROOT = Path(__file__).resolve().parents[2]
PRODUCTION = Path('D:/大数据项目/电商用户行为分析/第9章/UserBehavior.csv')
POLICY = AccessPolicy((PRODUCTION,), ROOT / 'tests/fixtures', ROOT / 'outputs/W1-A')


def save(name, data, directory):
    p = output_target(directory / name, POLICY)
    with p.open('x', encoding='utf-8') as stream:
        json.dump(data, stream, ensure_ascii=True, indent=2)
        stream.write('\n')


def read_config():
    # Fixed path only; configuration is data, never an authority source.
    path = normalized(ROOT / 'configs/w1a-source.json')
    check_components(path)
    return json.loads(path.read_text(encoding='utf-8'))


def publish_final_status(directory, data):
    from . import profile as p
    target = output_target(directory / 'final-status.json', p.OUTPUT_POLICY)
    # Same-directory rename publishes only a completely written terminal record.
    staging = output_target(directory / ('final-status-' + data['status'] + '.tmp'), p.OUTPUT_POLICY)
    with staging.open('xb') as stream:
        stream.write(p.json_bytes(data))
        stream.flush()
        os.fsync(stream.fileno())
    output_target(target, p.OUTPUT_POLICY)
    staging.rename(target)


def profile_entry(args, attempts):
    from . import profile as p
    directory = args.output_dir
    owned_directory = False
    phase = 'preflight'
    try:
        directory = normalized(directory)
        if not p.inside(directory, p.OUTPUT_POLICY.output_root) or directory == p.OUTPUT_POLICY.output_root:
            raise BoundaryError('output_outside_policy')
        check_components(directory)
        if directory.exists():
            raise BoundaryError('output_exists')
        owned_directory = True
        phase = 'computation'
        if args.command == 'profile':
            source = validate_source(SourceRequest('textbook_userbehavior', PRODUCTION, 'file',
                'configs/w1b-read-contract-v1.json'), AccessPolicy((PRODUCTION,), ROOT / 'tests/fixtures', ROOT / 'outputs/W1-B'))
            result = p.run_profile(source, p.load_read_contract(), directory)
        else:
            result = p.replay_profile_evidence(args.evidence, directory)
        if result.status != 'computed_pending_finalization':
            raise BoundaryError('unexpected_computation_status')
        phase = 'reference_verification'
        references = p.verify_profile_references(directory)
        p.save_profile_json(directory / 'reference-check.json', references)
        phase = 'environment_evidence'
        p.save_profile_json(directory / 'environment.json', {'executable': sys.executable,
            'python_version': sys.version, 'duckdb_version': p.duckdb.__version__,
            'duckdb_module': p.duckdb.__file__, 'temp_directory': tempfile.gettempdir(),
            'variables': {key: os.environ.get(key) for key in ('TEMP','TMP','TMPDIR','PYTHONPATH','PYTHONDONTWRITEBYTECODE')},
            'product_model_usage': 'not_applicable'})
        phase = 'network_evidence'
        p.save_profile_json(directory / 'network-observation.json', {'blocked_events': attempts,
            'scope': 'CLI Python audit events only; not DuckDB native or system isolation',
            'templates': 'local CSV only; automatic extension installation/loading disabled'})
        phase = 'command_evidence'
        p.save_profile_json(directory / 'cli-command.json', {'argv': sys.argv,
            'status': 'computed_pending_finalization', 'exit_status': None,
            'exit_status_ref': 'final-status.json#exit_status'})
        phase = 'final_status_publication'
        publish_final_status(directory, {'run_id': directory.name, 'command': args.command,
            'status': 'success', 'exit_status': 0, 'completed_at': now(),
            'required_evidence_refs': ['reference-check.json', 'environment.json',
                'network-observation.json', 'cli-command.json']})
    except (BoundaryError, OSError, ValueError, KeyError, TypeError):
        failure_persisted = False
        if owned_directory and directory.is_dir():
            try:
                publish_final_status(directory, {'run_id': directory.name, 'command': args.command,
                    'status': 'failed', 'exit_status': 2, 'failed_at': now(), 'phase': phase,
                    'reason_code': 'controlled_profile_operation_failed'})
                failure_persisted = True
            except (BoundaryError, OSError, ValueError, KeyError, TypeError):
                # An unwritable directory cannot publish either terminal state.
                # Computation artifacts remain explicitly pending, never success.
                pass
        print(json.dumps({'status': 'failed', 'reason_code': 'controlled_profile_operation_failed',
                          'failure_evidence_persisted': failure_persisted}))
        return 2
    print(json.dumps({'status': 'success', 'output_dir': str(directory)}))
    return 0


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    cli = sub.add_parser('inspect')
    cli.add_argument('--source', choices=['textbook_userbehavior'], required=True)
    cli.add_argument('--output-dir', type=Path, required=True)
    profile_cli = sub.add_parser('profile')
    profile_cli.add_argument('--source', choices=['textbook_userbehavior'], required=True)
    profile_cli.add_argument('--output-dir', type=Path, required=True)
    replay_cli = sub.add_parser('replay')
    replay_cli.add_argument('--evidence', type=Path, required=True)
    replay_cli.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    attempts = []
    def guard(event, arguments):
        if event.startswith('socket.') or event in ('subprocess.Popen', 'os.system'):
            attempts.append(event)
            raise BoundaryError('network_or_child_process_denied')
    sys.addaudithook(guard)
    directory = args.output_dir
    if args.command in ('profile', 'replay'):
        return profile_entry(args, attempts)
    try:
        # Require caller-created empty run directory inside the fixed output boundary.
        output_target(directory / 'inspection.json', POLICY)
        if any(directory.iterdir()):
            raise BoundaryError('run_directory_not_empty')
        config = read_config()
        if config['path'] != str(PRODUCTION) or config['source_id'] != args.source:
            raise BoundaryError('config_policy_mismatch')
        request = SourceRequest(args.source, PRODUCTION, 'file', config['read_contract_ref'])
        source = validate_source(request, POLICY)
        inspection = inspect_file(source)
        before = after = None
        equal = None
        if inspection.status == 'needs_configuration':
            before = fingerprint_file(source)
            inspection = inspect_file(source)
            after = fingerprint_file(source)
            equal = before.sha256 == after.sha256 and before.bytes_read == after.bytes_read
        save('fingerprints.json', {'before': asdict(before) if before else None,
            'after': asdict(after) if after else None, 'consistent': equal}, directory)
        if equal is False:
            save('error.json', {'code': 'source_changed', 'stage': 'S0'}, directory)
            return 2
        report = InspectionReport('1.0', directory.name, 'S0', args.source,
            'configs/w1a-source.json#path', inspection, after, request.read_contract_ref,
            'not_run', ['content_parse', 'schema', 'delimiter', 'encoding', 'null_markers',
                        'column_types', 'time_unit', 'timezone', 'business_semantics'],
            inspection.errors, 'not_applicable')
        artifact = write_inspection(report, directory / 'inspection.json', POLICY)
        save('environment.json', {'recorded_at': now(), 'executable': sys.executable,
            'version': sys.version, 'prefix': sys.prefix, 'temp_directory': tempfile.gettempdir(),
            'process_variables': {k: os.environ.get(k) for k in ('TEMP', 'TMP', 'TMPDIR',
                'PYTHONDONTWRITEBYTECODE', 'PYTHONPATH', 'UV_CACHE_DIR')},
            'api_key_requirement': 'none', 'dependencies': 'standard_library_only'}, directory)
        save('network-observation.json', {'scope': 'CLI Python process; not system isolation',
            'blocked_events': attempts, 'product_model_usage': 'not_applicable'}, directory)
        save('cli-command.json', {'argv': sys.argv, 'exit_status': 0 if inspection.status == 'needs_configuration' else 2,
            'status': inspection.status, 'artifact': asdict(artifact)}, directory)
        print(json.dumps({'status': inspection.status, 'reason_code': inspection.reason_code,
                          'run_id': directory.name, 'hash_consistent': equal}))
        return 0 if inspection.status == 'needs_configuration' else 2
    except (BoundaryError, OSError, ValueError, KeyError) as error:
        code = error.code if isinstance(error, BoundaryError) else 'controlled_operation_failed'
        print(json.dumps({'status': 'failed', 'reason_code': code}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
