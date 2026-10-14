"""Initial offline W2-B2 definitions; no live service, credential or policy.

Ledger recovery/exclusion, mock request pipeline, fault evidence and runner are
not implemented yet. Do not run this file as a complete C201-C212 test suite.
"""
from copy import deepcopy
import unittest
import os
from pathlib import Path
from unittest.mock import patch
from contextlib import contextmanager, redirect_stdout, redirect_stderr, ExitStack
import io
import json
import sys
import uuid
import socket

CASE_RESULTS = []
FAULT_RESULTS = []
UPSTREAM_RESULTS = []
BOUNDARY_RESULTS = []
BINDING_RESULTS = []
LOCK_RESULTS = []
from datainsight import feasibility as f
from datainsight import explanation as e
from datainsight import deepseek_call as d
from datainsight import call_budget as b


@contextmanager
def atomic_fault(directory, operation, events, filename=None):
    """Fault only matching staging files; all other I/O follows real methods."""
    original_open, original_rename, original_fsync = Path.open, Path.rename, os.fsync
    descriptors = {}
    def matches(path):
        return path.parent == directory and path.suffix == '.tmp' and (filename is None or path.name == filename)
    def hit(path):
        events.append({'operation': operation, 'path': f.relative(path)})
        raise OSError('controlled_atomic_fault')
    class Wrapped:
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
            if operation == 'write':
                hit(self.path)
            return self.stream.write(data)
        def flush(self):
            if operation == 'flush':
                hit(self.path)
            return self.stream.flush()
        def fileno(self):
            return self.stream.fileno()
        def __getattr__(self, name):
            return getattr(self.stream, name)
    def opened(path, *args, **kwargs):
        if matches(path) and operation == 'open':
            hit(path)
        stream = original_open(path, *args, **kwargs)
        return Wrapped(stream, path) if matches(path) else stream
    def renamed(path, target):
        if matches(path) and operation == 'rename':
            hit(path)
        return original_rename(path, target)
    def synced(fd):
        if fd in descriptors and operation == 'fsync':
            hit(descriptors[fd])
        return original_fsync(fd)
    with patch.object(Path, 'open', opened), patch.object(Path, 'rename', renamed), patch.object(os, 'fsync', synced):
        yield


def response():
    return {'schema_version': '1.0', 'selected_plan_alias': 'p_selected',
        'explanation_sections': [{'section_id': section,
            'text': '原始记录方案仅描述已确认口径，不授权后续操作。',
            'reference_aliases': ['metric_records']} for section in e.SECTIONS],
        'numeric_mentions': [{'value_ref': 'stat_row_count', 'display_role': 'raw_record_count'}]}


def references():
    return {alias: {'value': 0} if alias == 'stat_row_count' else {'controlled': True} for alias in e.ALIASES}


class ExplanationTests(unittest.TestCase):
    def test_unconfigured_live_boundary_never_sends(self):
        with self.assertRaisesRegex(f.BoundaryError, '^call_policy_not_configured$'):
            d.request_explanation(None, None)
        with self.assertRaisesRegex(f.BoundaryError, '^live_provider_protocol_not_verified$'):
            d.request_explanation(None, {'synthetic': True})
        with self.assertRaisesRegex(f.BoundaryError, '^live_budget_policy_not_verified$'):
            b.require_live_budget({'synthetic': True})

    def test_structural_draft_host_value(self):
        result = d.mock_result('controlled-request', 'synthetic-model', f.encoded(response()))
        draft = e.validate_explanation(result, references())
        self.assertEqual(draft['validation_state'], 'structurally_valid_draft')
        self.assertEqual(draft['human_review_state'], 'pending')
        self.assertEqual(draft['host_rendered_numeric_mentions'][0]['value'], 0)

    def test_independent_response_errors(self):
        cases = [('extra', lambda v: v.update(approve=True), 'invalid_object_keys'),
                 ('version', lambda v: v.update(schema_version='unknown'), 'explanation_identity'),
                 ('plan', lambda v: v.update(selected_plan_alias='unknown'), 'explanation_identity'),
                 ('number', lambda v: v['explanation_sections'][0].update(text='总计一万条，增长50%'), 'direct_numeric_text'),
                 ('sql', lambda v: v['explanation_sections'][0].update(text='SELECT secret'), 'unsupported_response_content'),
                 ('alias', lambda v: v['explanation_sections'][0].update(reference_aliases=['unknown']), 'explanation_reference_invalid'),
                 ('numeric', lambda v: v['numeric_mentions'][0].update(value=5), 'invalid_object_keys')]
        for case, mutate, reason in cases:
            valid = response()
            e.validate_explanation(d.mock_result('baseline', 'synthetic-model', f.encoded(valid)), references())
            invalid = deepcopy(valid)
            mutate(invalid)
            with self.subTest(case=case):
                with self.assertRaisesRegex(f.BoundaryError, '^' + reason + '$'):
                    e.validate_explanation(d.mock_result('invalid', 'synthetic-model', f.encoded(invalid)), references())

    def test_decimal_reservation_rounds_up(self):
        result = b.reserve_amount(1, 1, '1', '2', 1000, '0.01')
        self.assertEqual(result, '0.01')
        # A positive excess beyond default Decimal precision must still reserve up.
        self.assertEqual(b.reserve_amount(1, 0, '1.00000000000000000000000000001', '0', 1, '0.01'), '1.01')
        self.assertEqual(b.exact_amount_sum(('1', '0.00000000000000000000000000001')),
                         '1.00000000000000000000000000001')
        for invalid in ('NaN', 'Infinity', '-1'):
            with self.assertRaisesRegex(f.BoundaryError, '^budget_decimal_invalid$'):
                b.money(invalid)
        with self.assertRaisesRegex(f.BoundaryError, '^usage_invalid_or_over_reserved$'):
            b.validate_mock_usage({'input_tokens': True, 'output_tokens': 0}, 1, 1)


class MockPayloadTests(unittest.TestCase):
    def test_complete_body_and_independent_layer_injection(self):
        valid = e.build_mock_payload(0)
        e.validate_mock_payload(valid)
        for case in ('system', 'user', 'schema', 'envelope', 'aggregate'):
            draft = deepcopy(valid)
            body = draft['request_body']
            if case == 'system':
                body['messages'][0]['content'] = 'SENTINEL_SECRET'
            elif case == 'user':
                body['messages'][1]['content']['path'] = 'SENTINEL_PATH'
            elif case == 'schema':
                body['response_schema']['approve'] = True
            elif case == 'envelope':
                body['stream'] = True
            else:
                body['messages'][1]['content']['aggregate']['extra'] = 'SENTINEL_ROW'
            # Even an attacker recomputing the draft hash cannot enlarge the whitelist.
            draft['body_hash'] = f.digest(f.encoded(body))
            with self.subTest(case=case):
                with self.assertRaisesRegex(f.BoundaryError, '^mock_payload_whitelist$'):
                    e.validate_mock_payload(draft)
        self.assertNotIn('user_id', f.encoded(valid['request_body']).decode())
        self.assertNotIn('outputs/', f.encoded(valid['request_body']).decode())


class MockTransportTests(unittest.TestCase):
    def test_total_deadline_remaining_budget_not_reset(self):
        from types import SimpleNamespace
        ticks = iter((0, 10, 10, 59, 59, 59))
        connection = unittest.mock.Mock()
        chunks = iter((b'a', b'b', b''))
        response = SimpleNamespace(status=200, read=lambda size: next(chunks))
        self.assertEqual(d.read_mock_response(0, lambda: next(ticks), connection, response), b'ab')
        self.assertEqual([v.args[0] for v in connection.settimeout.call_args_list], [60, 50, 1])

    def test_timeout_after_blocking_read_not_success(self):
        from types import SimpleNamespace
        ticks = iter((0, 60))
        connection = unittest.mock.Mock()
        response = SimpleNamespace(status=200, read=lambda size: b'completed-too-late')
        with self.assertRaisesRegex(f.BoundaryError, '^mock_total_timeout$'):
            d.read_mock_response(0, lambda: next(ticks), connection, response)
        self.assertEqual(connection.settimeout.call_count, 1)

    def test_exact_limit_and_overflow(self):
        from types import SimpleNamespace
        for extra in (0, 1):
            payload = b'x' * (d.RESPONSE_LIMIT + extra)
            offset = [0]
            def read(size):
                result = payload[offset[0]:offset[0] + size]
                offset[0] += len(result)
                return result
            response = SimpleNamespace(status=200, read=read)
            connection = unittest.mock.Mock()
            if extra:
                with self.assertRaisesRegex(f.BoundaryError, '^response_size_boundary$'):
                    d.read_mock_response(0, lambda: 0, connection, response)
            else:
                self.assertEqual(d.read_mock_response(0, lambda: 0, connection, response), payload)

    def test_redirect_and_http_error_never_reads_body(self):
        from types import SimpleNamespace
        for status, reason in ((302, 'mock_redirect_rejected'), (500, 'mock_http_error')):
            response = SimpleNamespace(status=status, read=unittest.mock.Mock(side_effect=AssertionError('body-read')))
            with self.assertRaisesRegex(f.BoundaryError, '^' + reason + '$'):
                d.read_mock_response(0, lambda: 0, unittest.mock.Mock(), response)
            response.read.assert_not_called()


class MockLedgerTests(unittest.TestCase):
    def setUp(self):
        raw = os.environ.get('W2B2_TEST_RUN')
        if not raw:
            raise RuntimeError('P-B2-MOCK required: W2B2_TEST_RUN missing')
        batch = f.path_check(Path(raw), b.OUTPUT)
        if not batch.is_dir():
            raise RuntimeError('approved_batch_required')
        token_for_alias = batch.name.removeprefix('w2b2-mock-').removeprefix('w2b2-l1-')
        self.batch = b.OUTPUT / ('w2b2-mock-' + token_for_alias)
        token = batch.name.removeprefix('w2b2-mock-').removeprefix('w2b2-l1-')
        method_names = sorted(name for name in type(self).__dict__ if name.startswith('test_'))
        self.method_alias = ('l' if type(self).__name__ == 'L1BudgetTests' else 'm') + str(method_names.index(self._testMethodName)).zfill(2)
        self.policy = {'synthetic': True, 'scope_id': 'synthetic-' + token + '-' + self.method_alias,
            'input_upper': 10, 'output_upper': 10, 'input_rate': '1', 'output_rate': '2',
            'unit': 1000, 'quantum': '0.01', 'request_limit': 2,
            'input_limit': 20, 'output_limit': 20, 'amount_limit': '0.06'}
        f.identifier(self.policy['scope_id'])
        CASE_RESULTS.append({'test_method': self._testMethodName, 'method_alias': self.method_alias,
                             'synthetic_scope_id': self.policy['scope_id']})
        self.directory = b.OUTPUT / ('budget-' + self.policy['scope_id'])
        f.path_check(self.directory, b.OUTPUT)
        self.directory.mkdir()
        self.lock = f.ROOT / '.cache/tmp' / (self.policy['scope_id'] + '.lock')

    def test_durable_order_and_restart_reuse_rejection(self):
        calls = []
        def transport():
            state = b.ledger_read(self.directory, self.policy)
            self.assertEqual([v['kind'] for v in state['events']], ['reservation', 'attempt_started'])
            calls.append('mock-send')
            return {'usage': {'input_tokens': 1, 'output_tokens': 1}, 'synthetic': True}
        result = b.run_mock_attempt(self.directory, self.lock, self.policy, 'request-a', transport)
        self.assertEqual(calls, ['mock-send'])
        self.assertEqual(result['cost'], '0.01')
        self.assertFalse(b.ledger_read(self.directory, self.policy)['blocked'])
        with self.assertRaisesRegex(f.BoundaryError, '^budget_request_already_consumed$'):
            b.run_mock_attempt(self.directory, self.lock, self.policy, 'request-a', transport)
        self.assertEqual(calls, ['mock-send'])

    def test_unknown_charge_retains_and_stops(self):
        calls = []
        def transport():
            calls.append('mock-send')
            raise TimeoutError('controlled')
        with self.assertRaisesRegex(f.BoundaryError, '^mock_charge_unknown$'):
            b.run_mock_attempt(self.directory, self.lock, self.policy, 'request-a', transport)
        state = b.ledger_read(self.directory, self.policy)
        self.assertTrue(state['blocked'])
        self.assertEqual(state['amount'], '0.03')
        with self.assertRaisesRegex(f.BoundaryError, '^budget_unsettled_or_unknown$'):
            b.run_mock_attempt(self.directory, self.lock, self.policy, 'request-b', transport)
        self.assertEqual(calls, ['mock-send'])

    def test_reservation_failure_never_calls_transport(self):
        calls = []
        with patch.object(Path, 'rename', side_effect=OSError('controlled')):
            with self.assertRaises(OSError):
                b.run_mock_attempt(self.directory, self.lock, self.policy, 'request-a',
                    lambda: calls.append('unexpected-send'))
        self.assertEqual(calls, [])
        with self.assertRaisesRegex(f.BoundaryError, '^budget_unpublished_event$'):
            b.ledger_read(self.directory, self.policy)


    def test_mock_call_chain_and_invalid_draft_still_consumes(self):
        draft = e.build_mock_payload(0)
        upstream = f.digest(b'controlled-approved-plan')
        authorization = e.mock_authorize(draft, self.policy, 'request-a', upstream)
        calls = []
        def transport():
            calls.append('mock-send')
            invalid = response()
            invalid['approve'] = True
            return d.mock_result('request-a', 'synthetic-model', f.encoded(invalid),
                                 {'input_tokens': 1, 'output_tokens': 1})
        completed = e.execute_mock(draft, authorization, self.policy, upstream,
                                   self.directory, self.lock, transport)
        with self.assertRaisesRegex(f.BoundaryError, '^invalid_object_keys$'):
            e.validate_explanation(completed['result']['provider_result'], references())
        self.assertEqual(calls, ['mock-send'])
        self.assertEqual(b.ledger_read(self.directory, self.policy)['requests']['request-a']['state'], 'settlement')
        with self.assertRaisesRegex(f.BoundaryError, '^budget_request_already_consumed$'):
            e.execute_mock(draft, authorization, self.policy, upstream,
                           self.directory, self.lock, transport)
        self.assertEqual(calls, ['mock-send'])

    def test_authorization_change_never_sends(self):
        draft = e.build_mock_payload(0)
        upstream = f.digest(b'controlled-approved-plan')
        authorization = e.mock_authorize(draft, self.policy, 'request-a', upstream)
        transport = unittest.mock.Mock(side_effect=AssertionError('unexpected-send'))
        for case in ('body', 'policy', 'upstream', 'forged'):
            body, policy, identity, auth = deepcopy(draft), deepcopy(self.policy), upstream, authorization
            if case == 'body':
                body = e.build_mock_payload(1)
            elif case == 'policy':
                policy['amount_limit'] = '0.07'
            elif case == 'upstream':
                identity = f.digest(b'changed-upstream')
            else:
                auth = {'approved': True}
            reason = 'mock_authorization_required' if case == 'forged' else 'mock_authorization_changed'
            with self.subTest(case=case):
                with self.assertRaisesRegex(f.BoundaryError, '^' + reason + '$'):
                    e.execute_mock(body, auth, policy, identity, self.directory, self.lock, transport)
        transport.assert_not_called()
        self.assertEqual(b.ledger_read(self.directory, self.policy)['events'], [])

    def test_cumulative_request_limit_persists(self):
        calls = []
        def transport():
            calls.append('mock-send')
            return {'usage': {'input_tokens': 1, 'output_tokens': 1}, 'synthetic': True}
        for request in ('request-a', 'request-b'):
            b.run_mock_attempt(self.directory, self.lock, self.policy, request, transport)
        with self.assertRaisesRegex(f.BoundaryError, '^budget_limit_exceeded$'):
            b.run_mock_attempt(self.directory, self.lock, self.policy, 'request-c', transport)
        self.assertEqual(calls, ['mock-send', 'mock-send'])
        self.assertEqual(b.ledger_read(self.directory, self.policy)['request_count'], 2)

    def test_crash_reservation_blocks_restart(self):
        amount = b.reserve_amount(10, 10, '1', '2', 1000, '0.01')
        b.append_mock_event(self.directory, self.policy, 'request-a', 'reservation',
                            {'input_upper': 10, 'output_upper': 10, 'amount': amount})
        transport = unittest.mock.Mock(side_effect=AssertionError('unexpected-send'))
        with self.assertRaisesRegex(f.BoundaryError, '^budget_unsettled_or_unknown$'):
            b.run_mock_attempt(self.directory, self.lock, self.policy, 'request-b', transport)
        transport.assert_not_called()
        self.assertEqual(b.ledger_read(self.directory, self.policy)['amount'], amount)

    def test_actual_lock_competition_never_sends(self):
        transport = unittest.mock.Mock(side_effect=AssertionError('unexpected-send'))
        with b.mock_scope_lock(self.lock):
            with self.assertRaisesRegex(f.BoundaryError, '^budget_lock_conflict$'):
                b.run_mock_attempt(self.directory, self.lock, self.policy, 'request-a', transport)
        transport.assert_not_called()
        self.assertEqual(b.ledger_read(self.directory, self.policy)['events'], [])

    def test_lock_scope_change_rejected_before_send(self):
        transport = unittest.mock.Mock(side_effect=AssertionError('unexpected-send'))
        with self.assertRaisesRegex(f.BoundaryError, '^budget_lock_scope_mismatch$'):
            b.run_mock_attempt(self.directory, self.lock.with_name('different.lock'), self.policy, 'request-a', transport)
        transport.assert_not_called()
        self.assertEqual(b.ledger_read(self.directory, self.policy)['events'], [])

    def test_provider_request_identity_mismatch_retains_reservation(self):
        draft = e.build_mock_payload(0)
        upstream = f.digest(b'controlled-plan')
        auth = e.mock_authorize(draft, self.policy, 'request-a', upstream)
        def transport():
            return d.mock_result('wrong-request', 'synthetic-model', f.encoded(response()),
                                 {'input_tokens': 1, 'output_tokens': 1})
        with self.assertRaisesRegex(f.BoundaryError, '^mock_charge_unknown$'):
            e.execute_mock(draft, auth, self.policy, upstream, self.directory, self.lock, transport)
        self.assertTrue(b.ledger_read(self.directory, self.policy)['blocked'])

    def test_persisted_mock_authorization_restore_and_changes(self):
        draft = e.build_mock_payload(0)
        upstream = f.digest(b'controlled-upstream')
        target = b.OUTPUT / (self.batch.name + '-auth-restore')
        path = e.persist_mock_authorization(target, draft, self.policy, 'request-a', upstream)
        original_bytes = path.read_bytes()
        restored = e.restore_mock_authorization(path, draft, self.policy, upstream, 'request-a')
        self.assertEqual(restored.request_id, 'request-a')
        for case in ('body', 'policy', 'upstream', 'request'):
            body, policy, identity, request = deepcopy(draft), deepcopy(self.policy), upstream, 'request-a'
            if case == 'body':
                body = e.build_mock_payload(1)
            elif case == 'policy':
                policy['amount_limit'] = '0.07'
            elif case == 'upstream':
                identity = f.digest(b'changed-upstream')
            else:
                request = 'request-b'
            with self.subTest(case=case):
                with self.assertRaisesRegex(f.BoundaryError, '^mock_authorization_record_changed$'):
                    e.restore_mock_authorization(path, body, policy, identity, request)
        self.assertEqual(path.read_bytes(), original_bytes)
        with self.assertRaisesRegex(f.BoundaryError, '^output_exists$'):
            e.persist_mock_authorization(target, draft, self.policy, 'request-a', upstream)

    def test_persisted_forged_approval_field_rejected(self):
        draft = e.build_mock_payload(0)
        upstream = f.digest(b'controlled-upstream')
        target = b.OUTPUT / (self.batch.name + '-auth-forged')
        path = e.persist_mock_authorization(target, draft, self.policy, 'request-a', upstream)
        value = f.parse(path.read_bytes())
        value['approved'] = True
        original_read = f.read_bytes
        with patch.object(f, 'read_bytes', side_effect=lambda candidate, root=f.ROOT:
                          f.encoded(value) if candidate == path else original_read(candidate, root)):
            with self.assertRaisesRegex(f.BoundaryError, '^invalid_object_keys$'):
                e.restore_mock_authorization(path, draft, self.policy, upstream, 'request-a')

    def test_persisted_entry_consumed_across_restore(self):
        draft = e.build_mock_payload(0)
        upstream = f.digest(b'controlled-upstream')
        target = b.OUTPUT / (self.batch.name + '-auth-consumed')
        path = e.persist_mock_authorization(target, draft, self.policy, 'request-a', upstream)
        calls = []
        def transport():
            calls.append('mock-send')
            return d.mock_result('request-a', 'synthetic-model', f.encoded(response()),
                                 {'input_tokens': 1, 'output_tokens': 1})
        result = e.execute_persisted_mock(draft, path, self.policy, upstream, 'request-a',
                                          self.directory, self.lock, transport)
        rendered = e.validate_explanation(result['result']['provider_result'], references())
        self.assertEqual(rendered['human_review_state'], 'pending')
        with self.assertRaisesRegex(f.BoundaryError, '^budget_request_already_consumed$'):
            e.execute_persisted_mock(draft, path, self.policy, upstream, 'request-a',
                                     self.directory, self.lock, transport)
        self.assertEqual(calls, ['mock-send'])

    def test_persisted_entry_changed_body_never_reserves(self):
        draft = e.build_mock_payload(0)
        upstream = f.digest(b'controlled-upstream')
        target = b.OUTPUT / (self.batch.name + '-auth-unsent')
        path = e.persist_mock_authorization(target, draft, self.policy, 'request-a', upstream)
        transport = unittest.mock.Mock(side_effect=AssertionError('unexpected-send'))
        with self.assertRaisesRegex(f.BoundaryError, '^mock_authorization_record_changed$'):
            e.execute_persisted_mock(e.build_mock_payload(1), path, self.policy, upstream, 'request-a',
                                     self.directory, self.lock, transport)
        transport.assert_not_called()
        self.assertEqual(b.ledger_read(self.directory, self.policy)['events'], [])

    def test_attempt_publication_failure_retains_unsent_reservation(self):
        calls = []
        original_rename = Path.rename
        def renamed(path, target):
            if path.parent == self.directory and path.name.endswith('-attempt_started.tmp'):
                raise OSError('controlled_attempt_publish_failure')
            return original_rename(path, target)
        with patch.object(Path, 'rename', renamed):
            with self.assertRaises(OSError):
                b.run_mock_attempt(self.directory, self.lock, self.policy, 'request-a',
                    lambda: calls.append('unexpected-send'))
        self.assertEqual(calls, [])
        self.assertTrue((self.directory / 'event-000001-reservation.json').exists())
        self.assertTrue((self.directory / 'event-000002-attempt_started.tmp').exists())
        with self.assertRaisesRegex(f.BoundaryError, '^budget_unpublished_event$'):
            b.ledger_read(self.directory, self.policy)

    def test_settlement_publication_failure_cannot_be_success(self):
        calls = []
        original_rename = Path.rename
        def renamed(path, target):
            if path.parent == self.directory and path.name.endswith('-settlement.tmp'):
                raise OSError('controlled_settlement_publish_failure')
            return original_rename(path, target)
        def transport():
            calls.append('mock-send')
            return {'synthetic': True, 'usage': {'input_tokens': 1, 'output_tokens': 1}}
        with patch.object(Path, 'rename', renamed):
            with self.assertRaisesRegex(f.BoundaryError, '^budget_unpublished_event$'):
                b.run_mock_attempt(self.directory, self.lock, self.policy, 'request-a', transport)
        self.assertEqual(calls, ['mock-send'])
        self.assertTrue((self.directory / 'event-000003-settlement.tmp').exists())
        self.assertFalse((self.directory / 'event-000003-settlement.json').exists())
        # Unknown-charge publication is blocked by residual tmp; retain risk, no cleanup.
        with self.assertRaisesRegex(f.BoundaryError, '^budget_unpublished_event$'):
            b.ledger_read(self.directory, self.policy)

    def test_atomic_ledger_stage_fault_matrix(self):
        for stage in ('reservation', 'attempt_started', 'settlement'):
            for operation in ('open', 'write', 'flush', 'fsync', 'rename'):
                case = stage + '-' + operation
                policy = dict(self.policy, scope_id=self.policy['scope_id'] + '-' + case)
                directory = b.OUTPUT / ('budget-' + policy['scope_id'])
                f.identifier(directory.name)
                f.path_check(directory, b.OUTPUT)
                directory.mkdir()
                lock = f.ROOT / '.cache/tmp' / (policy['scope_id'] + '.lock')
                sequence = {'reservation': '000001', 'attempt_started': '000002', 'settlement': '000003'}[stage]
                filename = 'event-' + sequence + '-' + stage + '.tmp'
                events, calls = [], []
                def transport():
                    calls.append('mock-send')
                    return {'synthetic': True, 'usage': {'input_tokens': 1, 'output_tokens': 1}}
                exception = None
                with atomic_fault(directory, operation, events, filename):
                    try:
                        b.run_mock_attempt(directory, lock, policy, 'request-a', transport)
                    except (OSError, f.BoundaryError) as error:
                        exception = type(error).__name__
                files = sorted(path.name for path in directory.iterdir())
                FAULT_RESULTS.append({'case_id': case, 'kind': 'ledger', 'exception_type': exception,
                    'events': events, 'mock_send_count': len(calls), 'files': files,
                    'directory': f.relative(directory), 'synthetic': True})
                self.assertIsNotNone(exception)
                self.assertTrue(events)
                self.assertEqual(len(calls), 1 if stage == 'settlement' else 0)
                self.assertNotIn('event-' + sequence + '-' + stage + '.json', files)
                if stage == 'settlement':
                    self.assertIn('event-000001-reservation.json', files)
                    self.assertIn('event-000002-attempt_started.json', files)

    def test_atomic_authorization_publication_fault_matrix(self):
        for operation in ('open', 'write', 'flush', 'fsync', 'rename'):
            draft = e.build_mock_payload(0)
            upstream = f.digest(b'controlled-upstream')
            target = b.OUTPUT / (self.batch.name + '-auth-fault-' + operation)
            events = []
            with atomic_fault(target, operation, events):
                with self.assertRaises(OSError):
                    e.persist_mock_authorization(target, draft, self.policy, 'request-a', upstream)
            files = sorted(path.name for path in target.iterdir())
            FAULT_RESULTS.append({'case_id': 'auth-' + operation, 'kind': 'authorization',
                'events': events, 'mock_send_count': 0, 'files': files,
                'directory': f.relative(target), 'synthetic': True})
            self.assertTrue(events)
            self.assertFalse((target / 'final-status.json').exists())
            with self.assertRaisesRegex(f.BoundaryError, '^file_missing_or_size_boundary$'):
                e.restore_mock_authorization(target / 'outbound-authorization.json', draft,
                                             self.policy, upstream, 'request-a')

    def test_authorization_evidence_write_faults(self):
        for case, filename in (('auth-record', 'outbound-authorization.json'), ('auth-binding', 'binding-check.json')):
            draft = e.build_mock_payload(0)
            upstream = f.digest(b'controlled-upstream')
            target = b.OUTPUT / (self.batch.name + '-' + case)
            original = e.save_mock_file
            events = []
            def saving(path, value):
                if path.parent == target and path.name == filename:
                    events.append({'operation': 'evidence_write', 'path': f.relative(path)})
                    raise OSError('controlled_authorization_evidence_failure')
                return original(path, value)
            with patch.object(e, 'save_mock_file', side_effect=saving):
                with self.assertRaises(OSError):
                    e.persist_mock_authorization(target, draft, self.policy, 'request-a', upstream)
            self.assertFalse((target / 'final-status.json').exists())
            FAULT_RESULTS.append({'case_id': case, 'kind': 'authorization_evidence',
                'events': events, 'mock_send_count': 0, 'directory': f.relative(target),
                'files': sorted(path.name for path in target.iterdir())})

    def test_unknown_charge_atomic_fault_matrix(self):
        for operation in ('open', 'write', 'flush', 'fsync', 'rename'):
            policy = dict(self.policy, scope_id=self.policy['scope_id'] + '-unknown-' + operation)
            directory = b.OUTPUT / ('budget-' + policy['scope_id'])
            f.identifier(directory.name)
            f.path_check(directory, b.OUTPUT)
            directory.mkdir()
            lock = f.ROOT / '.cache/tmp' / (policy['scope_id'] + '.lock')
            events, calls = [], []
            def transport():
                calls.append('mock-send')
                raise TimeoutError('controlled')
            with atomic_fault(directory, operation, events, 'event-000003-unknown_charge.tmp'):
                with self.assertRaises(OSError):
                    b.run_mock_attempt(directory, lock, policy, 'request-a', transport)
            self.assertEqual(calls, ['mock-send'])
            self.assertTrue(events)
            self.assertTrue((directory / 'event-000001-reservation.json').exists())
            self.assertTrue((directory / 'event-000002-attempt_started.json').exists())
            self.assertFalse((directory / 'event-000003-unknown_charge.json').exists())
            with self.assertRaisesRegex(f.BoundaryError, '^budget_unsettled_or_unknown$|^budget_unpublished_event$'):
                b.run_mock_attempt(directory, lock, policy, 'request-b',
                    lambda: calls.append('unexpected-send'))
            self.assertEqual(calls, ['mock-send'])
            FAULT_RESULTS.append({'case_id': 'unknown-' + operation, 'kind': 'unknown_charge',
                'events': events, 'mock_send_count': len(calls), 'directory': f.relative(directory),
                'files': sorted(path.name for path in directory.iterdir())})

    def test_mock_call_run_safe_draft_and_evidence(self):
        draft = e.build_mock_payload(0)
        upstream = f.digest(b'controlled-upstream')
        authorization = e.persist_mock_authorization(b.OUTPUT / (self.batch.name + '-call-auth'),
                                                      draft, self.policy, 'request-a', upstream)
        target = b.OUTPUT / (self.batch.name + '-call-valid')
        calls = []
        def transport():
            calls.append('mock-send')
            return d.mock_result('request-a', 'synthetic-model', f.encoded(response()),
                                 {'input_tokens': 1, 'output_tokens': 1})
        result = e.mock_call_run(target, draft, authorization, self.policy, upstream, 'request-a',
                                 self.directory, self.lock, transport, references())
        self.assertEqual(result['exit_status'], 0)
        self.assertEqual(calls, ['mock-send'])
        terminal = f.parse(f.read_bytes(target / 'final-status.json'))
        self.assertEqual(terminal['status'], 'success')
        for filename in e.MOCK_CALL_REFS:
            self.assertTrue((target / filename).is_file())
        self.assertEqual(f.parse(f.read_bytes(target / 'explanation-draft.json'))['human_review_state'], 'pending')

    def test_invalid_raw_response_never_persisted(self):
        draft = e.build_mock_payload(0)
        upstream = f.digest(b'controlled-upstream')
        authorization = e.persist_mock_authorization(b.OUTPUT / (self.batch.name + '-raw-auth'),
                                                      draft, self.policy, 'request-a', upstream)
        target = b.OUTPUT / (self.batch.name + '-raw-failed')
        invalid = response()
        invalid['explanation_sections'][0]['text'] = 'SENTINEL_SECRET_DO_NOT_SAVE'
        result = e.mock_call_run(target, draft, authorization, self.policy, upstream, 'request-a',
            self.directory, self.lock, lambda: d.mock_result('request-a', 'synthetic-model', f.encoded(invalid),
                {'input_tokens': 1, 'output_tokens': 1}), references())
        self.assertEqual(result['exit_status'], 2)
        self.assertEqual(result['mock_transport_calls'], 1)
        self.assertFalse((target / 'validated-response.json').exists())
        self.assertFalse((target / 'explanation-draft.json').exists())
        for path in target.iterdir():
            self.assertNotIn(b'SENTINEL_SECRET_DO_NOT_SAVE', path.read_bytes())
        self.assertEqual(b.ledger_read(self.directory, self.policy)['requests']['request-a']['state'], 'settlement')

    def test_mock_call_evidence_fault_matrix(self):
        pre_send = ('request-metadata.json', 'authorization-reference.json', 'budget-check.json')
        for index, filename in enumerate(e.MOCK_CALL_REFS):
            case = 'cw' + str(index).zfill(2)
            policy = dict(self.policy, scope_id=self.policy['scope_id'] + '-' + case)
            directory = b.OUTPUT / ('budget-' + policy['scope_id'])
            f.identifier(directory.name)
            f.path_check(directory, b.OUTPUT)
            directory.mkdir()
            lock = f.ROOT / '.cache/tmp' / (policy['scope_id'] + '.lock')
            draft = e.build_mock_payload(0)
            upstream = f.digest(b'controlled-upstream')
            auth = e.persist_mock_authorization(b.OUTPUT / (self.batch.name + '-' + case + '-auth'),
                                                draft, policy, 'request-a', upstream)
            target = b.OUTPUT / (self.batch.name + '-' + case + '-call')
            events, calls = [], []
            original = e.save_mock_file
            def saving(path, value):
                if path.parent == target and path.name == filename:
                    events.append({'operation': 'evidence-write', 'path': f.relative(path)})
                    raise OSError('controlled_mock_call_evidence_failure')
                return original(path, value)
            def transport():
                calls.append('mock-send')
                return d.mock_result('request-a', 'synthetic-model', f.encoded(response()),
                                     {'input_tokens': 1, 'output_tokens': 1})
            with patch.object(e, 'save_mock_file', side_effect=saving):
                result = e.mock_call_run(target, draft, auth, policy, upstream, 'request-a',
                                         directory, lock, transport, references())
            terminal = f.parse(f.read_bytes(target / 'final-status.json'))
            FAULT_RESULTS.append({'case_id': case, 'kind': 'call-evidence', 'filename': filename,
                'events': events, 'result': result, 'terminal': terminal,
                'mock_send_count': len(calls), 'directory': f.relative(target),
                'ledger_state': b.ledger_read(directory, policy)})
            self.assertEqual(result['exit_status'], 2)
            self.assertEqual(terminal['status'], 'failed')
            self.assertTrue(events)
            self.assertEqual(len(calls), 0 if filename in pre_send else 1)

    def test_mock_call_atomic_status_fault_matrix(self):
        for operation in ('open', 'write', 'flush', 'fsync', 'rename'):
            case = 'cp-' + operation
            policy = dict(self.policy, scope_id=self.policy['scope_id'] + '-' + case)
            directory = b.OUTPUT / ('budget-' + policy['scope_id'])
            f.identifier(directory.name)
            f.path_check(directory, b.OUTPUT)
            directory.mkdir()
            lock = f.ROOT / '.cache/tmp' / (policy['scope_id'] + '.lock')
            draft = e.build_mock_payload(0)
            upstream = f.digest(b'controlled-upstream')
            auth = e.persist_mock_authorization(b.OUTPUT / (self.batch.name + '-' + case + '-auth'),
                                                draft, policy, 'request-a', upstream)
            target = b.OUTPUT / (self.batch.name + '-' + case + '-call')
            events, calls = [], []
            def transport():
                calls.append('mock-send')
                return d.mock_result('request-a', 'synthetic-model', f.encoded(response()),
                                     {'input_tokens': 1, 'output_tokens': 1})
            with atomic_fault(target, operation, events):
                result = e.mock_call_run(target, draft, auth, policy, upstream, 'request-a',
                                         directory, lock, transport, references())
            files = sorted(path.name for path in target.iterdir())
            FAULT_RESULTS.append({'case_id': case, 'kind': 'call-publication', 'events': events,
                'result': result, 'mock_send_count': len(calls), 'directory': f.relative(target),
                'files': files, 'ledger_state': b.ledger_read(directory, policy)})
            self.assertEqual(result['exit_status'], 2)
            self.assertFalse(result['failure_evidence_persisted'])
            self.assertEqual(calls, ['mock-send'])
            self.assertGreaterEqual(len(events), 2)
            self.assertNotIn('final-status.json', files)
            self.assertEqual(b.ledger_read(directory, policy)['requests']['request-a']['state'], 'settlement')

    def test_corrupt_event_rejected_without_send(self):
        target = self.directory / 'event-000001-reservation.json'
        # Newly created corrupt fixture, not mutation of a previously published event.
        with target.open('xb') as stream:
            stream.write(b'{"unexpected":true}')
        transport = unittest.mock.Mock(side_effect=AssertionError('unexpected-send'))
        with self.assertRaisesRegex(f.BoundaryError, '^invalid_object_keys$'):
            b.run_mock_attempt(self.directory, self.lock, self.policy, 'request-a', transport)
        transport.assert_not_called()


class ApprovedPlanGateTests(unittest.TestCase):
    def test_synthetic_full_chain_approve_and_stop_decisions(self):
        from test_w2b1 import PlanningChainTests, review_spec
        from datainsight import planning as planning
        raw = os.environ.get('W2B2_TEST_RUN')
        if not raw:
            raise RuntimeError('P-B2-MOCK required')
        batch = f.path_check(Path(raw), b.OUTPUT)
        for decision in ('approve', 'reject', 'cancel'):
            helper = PlanningChainTests(methodName='test_B103_candidate_and_review_restore')
            helper.batch = batch
            helper.work = f.ROOT / 'outputs/_scratch' / batch.name / self._testMethodName
            helper.work.mkdir(parents=True, exist_ok=True)
            with patch.object(planning, 'OUTPUT', b.OUTPUT):
                chain, chain_patches = helper.chain(decision)
                with chain_patches:
                    source = b.OUTPUT / (chain['prefix'] + '-candidates')
                    status, _ = helper.run_cli(['candidates', '--output-dir', str(source)])
                    self.assertEqual(status, 0)
                    review = b.OUTPUT / (chain['prefix'] + '-review')
                    spec = review_spec(decision)
                    argv = ['review', '--plan-set', str(source / 'candidate-plans.json'), '--decision', decision,
                        '--actor', 'controlled_test_actor', '--confirmed-at', spec['confirmed_at'], '--output-dir', str(review)]
                    if decision == 'approve':
                        argv += ['--selected-plan-id', spec['selected_plan_id'], '--selected-plan-version', spec['selected_plan_version'],
                                 '--metric-definition-hash', spec['metric_definition_hash'], '--confirm-metric-definition']
                    status, _ = helper.run_cli(argv)
                    self.assertEqual(status, 0)
                    stage = chain['root'] / 'explanation-stage.json'
                    with stage.open('xb') as stream:
                        stream.write('总判定：通过; synthetic fixture only'.encode())
                    with ExitStack() as stack:
                        stack.enter_context(patch.object(e, 'REVIEW', review / 's3-review.json'))
                        stack.enter_context(patch.object(e, 'ACCEPTANCE', stage))
                        original_profile_loader = f.load_accepted_profile
                        def profile_loader(profile_ref, acceptance_ref):
                            if profile_ref == f.LEGACY and acceptance_ref == f.ACCEPTANCE:
                                return original_profile_loader(chain['package'] / 'profile.json',
                                    chain['package'] / 'fixture-acceptance.json')
                            return original_profile_loader(profile_ref, acceptance_ref)
                        stack.enter_context(patch.object(f, 'load_accepted_profile', side_effect=profile_loader))
                        if decision == 'approve':
                            plan = e.load_approved_plan(e.REVIEW)
                            self.assertEqual(plan.references['stat_row_count']['value'], 0)
                            with self.assertRaisesRegex(f.BoundaryError, '^provider_configuration_not_verified$'):
                                e.build_reviewable_payload(plan)
                            actual = 'approved_plan_loaded_live_payload_stopped'
                        else:
                            with self.assertRaisesRegex(f.BoundaryError, '^s3_not_approved$'):
                                e.load_approved_plan(e.REVIEW)
                            actual = 's3_not_approved'
                    CASE_RESULTS.append({'case_id': decision, 'test': self._testMethodName,
                        'actual': actual, 'patch_scope': 'fixed constants to new synthetic chain only; real verifiers',
                        'not_user_confirmation': True})


    def test_l1_upstream_independent_changes(self):
        from test_w2b1 import PlanningChainTests, review_spec
        from datainsight import planning as planning
        from datainsight import planning_methods
        batch = Path(os.environ['W2B2_TEST_RUN'])
        for case in ('approve-baseline', 'missing-terminal', 'missing-reference', 'data-change', 'rules-change', 'registry-change'):
            helper = PlanningChainTests(methodName='test_B103_candidate_and_review_restore')
            helper.batch = batch
            helper.work = f.ROOT / 'outputs/_scratch' / batch.name / self._testMethodName
            helper.work.mkdir(parents=True, exist_ok=True)
            with patch.object(planning, 'OUTPUT', b.OUTPUT):
                chain, patches = helper.chain(case)
                with patches, ExitStack() as setup:
                    source = b.OUTPUT / (chain['prefix'] + '-candidates')
                    self.assertEqual(helper.run_cli(['candidates', '--output-dir', str(source)])[0], 0)
                    review = b.OUTPUT / (chain['prefix'] + '-review')
                    spec = review_spec()
                    self.assertEqual(helper.run_cli(['review', '--plan-set', str(source / 'candidate-plans.json'),
                        '--decision', 'approve', '--selected-plan-id', spec['selected_plan_id'],
                        '--selected-plan-version', spec['selected_plan_version'], '--metric-definition-hash', spec['metric_definition_hash'],
                        '--confirm-metric-definition', '--actor', 'controlled_test_actor', '--confirmed-at', spec['confirmed_at'],
                        '--output-dir', str(review)])[0], 0)
                    stage = chain['root'] / 'explanation-stage.json'
                    with stage.open('xb') as stream:
                        stream.write('总判定：通过; synthetic only'.encode())
                    setup.enter_context(patch.object(e, 'REVIEW', review / 's3-review.json'))
                    setup.enter_context(patch.object(e, 'ACCEPTANCE', stage))
                    original_loader = f.load_accepted_profile
                    def loader(profile, acceptance):
                        if profile == f.LEGACY and acceptance == f.ACCEPTANCE:
                            return original_loader(chain['package'] / 'profile.json', chain['package'] / 'fixture-acceptance.json')
                        return original_loader(profile, acceptance)
                    setup.enter_context(patch.object(f, 'load_accepted_profile', side_effect=loader))
                    baseline = e.load_approved_plan(e.REVIEW)
                    transport = unittest.mock.Mock(side_effect=AssertionError('unexpected-send'))
                    actual, target = 'accepted', None
                    expected = 'accepted'
                    with ExitStack() as change:
                        if case in ('missing-terminal', 'missing-reference', 'data-change'):
                            target = review / ('final-status.json' if case == 'missing-terminal' else 'reference-check.json')
                            original_read = f.read_bytes
                            if case == 'data-change':
                                target = chain['package'] / 'profile.json'
                                changed = f.parse(original_read(target))
                                changed['dataset_version'] = f.digest(b'L1-changed-data')
                                expected = 'fixture_acceptance'
                            else:
                                expected = 'file_missing_or_size_boundary'
                            def reader(path, root=f.ROOT):
                                if path == target:
                                    if case == 'data-change':
                                        return f.encoded(changed)
                                    f.fail('file_missing_or_size_boundary')
                                return original_read(path, root)
                            change.enter_context(patch.object(f, 'read_bytes', side_effect=reader))
                        elif case == 'rules-change':
                            changed = dict(f.rules_module.registered_rules(), ruleset_version='l1', ruleset_hash=f.digest(b'L1-rules'))
                            change.enter_context(patch.object(f.rules_module, 'registered_rules', return_value=changed))
                            expected = 'diagnosis_or_rules_changed'
                        elif case == 'registry-change':
                            changed = dict(planning_methods.registered_methods(), registry_version='l1', registry_hash=f.digest(b'L1-registry'))
                            change.enter_context(patch.object(planning_methods, 'registered_methods', return_value=changed))
                            expected = 'candidate_plan_changed'
                        try:
                            e.load_approved_plan(e.REVIEW)
                        except f.BoundaryError as error:
                            actual = str(error)
                    transport.assert_not_called()
                    UPSTREAM_RESULTS.append({'case_id': case, 'baseline_identity': baseline.identity,
                        'expected': expected, 'actual': actual, 'matches': expected == actual,
                        'target': f.relative(target) if target else None, 'transport_calls': 0,
                        'scope': 'independent synthetic chain; narrow byte/registry patch; real verifiers'})
                    self.assertEqual(actual, expected)


class L1BudgetTests(MockLedgerTests):
    # Only L1 methods; inherited original methods stay in MockLedgerTests suite.
    def test_l1_boundaries(self):
        for dimension in ('input', 'output', 'amount'):
            for variant in ('exact', 'over'):
                case = dimension + '-' + variant
                policy = dict(self.policy, scope_id=self.policy['scope_id'] + '-' + case,
                              request_limit=10, input_limit=100, output_limit=100, amount_limit='1')
                # First settlement uses one token each; next reservation uses ten.
                if dimension == 'input':
                    policy['input_limit'] = 11 if variant == 'exact' else 10
                elif dimension == 'output':
                    policy['output_limit'] = 11 if variant == 'exact' else 10
                else:
                    first = b.reserve_amount(1, 1, '1', '2', 1000, '0.01')
                    next_amount = b.reserve_amount(10, 10, '1', '2', 1000, '0.01')
                    policy['amount_limit'] = b.exact_amount_sum((first, next_amount)) if variant == 'exact' else next_amount
                directory, lock = self.new_case_scope(policy)
                calls = []
                def transport():
                    calls.append('mock-send')
                    return {'synthetic': True, 'usage': {'input_tokens': 1, 'output_tokens': 1}}
                b.run_mock_attempt(directory, lock, policy, 'first', transport)
                before = b.ledger_read(directory, policy)
                actual = 'accepted'
                try:
                    b.run_mock_attempt(directory, lock, policy, 'second', transport)
                except f.BoundaryError as error:
                    actual = str(error)
                after = b.ledger_read(directory, policy)
                expected = 'accepted' if variant == 'exact' else 'budget_limit_exceeded'
                BOUNDARY_RESULTS.append({'case_id': case, 'expected': expected, 'actual': actual,
                    'policy': policy, 'before': before, 'after': after, 'second_calls': len(calls) - 1})
                self.assertEqual(actual, expected)
                self.assertEqual(len(calls) - 1, 1 if variant == 'exact' else 0)
                if variant == 'over':
                    self.assertEqual(before, after)

    def new_case_scope(self, policy):
        directory = b.OUTPUT / ('budget-' + policy['scope_id'])
        f.identifier(directory.name)
        f.path_check(directory, b.OUTPUT)
        directory.mkdir()
        return directory, f.ROOT / '.cache/tmp' / (policy['scope_id'] + '.lock')

    def test_l1_event_bindings(self):
        for case in ('sequence-gap', 'previous-hash', 'policy-hash'):
            policy = dict(self.policy, scope_id=self.policy['scope_id'] + '-' + case)
            directory, lock = self.new_case_scope(policy)
            b.run_mock_attempt(directory, lock, policy, 'first',
                lambda: {'synthetic': True, 'usage': {'input_tokens': 1, 'output_tokens': 1}})
            baseline = b.ledger_read(directory, policy)
            original_read = f.read_bytes
            if case == 'sequence-gap':
                original_iter = Path.iterdir
                def listing(path):
                    values = list(original_iter(path))
                    return iter([v for v in values if not v.name.startswith('event-000002-')]) if path == directory else iter(values)
                context = patch.object(Path, 'iterdir', listing)
                expected = 'budget_sequence_gap'
            else:
                target = directory / 'event-000002-attempt_started.json'
                changed = f.parse(original_read(target))
                changed['previous_hash' if case == 'previous-hash' else 'policy_hash'] = f.digest(b'changed-L1-binding')
                context = patch.object(f, 'read_bytes', side_effect=lambda path, root=f.ROOT:
                    f.encoded(changed) if path == target else original_read(path, root))
                expected = 'budget_event_binding'
            results = []
            transport = unittest.mock.Mock(side_effect=AssertionError('unexpected-send'))
            with context:
                for entry, action in (('restore', lambda: b.ledger_read(directory, policy)),
                    ('attempt', lambda: b.run_mock_attempt(directory, lock, policy, 'second', transport))):
                    actual = None
                    try:
                        action()
                    except f.BoundaryError as error:
                        actual = str(error)
                    results.append({'entry': entry, 'expected': expected, 'actual': actual})
            transport.assert_not_called()
            self.assertEqual(baseline, b.ledger_read(directory, policy))
            BINDING_RESULTS.append({'case_id': case, 'baseline': baseline, 'checks': results, 'transport_calls': 0})
            self.assertTrue(all(v['actual'] == expected for v in results))

    def test_l1_lock_lifecycle(self):
        import msvcrt
        for case in ('open-fail', 'acquire-fail', 'release-normal', 'release-fail', 'close-fail'):
            policy = dict(self.policy, scope_id=self.policy['scope_id'] + '-' + case)
            directory, lock = self.new_case_scope(policy)
            calls, events = [], []
            def transport():
                calls.append('mock-send')
                return {'synthetic': True, 'usage': {'input_tokens': 1, 'output_tokens': 1}}
            original_open, original_locking = Path.open, msvcrt.locking
            class Closing:
                def __init__(self, stream):
                    self.stream = stream
                def close(self):
                    self.stream.close()
                    events.append('real_close_then_fault')
                    raise OSError('controlled_close_failure')
                def __getattr__(self, name):
                    return getattr(self.stream, name)
            def opened(path, *args, **kwargs):
                if path == lock and case == 'open-fail':
                    events.append('open_fault')
                    raise OSError('controlled_lock_open')
                stream = original_open(path, *args, **kwargs)
                return Closing(stream) if path == lock and case == 'close-fail' else stream
            def locking(fd, mode, count):
                if (case == 'acquire-fail' and mode == msvcrt.LK_NBLCK) or (case == 'release-fail' and mode == msvcrt.LK_UNLCK):
                    events.append('acquire_fault' if mode == msvcrt.LK_NBLCK else 'release_fault')
                    raise OSError('controlled_locking_fault')
                return original_locking(fd, mode, count)
            actual = 'success'
            with patch.object(Path, 'open', opened), patch.object(msvcrt, 'locking', locking):
                try:
                    b.run_mock_attempt(directory, lock, policy, 'first', transport)
                except (OSError, f.BoundaryError) as error:
                    actual = str(error) if type(error) is f.BoundaryError else 'OSError'
            if case == 'release-normal':
                b.run_mock_attempt(directory, lock, policy, 'second', transport)
            expected = 'success' if case == 'release-normal' else 'budget_lock_conflict' if case == 'acquire-fail' else 'OSError'
            state = b.ledger_read(directory, policy)
            LOCK_RESULTS.append({'case_id': case, 'expected': expected, 'actual': actual,
                'events': events, 'transport_calls': len(calls), 'ledger_state': state,
                'lock_exists': lock.exists(), 'lock_path': f.relative(lock),
                'resource_cleanup': 'real stream.close always; close-fail injected after real close; no unlink'})
            self.assertEqual(actual, expected)
            self.assertEqual(len(calls), 2 if case == 'release-normal' else 0 if case in ('open-fail', 'acquire-fail') else 1)
            if calls:
                self.assertEqual(state['requests']['first']['state'], 'settlement')


ACTIVE_BATCH = None


def evidence_runner(l1=False):
    global ACTIVE_BATCH
    environment = f.environment()
    if Path.cwd() != f.ROOT:
        raise RuntimeError('project_cwd_required')
    batch = b.OUTPUT / (('w2b2-l1-' if l1 else 'w2b2-mock-') + uuid.uuid4().hex)
    f.path_check(batch, b.OUTPUT)
    f.identifier(batch.name)
    batch.mkdir(parents=True)
    ACTIVE_BATCH = batch
    os.environ['W2B2_TEST_RUN'] = str(batch)
    token = batch.name.removeprefix('w2b2-mock-').removeprefix('w2b2-l1-')
    def save(name, value):
        path = batch / name
        f.path_check(path, b.OUTPUT)
        payload = value if type(value) is bytes else f.encoded(value)
        with path.open('xb') as stream:
            stream.write(payload)
    protected = [f.ROOT / name for name in ('src/datainsight/explanation.py',
        'src/datainsight/deepseek_call.py', 'src/datainsight/call_budget.py',
        'src/datainsight/planning.py', 'src/datainsight/planning_methods.py',
        'src/datainsight/feasibility.py', 'src/datainsight/feasibility_rules.py',
        'docs/acceptance/W2-B2-v1.md', 'docs/decisions/ADR-003-directory-and-evidence-layout.md',
        'docs/decisions/ADR-005-approval-responsibility-and-confirmation-time.md',
        'docs/decisions/ADR-006-W2B2-model-explanation-and-call-gates.md',
        'configs/w1b-read-contract-v1.json', 'configs/w2a-question-v1.json')]
    def identities():
        return [{'path': f.relative(path), 'sha256': f.digest(f.read_bytes(path))} for path in protected]
    started = f.now()
    before = identities()
    save('protected-files-before.json', before)
    snapshot = batch / 'source-snapshots'
    snapshot.mkdir()
    source = f.path_check(Path(__file__).absolute(), f.ROOT / 'tests')
    save('source-snapshots/test_w2b2.py', source.read_bytes())
    save('source-identity.json', {'protected_sources': before, 'test_sha256': f.digest(source.read_bytes()),
        'helper_identities': [{'path': name, 'sha256': f.digest(f.read_bytes(f.ROOT / name))}
                             for name in ('tests/test_w2a.py', 'tests/test_w2b1.py')]})
    shell = "cd /d/MyPythonProjects/datainsight && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH='D:\\MyPythonProjects\\datainsight\\src;D:\\MyPythonProjects\\datainsight\\tests' TEMP='D:\\MyPythonProjects\\datainsight\\.cache\\tmp' TMP='D:\\MyPythonProjects\\datainsight\\.cache\\tmp' TMPDIR='D:\\MyPythonProjects\\datainsight\\.cache\\tmp' .venv/Scripts/python.exe -B -m test_w2b2 --w2b2-evidence"
    if l1:
        shell = shell.replace('--w2b2-evidence', '--w2b2-l1-evidence')
    save('batch-command.json', {'argv': sys.argv, 'shell_transcript': shell,
        'executable': sys.executable, 'cwd': str(Path.cwd()), 'batch_id': batch.name})
    save('batch-environment.json', environment)
    save('authorization-record.json', {'confirmation_actor': 'user', 'confirmed_at': 'not_provided',
        'confirmation_basis': 'P-B2-MOCK single offline batch approval',
        'recorded_at': f.now(), 'recorded_at_source': 'Python datetime.now(timezone.utc)',
        'recorded_at_status': 'available', 'authorization_scope': 'synthetic tests only; no credentials/network/paid requests',
        'technical_responsibility': '技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。'})
    reads, blocked_calls = [], []
    original_open = Path.open
    def opened(path, *args, **kwargs):
        mode = args[0] if args else kwargs.get('mode', 'r')
        reads.append({'path': f.relative(path) if f.ROOT in path.parents else str(path), 'mode': mode})
        if path.suffix.lower() == '.csv':
            raise AssertionError('raw_csv_open')
        return original_open(path, *args, **kwargs)
    def network(*args, **kwargs):
        blocked_calls.append('network_attempt')
        raise AssertionError('network_attempt')
    log, stdout, stderr = io.StringIO(), io.StringIO(), io.StringIO()
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(cls) for cls in
        (ExplanationTests, MockPayloadTests, MockTransportTests, MockLedgerTests, ApprovedPlanGateTests))
    if l1:
        suite.addTests(L1BudgetTests(name) for name in ('test_l1_boundaries', 'test_l1_event_bindings', 'test_l1_lock_lifecycle'))
    with patch.object(Path, 'open', opened), patch.object(socket.socket, 'connect', side_effect=network), \
            patch.object(socket, 'getaddrinfo', side_effect=network), redirect_stdout(stdout), redirect_stderr(stderr):
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    save('test.log', log.getvalue().encode('utf-8'))
    save('case-results.json', CASE_RESULTS)
    save('fault-results.json', FAULT_RESULTS)
    if l1:
        save('upstream-gate-results.json', UPSTREAM_RESULTS)
        save('budget-boundary-results.json', BOUNDARY_RESULTS)
        save('ledger-binding-results.json', BINDING_RESULTS)
        save('lock-lifecycle-results.json', LOCK_RESULTS)
    save('read-observation.json', {'events': reads, 'blocked_calls': blocked_calls,
        'scope': 'Path.open/socket connect/getaddrinfo around test suite only; not native/system isolation'})
    save('stream-observation.json', {'stdout': stdout.getvalue(), 'stderr': stderr.getvalue(), 'real_provider_calls': 0})
    after = identities()
    save('protected-files-after.json', after)
    roots = [(batch, 'mock_evidence')]
    for path in sorted(b.OUTPUT.iterdir()):
        if (path.name.startswith(batch.name + '-') or path.name.startswith('w2b2-mock-' + token + '-')
                or path.name.startswith('budget-synthetic-' + token + '-')):
            roots.append((path, 'mock_product'))
    scratch = f.ROOT / 'outputs/_scratch' / batch.name
    if scratch.exists():
        roots.append((scratch, 'fixture_input'))
    def inventory():
        files = []
        def visit(path, category):
            f.path_check(path, f.ROOT)
            if path.is_dir():
                for child in sorted(path.iterdir()):
                    visit(child, category)
            else:
                if path.suffix not in ('.json', '.tmp', '.log', '.py', '.lock'):
                    raise RuntimeError('unknown_artifact_family')
                payload = path.read_bytes()
                files.append({'path': f.relative(path), 'category': category,
                              'size': len(payload), 'sha256': f.digest(payload)})
        for path, category in roots:
            visit(path, category)
        for path in sorted((f.ROOT / '.cache/tmp').iterdir()):
            if path.name.startswith('synthetic-' + token + '-') and path.suffix == '.lock':
                visit(path, 'mock_lock_state')
        return files
    files = inventory()
    findings, exclusions, scanned = [], [], []
    markers = ('SENTINEL_SECRET', 'SENTINEL_PATH', 'SENTINEL_ROW')
    for item in files:
        if item['category'] == 'fixture_input' or 'source-snapshots/' in item['path']:
            exclusions.append({'path': item['path'], 'reason': 'intentional_fixture/test_source'})
            continue
        data = (f.ROOT / item['path']).read_bytes()
        scanned.append(item['path'])
        for marker in markers:
            count = data.count(marker.encode())
            if count:
                findings.append({'marker_id': marker.removeprefix('SENTINEL_'), 'path': item['path'], 'count': count})
    for channel, text in (('stdout', stdout.getvalue()), ('stderr', stderr.getvalue()), ('test.log', log.getvalue())):
        for marker in markers:
            if marker in text:
                findings.append({'marker_id': marker.removeprefix('SENTINEL_'), 'stream': channel})
    save('privacy-scan.json', {'scanned_files': scanned, 'streams': ['stdout', 'stderr', 'test.log'],
        'findings': findings, 'exclusions': exclusions, 'trace_scope': 'no separate trace'})
    self_reports = ('artifact-inventory.json', 'privacy-scan.json', 'batch-result.json', 'batch-status.json')
    save('artifact-inventory.json', {'files': files, 'self_reports': list(self_reports),
        'reason': 'self-referential reports exclude self-hash; not product-output exclusion'})
    covered = {v['path'] for v in files} | {f.relative(batch / name) for name in self_reports}
    missing = {v['path'] for v in inventory()} - covered
    required_faults = {(kind, case) for kind, cases in (
        ('ledger', [stage + '-' + op for stage in ('reservation', 'attempt_started', 'settlement')
                    for op in ('open', 'write', 'flush', 'fsync', 'rename')]),
        ('authorization', ['auth-' + op for op in ('open', 'write', 'flush', 'fsync', 'rename')]),
        ('authorization_evidence', ['auth-record', 'auth-binding']),
        ('unknown_charge', ['unknown-' + op for op in ('open', 'write', 'flush', 'fsync', 'rename')]),
        ('call-evidence', ['cw' + str(i).zfill(2) for i in range(len(e.MOCK_CALL_REFS))]),
        ('call-publication', ['cp-' + op for op in ('open', 'write', 'flush', 'fsync', 'rename')]))
        for case in cases}
    missing_faults = required_faults - {(v['kind'], v['case_id']) for v in FAULT_RESULTS}
    l1_complete = not l1 or (
        {v['case_id'] for v in UPSTREAM_RESULTS} == {'approve-baseline', 'missing-terminal', 'missing-reference', 'data-change', 'rules-change', 'registry-change'}
        and all(v['matches'] for v in UPSTREAM_RESULTS)
        and {v['case_id'] for v in BOUNDARY_RESULTS} == {dim + '-' + variant for dim in ('input', 'output', 'amount') for variant in ('exact', 'over')}
        and all(v['actual'] == v['expected'] for v in BOUNDARY_RESULTS)
        and {v['case_id'] for v in BINDING_RESULTS} == {'sequence-gap', 'previous-hash', 'policy-hash'}
        and all(c['actual'] == c['expected'] for v in BINDING_RESULTS for c in v['checks'])
        and {v['case_id'] for v in LOCK_RESULTS} == {'open-fail', 'acquire-fail', 'release-normal', 'release-fail', 'close-fail'}
        and all(v['actual'] == v['expected'] for v in LOCK_RESULTS))
    success = result.wasSuccessful() and before == after and not findings and not missing and not blocked_calls and not missing_faults and l1_complete
    status = 0 if success else 2
    save('batch-result.json', {'tests_run': result.testsRun, 'failures': len(result.failures),
        'errors': len(result.errors), 'exit_status': status, 'real_provider_calls': 0,
        'protection_unchanged': before == after, 'uncovered_paths': sorted(missing),
        'missing_fault_cases': sorted(missing_faults), 'l1_complete': l1_complete,
        'live_provider_protocol': 'not_verified', 'final_acceptance': 'not_performed'})
    save('batch-status.json', {'status': 'success' if success else 'failed', 'exit_status': status,
        'started_at': started, 'completed_at': f.now(), 'final_acceptance': 'not_performed',
        'scope': 'offline mock only; C212 real call untested'})
    print(json.dumps({'batch': str(batch), 'exit_status': status}))
    return status


if __name__ == '__main__':
    if sys.argv[1:] in (['--w2b2-evidence'], ['--w2b2-l1-evidence']):
        try:
            status = evidence_runner(l1=sys.argv[1:] == ['--w2b2-l1-evidence'])
        except Exception as error:
            persisted = False
            if ACTIVE_BATCH is not None:
                try:
                    target = ACTIVE_BATCH / 'batch-status.json'
                    if not target.exists():
                        with target.open('xb') as stream:
                            stream.write(f.encoded({'status': 'failed', 'exit_status': 2,
                                'exception_type': type(error).__name__, 'final_acceptance': 'not_performed'}))
                        persisted = True
                except Exception:
                    pass
            print(json.dumps({'status': 'failed', 'exit_status': 2,
                'exception_type': type(error).__name__, 'failure_evidence_persisted': persisted}))
            status = 2
        raise SystemExit(status)
    unittest.main()
