"""Independent csv/Counter reference for synthetic fixtures only, v1.0."""
import csv
from collections import Counter
from pathlib import Path
import re
from datainsight.inspection import normalized, check_components, inside, BoundaryError

ROOT = Path('D:/MyPythonProjects/datainsight/tests/fixtures')
NAMES = ('user_id', 'goods_id', 'category_id', 'behaviour', 'timestamp')


def generate(path, case='mixed'):
    rows = [
        ['001', '002', '003', 'pv', '0001'],
        ['001', '002', '003', 'pv', '0001'],
        ['', '', '', '', ''], ['', '', '', '', ''],
        ['NULL', 'NA', 'sentinel-category', 'unknown-sensitive-behaviour', ' 12 '],
        ['sentinel-user', 'sentinel-goods', 'x', 'buy', '9223372036854775808'],
        ['a,b', 'c\nd', 'e"f', 'fav', '-9223372036854775808'],
        ['u', 'g', 'c', 'cart', '+9223372036854775807'],
        ['u2', 'g2', 'c2', 'PV', '1.5'],
        ['u3', 'g3', 'c3', 'pv', '-0002'],
    ]
    if case == 'all_null_time':
        rows = [['u', 'g', 'c', 'pv', ''], ['u2', 'g2', 'c2', '', '']]
    with path.open('w', encoding='utf-8', newline='') as stream:
        csv.writer(stream, delimiter=',', quotechar='"', doublequote=True).writerows(rows)


def reference(path):
    path = normalized(path)
    if not inside(path, ROOT):
        raise BoundaryError('reference_fixture_only')
    check_components(path)
    with path.open('r', encoding='utf-8', newline='') as stream:
        rows = [tuple(None if value == '' else value for value in row)
                for row in csv.reader(stream, delimiter=',', quotechar='"', doublequote=True, strict=True)]
    if any(len(row) != len(NAMES) for row in rows):
        raise BoundaryError('reference_column_count')
    columns = [{'column_name': name, 'null_count': sum(row[index] is None for row in rows),
                'cardinality': len({row[index] for row in rows if row[index] is not None})}
               for index, name in enumerate(NAMES)]
    behaviours = dict.fromkeys(('pv', 'fav', 'cart', 'buy', 'missing', 'other'), 0)
    for row in rows:
        value = row[3]
        label = 'missing' if value is None else value if value in ('pv', 'fav', 'cart', 'buy') else 'other'
        behaviours[label] += 1
    counts = Counter(rows)
    duplicates = {'duplicate_groups': sum(count > 1 for count in counts.values()),
                  'excess_rows': sum(count - 1 for count in counts.values() if count > 1)}
    timestamp = dict.fromkeys(('null_count', 'valid_integer', 'format_failed', 'range_failed'), 0)
    valid = []
    for row in rows:
        value = row[4]
        if value is None:
            timestamp['null_count'] += 1
        elif re.fullmatch(r'[+-]?[0-9]+', value) is None:
            timestamp['format_failed'] += 1
        else:
            number = int(value)
            if -(2**63) <= number < 2**63:
                timestamp['valid_integer'] += 1
                valid.append(number)
            else:
                timestamp['range_failed'] += 1
    timestamp.update(minimum=min(valid) if valid else None, maximum=max(valid) if valid else None)
    return {'summary': [{'row_count': len(rows)}], 'columns': columns,
            'behaviours': [behaviours], 'duplicates': [duplicates], 'timestamp': [timestamp]}
