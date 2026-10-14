"""Closed, source-code-only aggregate templates v1."""
from enum import Enum
import hashlib
from .inspection import BoundaryError


class ProfileTemplateId(str, Enum):
    SUMMARY = 'summary'
    COLUMNS = 'columns'
    BEHAVIOURS = 'behaviours'
    DUPLICATES = 'duplicates'
    TIMESTAMP = 'timestamp'


VERSION = '1.0'
COLUMNS = ('user_id', 'goods_id', 'category_id', 'behaviour', 'timestamp')
BODIES = {
    ProfileTemplateId.SUMMARY: 'SELECT COUNT(*) AS row_count FROM data',
    ProfileTemplateId.COLUMNS: ' UNION ALL '.join(
        "SELECT '" + name + "' AS column_name, COUNT(*)-COUNT(" + name + ') AS null_count, COUNT(DISTINCT ' + name + ') AS cardinality FROM data' for name in COLUMNS),
    ProfileTemplateId.BEHAVIOURS: "SELECT " + ', '.join(
        "COUNT(*) FILTER (WHERE behaviour='" + label + "') AS " + label for label in ('pv', 'fav', 'cart', 'buy')) + ", COUNT(*) FILTER (WHERE behaviour IS NULL) AS missing, COUNT(*) FILTER (WHERE behaviour IS NOT NULL AND behaviour NOT IN ('pv','fav','cart','buy')) AS other FROM data",
    ProfileTemplateId.DUPLICATES: 'SELECT COUNT(*) AS duplicate_groups, COALESCE(SUM(n-1),0)::BIGINT AS excess_rows FROM (SELECT COUNT(*) AS n FROM data GROUP BY user_id,goods_id,category_id,behaviour,timestamp HAVING COUNT(*)>1) grouped',
    ProfileTemplateId.TIMESTAMP: "SELECT COUNT(*) FILTER (WHERE timestamp IS NULL) AS null_count, COUNT(*) FILTER (WHERE format_ok AND number IS NOT NULL) AS valid_integer, COUNT(*) FILTER (WHERE timestamp IS NOT NULL AND NOT format_ok) AS format_failed, COUNT(*) FILTER (WHERE format_ok AND number IS NULL) AS range_failed, MIN(number) FILTER (WHERE format_ok) AS minimum, MAX(number) FILTER (WHERE format_ok) AS maximum FROM (SELECT timestamp, regexp_full_match(timestamp,'[+-]?[0-9]+') AS format_ok, TRY_CAST(timestamp AS BIGINT) AS number FROM data) diagnosed",
}
FIELDS = {
    ProfileTemplateId.SUMMARY: ('row_count',),
    ProfileTemplateId.COLUMNS: ('column_name', 'null_count', 'cardinality'),
    ProfileTemplateId.BEHAVIOURS: ('pv', 'fav', 'cart', 'buy', 'missing', 'other'),
    ProfileTemplateId.DUPLICATES: ('duplicate_groups', 'excess_rows'),
    ProfileTemplateId.TIMESTAMP: ('null_count', 'valid_integer', 'format_failed', 'range_failed', 'minimum', 'maximum'),
}


def build_template(template_id):
    if type(template_id) is not ProfileTemplateId:
        raise BoundaryError('unknown_profile_template')
    from .profile import READ_RELATION
    return 'WITH data AS (SELECT * FROM ' + READ_RELATION + ') ' + BODIES[template_id]


def template_hash(template_id):
    return hashlib.sha256(build_template(template_id).encode('utf-8')).hexdigest()
