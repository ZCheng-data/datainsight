"""Closed W2-A rules. No engine, model, SQL execution or user rules."""
from pathlib import Path
import hashlib

RULESET_ID = 'W2-A'
VERSION = 'v1'
RULE_IDS = ('M-BEHAVIOUR-RECORDS', 'P-GMV', 'P-STRICT-FUNNEL',
            'Q-NULL', 'Q-DUPLICATE-CANDIDATE', 'Q-TIME-SEMANTICS')
LIMITATIONS = [
    'Raw records and behaviour codes are not orders or payments.',
    'Duplicate candidates are not errors; no deletion.',
    'Zero NULL does not establish absence of quality problems.',
    'Integer timestamps do not establish dates, timezone or ordered links.',
    'Historical profile does not verify the current source CSV.',
    'No population, causal or business-effect inference.',
]


def registered_rules():
    return {'ruleset_id': RULESET_ID, 'ruleset_version': VERSION,
            'ruleset_hash': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'rule_ids': list(RULE_IDS)}


def evaluate(question, profile, rules):
    if rules != registered_rules():
        raise ValueError('unregistered_rules')
    checks, observations, gaps, eligible = [], [], [], []
    fields = {item['name'] for item in profile['reading_schema']}
    refs = profile['metric_refs']

    def check(rule, premise, state, evidence):
        checks.append({'rule_id': rule, 'rule_version': VERSION,
                       'premise': premise, 'state': state, 'evidence': evidence})

    for rule, metric in (('Q-NULL', 'columns'),
                         ('Q-DUPLICATE-CANDIDATE', 'duplicates'),
                         ('Q-TIME-SEMANTICS', 'timestamp')):
        observations.append({'rule_id': rule, 'rule_version': VERSION,
                             'metric_ref': refs.get(metric),
                             'interpretation': 'tool observation only; semantics unconfirmed'})
    if question is None:
        state, capability = 'needs_question', None
    elif question['intent'] not in ('behaviour_record_counts', 'gmv', 'strict_funnel'):
        state, capability = 'unsupported_request', None
    else:
        state = 'valid'
        intent = question['intent']
        schema_ref = profile['profile_identity']['profile_ref'] + '#reading_schema'
        if intent == 'behaviour_record_counts':
            check('M-BEHAVIOUR-RECORDS', 'behaviour column',
                  'met' if 'behaviour' in fields else 'unmet', schema_ref)
            check('M-BEHAVIOUR-RECORDS', 'referenced aggregate tool result',
                  'met' if refs.get('behaviours') else 'unknown', refs.get('behaviours'))
            if 'behaviour' not in fields:
                capability = 'unsupported'
                gaps.append('missing_prerequisite: behaviour column')
            elif not refs.get('behaviours'):
                capability = 'conditional'
                gaps.append('unknown_prerequisite: referenced behaviour result')
            else:
                capability = 'supported'
                eligible.append('M-BEHAVIOUR-RECORDS')
        elif intent == 'gmv':
            check('P-GMV', 'amount field', 'unmet', schema_ref)
            check('P-GMV', 'amount and order definitions', 'unknown', schema_ref)
            capability = 'unsupported'
            gaps.extend(['missing_prerequisite: amount field and amount/order definitions',
                         'outside_method_scope: GMV'])
        else:
            for premise in ('subject semantics', 'time/order semantics',
                            'linked event definition', 'event semantics'):
                check('P-STRICT-FUNNEL', premise, 'unknown', schema_ref)
            capability = 'unsupported'
            gaps.append('outside_method_scope: strict funnel')
    return {'request_state': state, 'capability': capability,
            'prerequisite_checks': checks, 'quality_observations': observations,
            'eligible_method_ids': eligible, 'gaps': gaps,
            'human_decision_state': 'pending', 'limitations': list(LIMITATIONS)}
