"""Decimal mock-budget arithmetic and immutable event publication primitives.

Live policy/scope approval, OS exclusion and full ledger recovery are not yet
implemented. Arithmetic alone never grants a sending permission.
"""
from decimal import Decimal, InvalidOperation, localcontext
from fractions import Fraction
import os
import re
from contextlib import contextmanager
from pathlib import Path
from . import feasibility as f

ROOT = f.ROOT
OUTPUT = ROOT / 'outputs/W2-B2'


def money(value):
    if type(value) is not str:
        f.fail('budget_decimal_string_required')
    if len(value) > 128:
        f.fail('budget_decimal_boundary')
    try:
        result = Decimal(value)
    except InvalidOperation:
        f.fail('budget_decimal_invalid')
    if not result.is_finite() or result < 0:
        f.fail('budget_decimal_invalid')
    if abs(result.as_tuple().exponent) > 128:
        f.fail('budget_decimal_boundary')
    return result


def reserve_amount(input_upper, output_upper, input_rate, output_rate, unit, quantum):
    for value in (input_upper, output_upper, unit):
        if type(value) is not int or value < 0:
            f.fail('budget_integer_invalid')
    if unit == 0:
        f.fail('budget_unit_zero')
    step = money(quantum)
    if step == 0:
        f.fail('budget_quantum_zero')
    # Exact rational ceiling: Decimal division must not round a tiny excess down.
    raw = (input_upper * Fraction(money(input_rate)) +
           output_upper * Fraction(money(output_rate))) / unit
    units = raw / Fraction(step)
    rounded_units = (units.numerator + units.denominator - 1) // units.denominator
    with localcontext() as context:
        context.prec = len(str(rounded_units)) + len(step.as_tuple().digits) + 2
        return str(Decimal(rounded_units) * step)


def validate_mock_usage(usage, input_upper, output_upper):
    f.exact(usage, ('input_tokens', 'output_tokens'))
    for key, limit in (('input_tokens', input_upper), ('output_tokens', output_upper)):
        if type(usage[key]) is not int or usage[key] < 0 or usage[key] > limit:
            f.fail('usage_invalid_or_over_reserved')
    return usage


def publish_event(directory, sequence, kind, data):
    directory = f.path_check(directory, OUTPUT)
    if not directory.name.startswith('budget-synthetic-'):
        f.fail('live_budget_scope_not_configured')
    if type(sequence) is not int or sequence < 1:
        f.fail('event_sequence_invalid')
    if kind not in ('reservation', 'attempt_started', 'settlement', 'unknown_charge', 'reconciliation'):
        f.fail('event_kind_invalid')
    if not directory.is_dir():
        f.fail('budget_scope_missing')
    if any(path.suffix == '.tmp' for path in directory.iterdir()):
        f.fail('budget_unpublished_event')
    name = 'event-' + str(sequence).zfill(6) + '-' + kind
    target, staging = directory / (name + '.json'), directory / (name + '.tmp')
    f.path_check(staging, OUTPUT)
    if target.exists():
        f.fail('event_exists')
    payload = f.encoded(data)
    if len(payload) > f.LIMIT:
        f.fail('budget_event_size_boundary')
    with staging.open('xb') as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    if target.exists():
        f.fail('event_exists')
    staging.rename(target)
    return {'event_ref': f.relative(target), 'sha256': f.digest(payload)}


def mock_policy_check(policy):
    f.exact(policy, ('synthetic', 'scope_id', 'input_upper', 'output_upper', 'input_rate',
        'output_rate', 'unit', 'quantum', 'request_limit', 'input_limit', 'output_limit', 'amount_limit'))
    if policy['synthetic'] is not True:
        f.fail('mock_policy_required')
    f.identifier(policy['scope_id'])
    if not policy['scope_id'].startswith('synthetic-'):
        f.fail('mock_scope_required')
    for key in ('input_upper', 'output_upper', 'unit', 'request_limit', 'input_limit', 'output_limit'):
        if type(policy[key]) is not int or policy[key] < 1:
            f.fail('budget_integer_invalid')
    for key in ('input_rate', 'output_rate', 'quantum', 'amount_limit'):
        money(policy[key])
    reserve_amount(policy['input_upper'], policy['output_upper'], policy['input_rate'],
                   policy['output_rate'], policy['unit'], policy['quantum'])
    return f.digest(f.encoded(policy))


def ledger_read(directory, policy):
    identity = mock_policy_check(policy)
    directory = f.path_check(directory, OUTPUT)
    if directory.parent != OUTPUT or directory.name != 'budget-' + policy['scope_id']:
        f.fail('budget_scope_identity')
    if not directory.is_dir():
        f.fail('budget_scope_missing')
    events, previous, requests = [], None, {}
    for path in sorted(directory.iterdir()):
        f.path_check(path, OUTPUT)
        if path.suffix == '.tmp':
            f.fail('budget_unpublished_event')
        match = re.fullmatch(r'event-([0-9]{6})-(reservation|attempt_started|settlement|unknown_charge|reconciliation)\.json', path.name)
        if not match or not path.is_file():
            f.fail('budget_unknown_file')
        sequence = int(match.group(1))
        if sequence != len(events) + 1:
            f.fail('budget_sequence_gap')
        payload = f.read_bytes(path)
        event = f.parse(payload)
        f.exact(event, ('schema_version', 'sequence', 'kind', 'policy_hash', 'request_id',
                        'previous_hash', 'recorded_at', 'data'))
        if (event['schema_version'] != '1.0' or event['sequence'] != sequence
                or event['kind'] != match.group(2) or event['policy_hash'] != identity
                or event['previous_hash'] != previous):
            f.fail('budget_event_binding')
        f.identifier(event['request_id'])
        f.timestamp(event['recorded_at'])
        kind, request = event['kind'], event['request_id']
        data = event['data']
        if kind == 'reservation':
            if request in requests:
                f.fail('budget_duplicate_reservation')
            f.exact(data, ('input_upper', 'output_upper', 'amount'))
            expected = reserve_amount(policy['input_upper'], policy['output_upper'], policy['input_rate'],
                                      policy['output_rate'], policy['unit'], policy['quantum'])
            if data != {'input_upper': policy['input_upper'], 'output_upper': policy['output_upper'], 'amount': expected}:
                f.fail('budget_reservation_mismatch')
            requests[request] = {'state': kind, **data}
        elif kind == 'attempt_started':
            f.exact(data, ())
            if request not in requests or requests[request]['state'] != 'reservation':
                f.fail('budget_attempt_order')
            requests[request]['state'] = kind
        elif kind == 'settlement':
            f.exact(data, ('usage', 'amount'))
            if request not in requests or requests[request]['state'] != 'attempt_started':
                f.fail('budget_settlement_order')
            usage = validate_mock_usage(data['usage'], policy['input_upper'], policy['output_upper'])
            expected = reserve_amount(usage['input_tokens'], usage['output_tokens'], policy['input_rate'],
                                      policy['output_rate'], policy['unit'], policy['quantum'])
            if data['amount'] != expected or money(expected) > money(requests[request]['amount']):
                f.fail('budget_settlement_mismatch')
            requests[request].update(state=kind, amount=expected,
                input_upper=usage['input_tokens'], output_upper=usage['output_tokens'])
        elif kind == 'unknown_charge':
            f.exact(data, ('reason_code',))
            f.identifier(data['reason_code'])
            if request not in requests or requests[request]['state'] not in ('reservation', 'attempt_started'):
                f.fail('budget_unknown_order')
            requests[request]['state'] = kind
        else:
            f.fail('reconciliation_requires_separate_authorization')
        previous = f.digest(payload)
        events.append(event)
    return {'events': events, 'last_hash': previous, 'requests': requests,
        'blocked': any(v['state'] != 'settlement' for v in requests.values()),
        'request_count': len(requests), 'input_tokens': sum(v['input_upper'] for v in requests.values()),
        'output_tokens': sum(v['output_upper'] for v in requests.values()),
        'amount': exact_amount_sum(v['amount'] for v in requests.values())}


def exact_amount_sum(values):
    decimals = [money(value) for value in values]
    with localcontext() as context:
        context.prec = 512 + len(str(len(decimals) + 1))
        return str(sum(decimals, Decimal(0)))


@contextmanager
def mock_scope_lock(lock_path):
    # OS-held file lock: no deletion/replacement of lock evidence, no stale bypass.
    import msvcrt
    lock_path = f.path_check(lock_path, ROOT / '.cache/tmp')
    stream = lock_path.open('a+b')
    try:
        if stream.seek(0, 2) == 0:
            stream.write(b'0')
            stream.flush()
        stream.seek(0)
        try:
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            f.fail('budget_lock_conflict')
        try:
            yield
        finally:
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
    finally:
        stream.close()


def append_mock_event(directory, policy, request_id, kind, data):
    state = ledger_read(directory, policy)
    sequence = len(state['events']) + 1
    event = {'schema_version': '1.0', 'sequence': sequence, 'kind': kind,
        'policy_hash': mock_policy_check(policy), 'request_id': request_id,
        'previous_hash': state['last_hash'], 'recorded_at': f.now(), 'data': data}
    return publish_event(directory, sequence, kind, event)


def run_mock_attempt(directory, lock_path, policy, request_id, transport):
    mock_policy_check(policy)
    f.identifier(request_id)
    expected_lock = ROOT / '.cache/tmp' / (policy['scope_id'] + '.lock')
    if Path(lock_path) != expected_lock:
        f.fail('budget_lock_scope_mismatch')
    with mock_scope_lock(expected_lock):
        state = ledger_read(directory, policy)
        if state['blocked']:
            f.fail('budget_unsettled_or_unknown')
        if request_id in state['requests']:
            f.fail('budget_request_already_consumed')
        amount = reserve_amount(policy['input_upper'], policy['output_upper'], policy['input_rate'],
                                policy['output_rate'], policy['unit'], policy['quantum'])
        if (state['request_count'] + 1 > policy['request_limit']
                or state['input_tokens'] + policy['input_upper'] > policy['input_limit']
                or state['output_tokens'] + policy['output_upper'] > policy['output_limit']
                or money(exact_amount_sum((state['amount'], amount))) > money(policy['amount_limit'])):
            f.fail('budget_limit_exceeded')
        reservation = append_mock_event(directory, policy, request_id, 'reservation',
            {'input_upper': policy['input_upper'], 'output_upper': policy['output_upper'], 'amount': amount})
        attempt = append_mock_event(directory, policy, request_id, 'attempt_started', {})
        # A mock callable is invoked exactly once, only after durable events.
        try:
            result = transport()
            if type(result) is not dict or result.get('synthetic') is not True:
                f.fail('mock_transport_result_required')
            usage = validate_mock_usage(result['usage'], policy['input_upper'], policy['output_upper'])
            actual = reserve_amount(usage['input_tokens'], usage['output_tokens'], policy['input_rate'],
                                    policy['output_rate'], policy['unit'], policy['quantum'])
            settlement = append_mock_event(directory, policy, request_id, 'settlement', {'usage': usage, 'amount': actual})
        except Exception:
            # Safe fixed reason only; settlement failures also retain the reservation.
            append_mock_event(directory, policy, request_id, 'unknown_charge', {'reason_code': 'mock_charge_unknown'})
            f.fail('mock_charge_unknown')
        return {'synthetic': True, 'usage': usage, 'cost': actual,
                'event_refs': [reservation, attempt, settlement], 'result': result}


def require_live_budget(policy):
    if policy is None:
        f.fail('call_policy_not_configured')
    f.fail('live_budget_policy_not_verified')
