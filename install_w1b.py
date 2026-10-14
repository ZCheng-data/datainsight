"""Single approved uv installation, with process-tree supervision."""
from pathlib import Path
import sys
import os
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from supervise_w1b import supervise
from datainsight.inspection import normalized, check_components

ROOT = Path('D:/MyPythonProjects/datainsight')
UV = Path('C:/Users/86151/.cherrystudio/bin/uv.exe')
PYTHON = ROOT / '.venv/Scripts/python.exe'

def validate_install_paths(effective):
    expected = {'temp': ROOT / '.cache/tmp', 'uv_cache': ROOT / '.cache/uv', 'interpreter': PYTHON}
    for key, target in expected.items():
        path = normalized(effective[key])
        if path != target:
            raise RuntimeError('effective_path_mismatch')
        check_components(path)


def valid_import(imported):
    if type(imported) is not dict or set(imported) != {'version', 'module'}:
        return False
    if imported['version'] != '1.4.1' or type(imported['module']) is not str:
        return False
    try:
        path = normalized(imported['module'])
        check_components(path)
        return ROOT / '.venv' in path.parents
    except (ValueError, OSError):
        return False


def install_once(default, effective, output):
    validate_install_paths(effective)
    command = [str(UV), '--no-config', '--no-progress', '--color', 'never', '-v',
        'pip', 'install', '--python', str(PYTHON), '--no-python-downloads',
        '--no-managed-python', '--only-binary', ':all:', '--no-deps',
        '--default-index', 'https://pypi.org/simple', '--cache-dir', str(ROOT / '.cache/uv'),
        '--link-mode', 'copy', 'duckdb==1.4.1']
    result = supervise(command, output, 300)
    record = {'default_paths': default, 'effective_paths': effective, 'supervision': result,
              'installation_actions_started': 1, 'default_retry_policy': '未确认',
              'retry_observed': '无法确认', 'retry_count': None,
              'retry_count_complete': False,
              'retry_observation_reason': 'Verbose logs retained; absence of retry lines does not confirm zero retries.',
              'retry_observation_sources': ['stdout.log', 'stderr.log', 'local uv help checked during P-B0'],
              'allowed_index': 'https://pypi.org/simple',
              'allowed_package_file_service': 'files.pythonhosted.org',
              'wheel_hash': None, 'wheel_hash_status': 'not_yet_obtained'}
    if result['parent_exit_status'] == 0 and not result['timeout'] and result['termination_confirmed']:
        check = subprocess.run([str(PYTHON), '-B', '-c',
            'import duckdb,json; print(json.dumps({"version":duckdb.__version__,"module":duckdb.__file__}))'],
            capture_output=True, text=True)
        record['import_exit_status'] = check.returncode
        if check.returncode == 0:
            imported = json.loads(check.stdout)
            record['import_verification'] = imported
            record['import_valid'] = valid_import(imported)
        else:
            record['import_valid'] = False
            record['import_error'] = 'controlled_import_failed; raw exception suppressed'
    else:
        record['import_verification'] = 'not_run'
    return record


def main():
    for target in (ROOT, PYTHON, ROOT / '.cache/uv', ROOT / '.cache/tmp', ROOT / '.cache/duckdb'):
        check_components(normalized(target))
    default = {'temp': tempfile.gettempdir(),
               'uv_cache': subprocess.check_output([str(UV), 'cache', 'dir'], text=True).strip(),
               'uv_version': subprocess.check_output([str(UV), '--version'], text=True).strip(),
               'pip_cache': 'not_applicable; pip absent in P-B0',
               'historical_P_B0_log': 'conversation tool output only; no reconstructed historical log'}
    removed = []
    for key in list(os.environ):
        if key.startswith(('UV_', 'PIP_')):
            removed.append(key)
            del os.environ[key]
    os.environ.update(TEMP=str(ROOT / '.cache/tmp'), TMP=str(ROOT / '.cache/tmp'),
        TMPDIR=str(ROOT / '.cache/tmp'), UV_CACHE_DIR=str(ROOT / '.cache/uv'),
        PYTHONDONTWRITEBYTECODE='1')
    for name in ('uv', 'tmp', 'duckdb'):
        (ROOT / '.cache' / name).mkdir(exist_ok=True)
    tempfile.tempdir = None
    effective = {'temp': tempfile.gettempdir(),
                 'uv_cache': subprocess.check_output([str(UV), '--no-config', 'cache', 'dir'], text=True).strip(),
                 'interpreter': str(PYTHON), 'cleared_variable_names_only': removed}
    run = 'install-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output = ROOT / 'outputs/W1-B' / run
    record = install_once(default, effective, output)
    result = record['supervision']
    with (output / 'installation.json').open('x', encoding='utf-8') as stream:
        json.dump(record, stream, ensure_ascii=True, indent=2)
    print(json.dumps({'evidence_directory': str(output), 'supervision': result,
        'import_verification': record.get('import_verification'), 'import_valid': record.get('import_valid', False)}, indent=2))
    sys.exit(0 if record.get('import_valid') else 2)


if __name__ == '__main__':
    main()
