"""Closed W2-B1 metadata; definitions, never computed business results."""
from copy import deepcopy
from pathlib import Path
import hashlib
from . import feasibility as f

REGISTRY_ID = 'W2-B1'
VERSION = 'v1'
METHOD = 'M-BEHAVIOUR-RECORDS'
METRIC = {
    'event_meaning': 'read raw record and behaviour code; not proven order or payment',
    'subject': 'raw_read_record', 'grain': 'one_raw_record',
    'metric_name': 'behaviour_bucket_raw_record_count',
    'counted_object': 'records in each fixed bucket', 'numerator': 'not_a_ratio',
    'denominator': 'not_applicable',
    'window': 'entire_file_bound_to_dataset_version; date coverage unconfirmed',
    'time_unit': 'unknown', 'timezone': 'unknown',
    'buckets': ['pv', 'fav', 'cart', 'buy', 'missing', 'other'],
    'classification': {'pv': 'exact text pv', 'fav': 'exact text fav',
        'cart': 'exact text cart', 'buy': 'exact text buy', 'missing': 'behaviour IS NULL',
        'other': 'non-NULL outside pv/fav/cart/buy; no original text expansion'},
    'global_filter': 'none; no record exclusion',
    'null_policy': 'behaviour NULL enters missing; other NULLs do not exclude; no imputation',
    'duplicate_policy': 'preserve all; duplicate candidates are not error judgments',
    'text_policy': 'no trim or case normalization; W1 reading contract',
    'dimensions': ['fixed_behaviour_bucket'], 'aggregation': 'COUNT raw records; no DISTINCT',
    'transformation': 'raw_preserved_no_transformation',
    'cleaning_authorization': 'none; not an S3.5 approval',
}
OUTPUT_SCHEMA = [{'name': name, 'type': 'nonnegative_integer_count'}
                 for name in ('pv', 'fav', 'cart', 'buy', 'missing', 'other')]


def registered_methods():
    return {'registry_id': REGISTRY_ID, 'registry_version': VERSION,
            'registry_hash': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'method_ids': [METHOD]}


def definition():
    return deepcopy(METRIC)


def candidate(context):
    metric = definition()
    return {'plan_id': 'P-BEHAVIOUR-RECORDS', 'plan_version': VERSION,
        'method_id': METHOD, 'rule_version': 'v1', 'question_ref': context['question_ref'],
        'required_fields': ['behaviour'], 'optional_fields': [], 'grain': 'one_raw_record',
        'prerequisites': deepcopy(context['prerequisite_checks']),
        'satisfied_evidence': deepcopy(context['evidence_refs']), 'unmet_conditions': [],
        'metric_definition': metric, 'metric_definition_version': VERSION,
        'metric_definition_hash': f.digest(f.encoded(metric)),
        'expected_output_schema': deepcopy(OUTPUT_SCHEMA),
        'assumptions': ['W1 specified reading contract; not inferred natural types'],
        'risks': ['behaviour code semantics unconfirmed', 'current source file not revalidated'],
        'limitations': ['plan only; no computation', 'no orders/payments/GMV/ratios/funnel/dates',
                        'S3 review does not authorize cleaning, SQL or execution']}
