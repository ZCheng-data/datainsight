"""W2-B1 fixed S2 entry, deterministic plans and explicit S3 review only."""
import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import sys
from . import feasibility as f
from . import planning_methods as methods

ROOT = f.ROOT
OUTPUT = ROOT / 'outputs/W2-B1'
S2 = ROOT / 'outputs/W2-A/s2-accept-3178ad8b677e49edb91de623be0c3905/decision.json'
DIAGNOSIS = ROOT / 'outputs/W2-A/local-syn-3178ad8b677e49edb91de623be0c3905/diagnosis.json'
ACCEPTANCE = ROOT / 'docs/acceptance/results/W2-A-final-review-v2.md'
REQUIRED = ('input-manifest.json', 'reference-check.json', 'environment.json',
            'network-observation.json', 'cli-command.json')
REVIEW_KEYS = ('decision', 'selected_plan_id', 'selected_plan_version', 'metric_definition_hash',
               'confirm_metric_definition', 'actor', 'confirmed_at')


class AcceptedContext(dict):
    """Origin marker; every production build revalidates the underlying files."""


def load_s2_accept(decision_ref):
    path = f.path_check(decision_ref, ROOT)
    if path != S2:
        f.fail('s2_source_not_allowed')
    receipt = f.verify_decision(path)
    if receipt['decision'] != 'accept':
        f.fail('s2_not_accepted')
    if ROOT / receipt['diagnosis_ref'] != DIAGNOSIS:
        f.fail('s2_diagnosis_source')
    diagnosis, payload, manifest = f.load_diagnosis(DIAGNOSIS)
    if diagnosis['request_state'] != 'valid' or diagnosis['capability'] != 'supported':
        f.fail('s2_diagnosis_not_supported')
    acceptance = f.read_bytes(ACCEPTANCE)
    if '总判定：通过'.encode('utf-8') not in acceptance:
        f.fail('s2_stage_not_accepted')
    files = deepcopy(manifest['files'])
    for directory, primary in ((S2.parent, 'decision.json'), (DIAGNOSIS.parent, 'diagnosis.json')):
        for name in (primary, 'final-status.json', *REQUIRED):
            target = directory / name
            files.append({'path': f.relative(target), 'sha256': f.digest(f.read_bytes(target))})
    files.append({'path': f.relative(ACCEPTANCE), 'sha256': f.digest(acceptance)})
    files.append({'path': 'src/datainsight/feasibility_rules.py',
                  'sha256': f.digest(f.read_bytes(ROOT / 'src/datainsight/feasibility_rules.py'))})
    files.append({'path': 'src/datainsight/profile_templates.py',
                  'sha256': f.digest(f.read_bytes(ROOT / 'src/datainsight/profile_templates.py'))})
    refs, checks = [], []
    for check in diagnosis['prerequisite_checks']:
        if check['rule_id'] != methods.METHOD or check['rule_version'] != 'v1' or check['state'] != 'met':
            f.fail('method_prerequisite_not_met')
        evidence = check['evidence']
        reference = evidence if type(evidence) is str else {
            k: evidence[k] for k in ('evidence_ref', 'result_ref', 'result_sha256')}
        refs.append(reference)
        checks.append({**{k: check[k] for k in ('rule_id', 'rule_version', 'state', 'premise')},
                       'evidence': deepcopy(reference)})
    return AcceptedContext(schema_version='1.0', dataset_version=diagnosis['dataset_version'],
        s2_receipt_ref=f.relative(S2), s2_receipt_hash=f.digest(f.read_bytes(S2)),
        diagnosis_ref=f.relative(DIAGNOSIS), diagnosis_hash=f.digest(payload),
        question_ref=diagnosis['question_ref'], question_version=diagnosis['question_version'],
        question_hash=diagnosis['question_hash'], diagnostic_rules_id=diagnosis['ruleset_id'],
        diagnostic_rules_version=diagnosis['ruleset_version'], diagnostic_rules_hash=diagnosis['ruleset_hash'],
        input_manifest_ref=f.relative(DIAGNOSIS.parent / 'input-manifest.json'),
        input_manifest_hash=diagnosis['input_manifest_hash'],
        eligible_method_ids=diagnosis['eligible_method_ids'],
        prerequisite_checks=checks, evidence_refs=refs,
        acceptance_basis='verified_s2_accept', limitations=deepcopy(diagnosis['limitations']),
        bound_files=files)


def build_candidate_plans(context, registry):
    if type(context) is not AcceptedContext:
        f.fail('unverified_context')
    if f.encoded(context) != f.encoded(load_s2_accept(ROOT / context['s2_receipt_ref'])):
        f.fail('accepted_context_changed')
    if registry != methods.registered_methods():
        f.fail('unregistered_planning_methods')
    if any(m != methods.METHOD for m in context['eligible_method_ids']):
        f.fail('unknown_eligible_method')
    candidates = []
    if methods.METHOD in context['eligible_method_ids']:
        if not context['prerequisite_checks'] or any(c['state'] != 'met' for c in context['prerequisite_checks']):
            f.fail('candidate_prerequisites_unmet')
        candidates.append(methods.candidate(context))
    return {'schema_version': '1.0', 'run_id': 'unpublished', 'stage': 'S3',
        'status': 'computed_pending_finalization', 'accepted_context_ref': 'accepted-context.json',
        'accepted_context_hash': f.digest(f.encoded(context)), 'dataset_version': context['dataset_version'],
        'question_identity': {k: context['question_' + k] for k in ('ref', 'version', 'hash')},
        'diagnostic_rules_identity': {k: context['diagnostic_rules_' + k] for k in ('id', 'version', 'hash')},
        **{k: registry[k] for k in ('registry_id', 'registry_version', 'registry_hash')},
        'plan_set_version': 'v1', 'candidates': candidates, 'human_review_state': 'pending',
        'limitations': ['plan metadata only; no business result values', 'S3 only; no execution authorization']}


def new_run(value):
    directory = f.path_check(value, OUTPUT)
    if directory.parent != OUTPUT:
        f.fail('planning_run_direct_child_required')
    f.identifier(directory.name)
    if directory.exists():
        f.fail('output_exists')
    directory.mkdir(parents=True)
    return directory


def save(path, value):
    f.path_check(path, OUTPUT)
    payload = f.encoded(value)
    if len(payload) > f.LIMIT:
        f.fail('planning_output_size_boundary')
    with path.open('xb') as stream:
        stream.write(payload)
    return f.digest(payload)


def publish(directory, data):
    target = directory / 'final-status.json'
    staging = directory / ('final-status-' + data['status'] + '.tmp')
    f.path_check(target, OUTPUT)
    if target.exists():
        f.fail('terminal_exists')
    with staging.open('xb') as stream:
        stream.write(f.encoded(data))
        stream.flush()
        os.fsync(stream.fileno())
    if target.exists():
        f.fail('terminal_exists')
    staging.rename(target)


def terminal(directory, command):
    value = f.parse(f.read_bytes(f.path_check(directory / 'final-status.json', OUTPUT)))
    f.exact(value, ('schema_version', 'run_id', 'command', 'status', 'exit_status',
                    'completed_at', 'required_evidence_refs'))
    if (value['schema_version'] != '1.0' or value['run_id'] != directory.name
            or value['command'] != command or value['status'] != 'success'
            or type(value['exit_status']) is not int or value['exit_status'] != 0
            or value['required_evidence_refs'] != list(REQUIRED)):
        f.fail('planning_terminal_invalid')
    f.timestamp(value['completed_at'])
    for name in REQUIRED:
        f.parse(f.read_bytes(directory / name))


def planning_manifest(context):
    files = deepcopy(context['bound_files'])
    files.append({'path': 'src/datainsight/planning_methods.py',
                  'sha256': f.digest(f.read_bytes(ROOT / 'src/datainsight/planning_methods.py'))})
    return {'schema_version': '1.0', 'files': files}


def load_plan_set(path):
    path = f.path_check(path, OUTPUT)
    if path.name != 'candidate-plans.json' or path.parent.parent != OUTPUT:
        f.fail('plan_set_path')
    terminal(path.parent, 'candidates')
    context = load_s2_accept(S2)
    context_payload = f.read_bytes(path.parent / 'accepted-context.json')
    if context_payload != f.encoded(context):
        f.fail('stored_context_changed')
    manifest = planning_manifest(context)
    if f.read_bytes(path.parent / 'input-manifest.json') != f.encoded(manifest):
        f.fail('planning_manifest_changed')
    expected = build_candidate_plans(context, methods.registered_methods())
    expected['run_id'] = path.parent.name
    payload = f.read_bytes(path)
    if payload != f.encoded(expected):
        f.fail('candidate_plan_changed')
    audit = f.parse(f.read_bytes(path.parent / 'reference-check.json'))
    if audit != {'schema_version': '1.0', 'references_resolvable': True,
                 'context_hash': f.digest(context_payload), 'manifest_hash': f.digest(f.encoded(manifest))}:
        f.fail('candidate_reference_changed')
    return expected, payload, context, manifest


def review_check(review, plans):
    f.exact(review, REVIEW_KEYS)
    if review['decision'] not in ('approve', 'reject', 'cancel'):
        f.fail('invalid_s3_decision')
    f.identifier(review['actor'])
    f.timestamp(review['confirmed_at'])
    if type(review['confirm_metric_definition']) is not bool:
        f.fail('invalid_metric_confirmation_type')
    if review['decision'] != 'approve':
        if (any(review[k] is not None for k in ('selected_plan_id', 'selected_plan_version', 'metric_definition_hash'))
                or review['confirm_metric_definition']):
            f.fail('stop_review_has_selection')
        return None
    if not review['confirm_metric_definition']:
        f.fail('metric_confirmation_required')
    selected = [c for c in plans['candidates'] if c['plan_id'] == review['selected_plan_id']
                and c['plan_version'] == review['selected_plan_version']]
    if len(selected) != 1:
        f.fail('selected_plan_not_found')
    if selected[0]['metric_definition_hash'] != review['metric_definition_hash']:
        f.fail('metric_hash_mismatch')
    return selected[0]


def receipt_value(path, payload, context, manifest, plans, review, run_id):
    selected = review_check(review, plans)
    return {'schema_version': '1.0', 'run_id': run_id, 'plan_set_ref': f.relative(path),
        'plan_set_hash': f.digest(payload), **review,
        'metric_definition_version': selected['metric_definition_version'] if selected else None,
        'dataset_version': context['dataset_version'],
        's2_receipt_ref': context['s2_receipt_ref'], 's2_receipt_hash': context['s2_receipt_hash'],
        'diagnosis_ref': context['diagnosis_ref'], 'diagnosis_hash': context['diagnosis_hash'],
        'question_identity': plans['question_identity'],
        'diagnostic_rules_identity': plans['diagnostic_rules_identity'],
        'registry_identity': {k: plans['registry_' + k] for k in ('id', 'version', 'hash')},
        'input_manifest_hash': f.digest(f.encoded(manifest)), 'acceptance_scope': 'S3_plan_and_metric_only'}


def record_s3_review(plan_set_ref, review, output_dir):
    path = f.path_check(plan_set_ref, OUTPUT)
    plans, payload, context, manifest = load_plan_set(path)
    review_check(review, plans)
    directory = new_run(output_dir)
    receipt = receipt_value(path, payload, context, manifest, plans, review, directory.name)
    save(directory / 's3-review.json', receipt)
    save(directory / 'input-manifest.json', manifest)
    save(directory / 'reference-check.json', {'schema_version': '1.0', 'references_resolvable': True,
        'plan_set_ref': f.relative(path), 'plan_set_hash': f.digest(payload)})
    return receipt


def verify_review(path):
    path = f.path_check(path, OUTPUT)
    if path.name != 's3-review.json' or path.parent.parent != OUTPUT:
        f.fail('s3_receipt_path')
    terminal(path.parent, 'review')
    value = f.parse(f.read_bytes(path))
    f.exact(value, ('schema_version', 'run_id', 'plan_set_ref', 'plan_set_hash', *REVIEW_KEYS,
        'metric_definition_version', 'dataset_version', 's2_receipt_ref', 's2_receipt_hash',
        'diagnosis_ref', 'diagnosis_hash', 'question_identity', 'diagnostic_rules_identity',
        'registry_identity', 'input_manifest_hash', 'acceptance_scope'))
    plan_path = ROOT / value['plan_set_ref']
    plans, payload, context, manifest = load_plan_set(plan_path)
    expected = receipt_value(plan_path, payload, context, manifest, plans,
                             {k: value[k] for k in REVIEW_KEYS}, path.parent.name)
    if f.encoded(value) != f.encoded(expected):
        f.fail('s3_receipt_binding_changed')
    if f.read_bytes(path.parent / 'input-manifest.json') != f.encoded(manifest):
        f.fail('s3_manifest_changed')
    if f.parse(f.read_bytes(path.parent / 'reference-check.json')) != {
            'schema_version': '1.0', 'references_resolvable': True,
            'plan_set_ref': f.relative(plan_path), 'plan_set_hash': f.digest(payload)}:
        f.fail('s3_reference_changed')
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    candidates = sub.add_parser('candidates')
    candidates.add_argument('--output-dir', type=Path, required=True)
    review = sub.add_parser('review')
    review.add_argument('--plan-set', type=Path, required=True)
    review.add_argument('--decision', choices=('approve', 'reject', 'cancel'), required=True)
    review.add_argument('--selected-plan-id')
    review.add_argument('--selected-plan-version')
    review.add_argument('--metric-definition-hash')
    review.add_argument('--confirm-metric-definition', action='store_true')
    review.add_argument('--actor', required=True)
    review.add_argument('--confirmed-at', required=True)
    review.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args(argv)
    directory, owned, phase = args.output_dir, False, 'preflight'
    events = []
    def guard(event, arguments):
        if event in ('socket.connect', 'socket.connect_ex', 'socket.getaddrinfo', 'socket.sendto'):
            events.append(event)
            f.fail('planning_network_blocked')
    sys.addaudithook(guard)
    try:
        env = f.environment()
        f.path_check(directory, OUTPUT)
        if directory.exists():
            f.fail('output_exists')
        phase = 'input_verification'
        if args.command == 'candidates':
            context = load_s2_accept(S2)
            plans = build_candidate_plans(context, methods.registered_methods())
            manifest = planning_manifest(context)
            directory = new_run(directory)
            owned = True
            plans['run_id'] = directory.name
            phase = 'candidate_evidence'
            save(directory / 'accepted-context.json', context)
            save(directory / 'candidate-plans.json', plans)
            save(directory / 'input-manifest.json', manifest)
            save(directory / 'reference-check.json', {'schema_version': '1.0', 'references_resolvable': True,
                'context_hash': f.digest(f.encoded(context)), 'manifest_hash': f.digest(f.encoded(manifest))})
        else:
            spec = {k: getattr(args, k) for k in REVIEW_KEYS}
            load_plan_set(args.plan_set)
            try:
                record_s3_review(args.plan_set, spec, directory)
            finally:
                owned = directory.is_dir()
        phase = 'environment_evidence'
        save(directory / 'environment.json', env)
        phase = 'network_evidence'
        save(directory / 'network-observation.json', {'blocked_events': events,
            'scope': 'Python audit events only; not native/system isolation',
            'product_model_usage': 'not_applicable', 'engine_started': False})
        phase = 'command_evidence'
        save(directory / 'cli-command.json', {'executable': sys.executable, 'process_argv': sys.argv,
            'main_argv': list(argv) if argv is not None else sys.argv[1:],
            'exit_status': None, 'exit_status_ref': 'final-status.json#exit_status'})
        phase = 'final_status_publication'
        publish(directory, {'schema_version': '1.0', 'run_id': directory.name,
            'command': args.command, 'status': 'success', 'exit_status': 0,
            'completed_at': f.now(), 'required_evidence_refs': list(REQUIRED)})
    except (ValueError, OSError, TypeError, KeyError, RecursionError) as error:
        reason = str(error) if type(error) is f.BoundaryError else 'controlled_planning_failure'
        persisted = False
        if owned:
            try:
                publish(directory, {'schema_version': '1.0', 'run_id': directory.name,
                    'command': args.command, 'status': 'failed', 'exit_status': 2,
                    'phase': phase, 'reason_code': reason, 'failed_at': f.now()})
                persisted = True
            except (ValueError, OSError, TypeError, KeyError):
                pass
        print(json.dumps({'status': 'failed', 'exit_status': 2, 'phase': phase,
                          'reason_code': reason, 'failure_evidence_persisted': persisted}))
        return 2
    print(json.dumps({'status': 'success', 'exit_status': 0, 'output_dir': str(directory),
                      'final_acceptance': 'not_performed', 'scope': 'S3_plan_and_metric_only'}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
