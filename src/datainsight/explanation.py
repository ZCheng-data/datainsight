"""W2-B2 explanation boundary; drafts do not confer business authority."""
from copy import deepcopy
from dataclasses import dataclass
import re
import os
from pathlib import Path
from . import feasibility as f
from . import planning as p
from . import planning_methods as methods
from .deepseek_call import ProviderResult, RESPONSE_LIMIT

REVIEW = f.ROOT / 'outputs/W2-B1/w2b1-review-219e79901d08444bab62c6e61f6e2211/s3-review.json'
ACCEPTANCE = f.ROOT / 'docs/acceptance/results/W2-B1-final-review-v2.md'
ALIASES = ('p_selected', 'schema_behaviour', 'metric_records', 'stat_row_count')
SECTIONS = ('purpose', 'prerequisites', 'metric_scope', 'limitations')


@dataclass(frozen=True)
class ApprovedPlan:
    identity: dict
    metric_definition: dict
    references: dict
    input_manifest: dict


def load_approved_plan(review_ref):
    path = f.path_check(review_ref, f.ROOT)
    if path != REVIEW:
        f.fail('explanation_review_source_not_allowed')
    receipt = p.verify_review(path)
    if receipt['decision'] != 'approve' or receipt['confirm_metric_definition'] is not True:
        f.fail('s3_not_approved')
    plans, payload, context, manifest = p.load_plan_set(f.ROOT / receipt['plan_set_ref'])
    chosen = [c for c in plans['candidates'] if c['plan_id'] == receipt['selected_plan_id']
              and c['plan_version'] == receipt['selected_plan_version']]
    if (len(chosen) != 1 or chosen[0]['method_id'] != methods.METHOD
            or chosen[0]['metric_definition_hash'] != receipt['metric_definition_hash']):
        f.fail('approved_plan_selection_mismatch')
    acceptance = f.read_bytes(ACCEPTANCE)
    if '总判定：通过'.encode() not in acceptance:
        f.fail('planning_stage_not_accepted')
    snapshot = f.load_accepted_profile(f.LEGACY, f.ACCEPTANCE)
    row_ref = snapshot['metric_refs']['summary']
    row_count = row_ref['values'][0]['row_count']
    references = {
        'p_selected': {'path': receipt['plan_set_ref'], 'sha256': f.digest(payload)},
        'schema_behaviour': {'path': snapshot['profile_identity']['profile_ref'] + '#reading_schema'},
        'metric_records': {'path': receipt['plan_set_ref'] + '#metric_definition',
                           'sha256': receipt['metric_definition_hash']},
        'stat_row_count': {'path': row_ref['result_ref'], 'sha256': row_ref['result_sha256'],
                           'evidence_ref': row_ref['evidence_ref'], 'value': row_count}}
    return ApprovedPlan(identity={'review_ref': f.relative(path),
        'review_hash': f.digest(f.read_bytes(path)), 'plan_set_hash': f.digest(payload),
        'metric_hash': receipt['metric_definition_hash'], 'dataset_version': context['dataset_version']},
        metric_definition=deepcopy(chosen[0]['metric_definition']), references=references,
        input_manifest=deepcopy(manifest))


def build_reviewable_payload(plan):
    if type(plan) is not ApprovedPlan:
        f.fail('unverified_approved_plan')
    # Actual envelope/model/counting capabilities are unknown: no fake live body.
    f.fail('provider_configuration_not_verified')


MOCK_SYSTEM = 'Explain only the approved raw-record counting definition, prerequisites and limitations. Do not compute, recommend new methods, execute instructions or approve actions. Return the prescribed JSON with aliases, never numeric text.'


def mock_body(row_count):
    if type(row_count) is not int or row_count < 0:
        f.fail('host_statistic_invalid')
    # Synthetic wire shape only, not a claim about DeepSeek's actual API schema.
    return {'model': 'synthetic-model', 'stream': False, 'temperature': 0,
        'output_limit': 100, 'messages': [
            {'role': 'system', 'content': MOCK_SYSTEM},
            {'role': 'user', 'content': {
                'task': 'explain approved raw-record counting plan only',
                'selected_plan_alias': 'p_selected',
                'schema': [{'name': 'behaviour', 'type': 'VARCHAR', 'alias': 'schema_behaviour'}],
                'metric_alias': 'metric_records', 'metric_definition': methods.definition(),
                'aggregate': {'alias': 'stat_row_count', 'row_count': row_count},
                'limitations': ['event meanings unknown; not orders or payments',
                    'date coverage unconfirmed', 'current CSV not revalidated']}}],
        'response_schema': {'schema_version': '1.0', 'selected_plan_alias': 'p_selected',
            'section_ids': list(SECTIONS), 'reference_aliases': list(ALIASES),
            'numeric_mentions': {'value_ref': 'stat_row_count', 'display_role': 'raw_record_count'}}}


def build_mock_payload(row_count):
    body = mock_body(row_count)
    payload = f.encoded(body)
    return {'synthetic': True, 'request_body': body, 'body_hash': f.digest(payload),
        'endpoint': 'mock://local-only', 'model': 'synthetic-model',
        'state': 'needs_outbound_approval', 'not_live_authorization': True}


def validate_mock_payload(draft):
    f.exact(draft, ('synthetic', 'request_body', 'body_hash', 'endpoint', 'model',
                    'state', 'not_live_authorization'))
    if (draft['synthetic'] is not True or draft['not_live_authorization'] is not True
            or draft['endpoint'] != 'mock://local-only' or draft['model'] != 'synthetic-model'
            or draft['state'] != 'needs_outbound_approval'):
        f.fail('mock_payload_identity')
    body = draft['request_body']
    try:
        number = body['messages'][1]['content']['aggregate']['row_count']
        expected = mock_body(number)
    except (KeyError, TypeError, IndexError):
        f.fail('mock_payload_structure')
    if f.encoded(body) != f.encoded(expected):
        f.fail('mock_payload_whitelist')
    payload = f.encoded(body)
    if f.digest(payload) != draft['body_hash']:
        f.fail('mock_payload_hash')
    if len(payload) > RESPONSE_LIMIT:
        f.fail('mock_payload_size_boundary')
    return payload


@dataclass(frozen=True)
class MockAuthorization:
    body_hash: str
    policy_hash: str
    request_id: str
    upstream_hash: str
    synthetic: bool = True


def mock_authorize(draft, policy, request_id, upstream_hash):
    from . import call_budget as budget
    validate_mock_payload(draft)
    f.identifier(request_id)
    f.hash_value(upstream_hash)
    return MockAuthorization(draft['body_hash'], budget.mock_policy_check(policy), request_id, upstream_hash)


MOCK_OUTPUT = f.ROOT / 'outputs/W2-B2'
MOCK_AUTH_REFS = ('outbound-authorization.json', 'binding-check.json')


def save_mock_file(path, value):
    f.path_check(path, MOCK_OUTPUT)
    payload = f.encoded(value)
    if len(payload) > f.LIMIT:
        f.fail('mock_evidence_size_boundary')
    with path.open('xb') as stream:
        stream.write(payload)
    return f.digest(payload)


def publish_mock_status(directory, value):
    target = directory / 'final-status.json'
    staging = directory / ('final-status-' + value['status'] + '.tmp')
    f.path_check(staging, MOCK_OUTPUT)
    if target.exists():
        f.fail('mock_terminal_exists')
    with staging.open('xb') as stream:
        stream.write(f.encoded(value))
        stream.flush()
        os.fsync(stream.fileno())
    if target.exists():
        f.fail('mock_terminal_exists')
    staging.rename(target)


def authorization_value(draft, policy, request_id, upstream_hash):
    from . import call_budget as budget
    validate_mock_payload(draft)
    f.identifier(request_id)
    f.hash_value(upstream_hash)
    return {'schema_version': '1.0', 'synthetic_test_input': True,
        'not_user_confirmation': True, 'not_live_authorization': True,
        'body_hash': draft['body_hash'], 'endpoint': draft['endpoint'], 'model': draft['model'],
        'policy_hash': budget.mock_policy_check(policy), 'scope_id': policy['scope_id'],
        'upstream_hash': upstream_hash, 'request_id': request_id,
        'attempt_limit': 1, 'confirmation_actor': 'controlled_test_actor',
        'confirmed_at': 'not_provided'}


def persist_mock_authorization(output_dir, draft, policy, request_id, upstream_hash):
    value = authorization_value(draft, policy, request_id, upstream_hash)
    directory = f.path_check(output_dir, MOCK_OUTPUT)
    if directory.parent != MOCK_OUTPUT or not directory.name.startswith('w2b2-mock-'):
        f.fail('mock_authorization_path')
    f.identifier(directory.name)
    if directory.exists():
        f.fail('output_exists')
    directory.mkdir()
    value.update(recorded_at=f.now(), recorded_at_source='Python datetime.now(timezone.utc)',
                 recorded_at_status='available')
    identity = save_mock_file(directory / 'outbound-authorization.json', value)
    save_mock_file(directory / 'binding-check.json', {'authorization_hash': identity,
        'body_hash': draft['body_hash'], 'policy_hash': value['policy_hash'], 'upstream_hash': upstream_hash})
    publish_mock_status(directory, {'schema_version': '1.0', 'run_id': directory.name,
        'status': 'success', 'synthetic': True, 'exit_status': 0,
        'required_evidence_refs': list(MOCK_AUTH_REFS)})
    return directory / 'outbound-authorization.json'


def restore_mock_authorization(path, draft, policy, upstream_hash, request_id):
    path = f.path_check(path, MOCK_OUTPUT)
    if (path.name != 'outbound-authorization.json' or path.parent.parent != MOCK_OUTPUT
            or not path.parent.name.startswith('w2b2-mock-')):
        f.fail('mock_authorization_path')
    expected_terminal = {'schema_version': '1.0', 'run_id': path.parent.name,
        'status': 'success', 'synthetic': True, 'exit_status': 0,
        'required_evidence_refs': list(MOCK_AUTH_REFS)}
    if f.encoded(f.parse(f.read_bytes(path.parent / 'final-status.json'))) != f.encoded(expected_terminal):
        f.fail('mock_authorization_terminal')
    value = f.parse(f.read_bytes(path))
    expected = authorization_value(draft, policy, request_id, upstream_hash)
    f.exact(value, (*expected.keys(), 'recorded_at', 'recorded_at_source', 'recorded_at_status'))
    f.timestamp(value['recorded_at'])
    if value['recorded_at_source'] != 'Python datetime.now(timezone.utc)' or value['recorded_at_status'] != 'available':
        f.fail('mock_authorization_time')
    for key, item in expected.items():
        if type(value[key]) is not type(item) or value[key] != item:
            f.fail('mock_authorization_record_changed')
    binding = {'authorization_hash': f.digest(f.read_bytes(path)), 'body_hash': draft['body_hash'],
               'policy_hash': expected['policy_hash'], 'upstream_hash': upstream_hash}
    if f.encoded(f.parse(f.read_bytes(path.parent / 'binding-check.json'))) != f.encoded(binding):
        f.fail('mock_authorization_binding')
    # Synthetic local consistency only: this is not authenticated human approval.
    return mock_authorize(draft, policy, request_id, upstream_hash)


def execute_mock(draft, authorization, policy, upstream_hash, directory, lock_path, transport):
    from . import call_budget as budget
    validate_mock_payload(draft)
    if type(authorization) is not MockAuthorization or authorization.synthetic is not True:
        f.fail('mock_authorization_required')
    if (authorization.body_hash != draft['body_hash']
            or authorization.policy_hash != budget.mock_policy_check(policy)
            or authorization.upstream_hash != upstream_hash):
        f.fail('mock_authorization_changed')
    # Callable is test-only; never routed through the disabled live provider function.
    def checked_transport():
        result = transport()
        if type(result) is not ProviderResult or result.synthetic is not True or result.model != draft['model'] or result.request_id != authorization.request_id:
            f.fail('mock_provider_identity')
        if result.failure_code or result.finish_state != 'stop':
            f.fail('mock_provider_failed')
        return {'usage': result.usage, 'provider_result': result, 'synthetic': True}
    return budget.run_mock_attempt(directory, lock_path, policy, authorization.request_id, checked_transport)


def execute_persisted_mock(draft, authorization_ref, policy, upstream_hash, request_id,
                           directory, lock_path, transport):
    """Offline entry: durable authorization rechecked before any budget/send step."""
    authorization = restore_mock_authorization(authorization_ref, draft, policy, upstream_hash, request_id)
    return execute_mock(draft, authorization, policy, upstream_hash, directory, lock_path, transport)


MOCK_CALL_REFS = ('request-metadata.json', 'authorization-reference.json', 'budget-check.json',
    'usage.json', 'cost.json', 'validated-response.json', 'explanation-draft.json',
    'reference-check.json', 'environment.json', 'network-observation.json', 'cli-command.json')


def mock_call_run(output_dir, draft, authorization_ref, policy, upstream_hash, request_id,
                  budget_dir, lock_path, transport, references):
    """Synthetic evidence orchestration only, not a product paid-call entry."""
    from . import call_budget as budget
    env = f.environment()
    directory = f.path_check(output_dir, MOCK_OUTPUT)
    if directory.parent != MOCK_OUTPUT or not directory.name.startswith('w2b2-mock-'):
        f.fail('mock_call_path')
    f.identifier(directory.name)
    if directory.exists():
        f.fail('output_exists')
    # Validate authorization before owning/writing a run; no implicit permission.
    restore_mock_authorization(authorization_ref, draft, policy, upstream_hash, request_id)
    directory.mkdir()
    phase, calls = 'pre_send_evidence', 0
    completed = None
    def counted_transport():
        nonlocal calls
        calls += 1
        return transport()
    try:
        save_mock_file(directory / 'request-metadata.json', {'synthetic': True, 'request_id': request_id,
            'body_hash': draft['body_hash'], 'endpoint': draft['endpoint'], 'model': draft['model']})
        save_mock_file(directory / 'authorization-reference.json', {
            'path': f.relative(authorization_ref), 'sha256': f.digest(f.read_bytes(authorization_ref))})
        save_mock_file(directory / 'budget-check.json', {'policy_hash': budget.mock_policy_check(policy),
            'budget_dir': f.relative(budget_dir), 'synthetic': True})
        phase = 'mock_attempt'
        completed = execute_persisted_mock(draft, authorization_ref, policy, upstream_hash, request_id,
                                           budget_dir, lock_path, counted_transport)
        phase = 'response_validation'
        result = completed['result']['provider_result']
        explanation = validate_explanation(result, references)
        # No raw content is persisted before strict schema/safety validation.
        save_mock_file(directory / 'validated-response.json', f.parse(result.content))
        save_mock_file(directory / 'explanation-draft.json', explanation)
        save_mock_file(directory / 'usage.json', {'synthetic': True, 'usage': completed['usage']})
        save_mock_file(directory / 'cost.json', {'synthetic': True, 'amount': completed['cost'],
            'basis': 'mock usage and mock rates; not provider billing'})
        save_mock_file(directory / 'reference-check.json', {'event_refs': completed['event_refs'],
            'body_hash': draft['body_hash'], 'upstream_hash': upstream_hash})
        save_mock_file(directory / 'environment.json', env)
        save_mock_file(directory / 'network-observation.json', {'real_network_calls': 0,
            'scope': 'test callable only; not independent system monitoring'})
        save_mock_file(directory / 'cli-command.json', {'entry': 'mock_call_run',
            'not_cli_process': True, 'request_id': request_id, 'real_provider_attempts': 0,
            'mock_transport_calls': calls})
        phase = 'publication'
        publish_mock_status(directory, {'schema_version': '1.0', 'run_id': directory.name,
            'status': 'success', 'synthetic': True, 'exit_status': 0,
            'required_evidence_refs': list(MOCK_CALL_REFS)})
        return {'exit_status': 0, 'mock_transport_calls': calls, 'failure_evidence_persisted': False}
    except Exception as error:
        reason = str(error) if type(error) is f.BoundaryError else 'controlled_mock_call_failure'
        # A completed mock settlement is never erased for an invalid explanation.
        persisted = False
        try:
            save_mock_file(directory / 'failure.json', {'reason_code': reason, 'phase': phase,
                'synthetic': True, 'mock_transport_calls': calls, 'raw_response_persisted': False,
                'mock_settlement_completed': completed is not None})
            publish_mock_status(directory, {'schema_version': '1.0', 'run_id': directory.name,
                'status': 'failed', 'synthetic': True, 'exit_status': 2, 'reason_code': reason, 'phase': phase})
            persisted = True
        except Exception:
            pass
        return {'exit_status': 2, 'mock_transport_calls': calls,
                'failure_evidence_persisted': persisted, 'reason_code': reason}


def safe_text(value):
    if type(value) is not str or not value or len(value) > 2000:
        f.fail('explanation_text_boundary')
    if re.search(r'[0-9０-９%％]|(?:\d{4}[-/])', value):
        f.fail('direct_numeric_text')
    if re.search(r'(?i)(?:[a-z]:[\\/]|https?://|/outputs/|SENTINEL|api[_ -]?key|bearer\s)', value):
        f.fail('sensitive_response_text')
    if re.search(r'(?i)\b(select|with|insert|delete|drop|attach|gmv|lstm|approve|approved)\b', value):
        f.fail('unsupported_response_content')
    if any(word in value for word in ('转化率', '因果', '提升收益', '订单数', '支付数', '批准执行', '清洗数据')):
        f.fail('unsupported_response_content')


def validate_explanation(result, references):
    if type(result) is not ProviderResult:
        f.fail('provider_result_type')
    if result.failure_code:
        f.fail(result.failure_code)
    if result.finish_state != 'stop':
        f.fail('provider_finish_not_complete')
    if type(result.content) is not bytes or not result.content:
        f.fail('provider_empty_content')
    if len(result.content) > RESPONSE_LIMIT:
        f.fail('response_size_boundary')
    f.exact(references, ALIASES)
    value = f.parse(result.content)
    f.exact(value, ('schema_version', 'selected_plan_alias', 'explanation_sections', 'numeric_mentions'))
    if value['schema_version'] != '1.0' or value['selected_plan_alias'] != 'p_selected':
        f.fail('explanation_identity')
    sections = value['explanation_sections']
    if type(sections) is not list or len(sections) != len(SECTIONS):
        f.fail('explanation_sections_boundary')
    for index, section in enumerate(sections):
        f.exact(section, ('section_id', 'text', 'reference_aliases'))
        if section['section_id'] != SECTIONS[index]:
            f.fail('explanation_section_identity')
        safe_text(section['text'])
        refs = section['reference_aliases']
        if (type(refs) is not list or not refs or len(refs) > len(ALIASES)
                or any(type(alias) is not str or alias not in ALIASES for alias in refs)
                or len(set(refs)) != len(refs)):
            f.fail('explanation_reference_invalid')
    mentions = value['numeric_mentions']
    if type(mentions) is not list or len(mentions) > 1:
        f.fail('numeric_mentions_boundary')
    for mention in mentions:
        f.exact(mention, ('value_ref', 'display_role'))
        if mention != {'value_ref': 'stat_row_count', 'display_role': 'raw_record_count'}:
            f.fail('numeric_reference_invalid')
    number = references['stat_row_count']['value']
    if type(number) is not int or number < 0:
        f.fail('host_statistic_invalid')
    return {'schema_version': '1.0', 'validation_state': 'structurally_valid_draft',
        'human_review_state': 'pending', 'selected_plan_alias': 'p_selected',
        'explanation_sections': deepcopy(sections),
        'host_rendered_numeric_mentions': [{'value_ref': 'stat_row_count', 'value': number,
                                           'display_role': 'raw_record_count'}] if mentions else [],
        'limitations': ['structure/reference checks cannot certify every semantic claim',
                        'not a new data finding or approved business action',
                        'synthetic provider result' if result.synthetic else 'provider output requires human review']}
