"""Offline B09 regression and retained synthetic CLI finalization evidence."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datainsight import profile as p

ROOT = p.ROOT


def save(directory, name, data):
    with (directory / name).open('x', encoding='utf-8') as stream:
        json.dump(data, stream, ensure_ascii=True, indent=2, allow_nan=False)
        stream.write('\n')


def main():
    run_id = 'b09-finalization-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out = p.new_output(ROOT / 'outputs/W1-B' / run_id)
    source_paths = [ROOT / 'src/datainsight/__main__.py', ROOT / 'src/datainsight/profile.py',
        ROOT / 'tests/test_w1b_finalization.py', Path(__file__).absolute()]
    snapshots = out / 'source-snapshots'
    snapshots.mkdir()
    for path in source_paths:
        with (snapshots / path.name).open('xb') as stream:
            stream.write(path.read_bytes())
    command = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', str(ROOT / 'tests'),
               '-p', 'test_*.py', '-v']
    started_at = p.now()
    clock = time.perf_counter()
    tested = subprocess.run(command, capture_output=True, text=True)
    duration = time.perf_counter() - clock
    with (out / 'test.log').open('x', encoding='utf-8') as stream:
        stream.write(tested.stdout + tested.stderr)
    print(tested.stdout + tested.stderr)
    save(out, 'test-command.json', {'argv': command, 'exit_status': tested.returncode,
        'started_at': started_at, 'ended_at': p.now(), 'elapsed_seconds': duration})
    save(out, 'environment.json', {'executable': sys.executable, 'python_version': sys.version,
        'duckdb_version': p.duckdb.__version__, 'process_variables': {key: os.environ.get(key) for key in
            ('TEMP', 'TMP', 'TMPDIR', 'PYTHONPATH', 'PYTHONDONTWRITEBYTECODE')},
        'production_csv_opened': False, 'dependencies_installed': False})
    status = tested.returncode
    injection_success = False
    observations = []
    if status == 0:
        sys.path.insert(0, str(ROOT / 'tests'))
        from test_w1b_finalization import exercise_finalization
        started = p.now()
        clock = time.perf_counter()
        try:
            observations = exercise_finalization(out)
            injection_success = all(
                case['exit_status'] == (0 if case['fault'] == 'none' else 2)
                and case['terminal']['status'] == ('success' if case['fault'] == 'none' else 'failed')
                and case['terminal']['exit_status'] == case['exit_status']
                and case['calculation_status'] == 'computed_pending_finalization'
                for case in observations)
            status = 0 if injection_success else 2
            save(out, 'fault-injection-results.json', {'all_terminal_states_match': injection_success,
                'cases': observations, 'scope': 'synthetic CSV; profile source patched; no production reads',
                'started_at': started, 'ended_at': p.now(), 'elapsed_seconds': time.perf_counter() - clock})
        except (Exception,):
            status = 2
            save(out, 'fault-injection-failure.json', {'status': 'failed', 'reason_code': 'controlled_evidence_generation_failed'})
    save(out, 'runner-command.json', {'argv': [sys.executable, '-B', str(Path(__file__).absolute())],
        'exit_status': status, 'test_exit_status': tested.returncode,
        'fault_injection_status': 'complete' if injection_success else 'not_complete'})
    result_index = ROOT / 'docs/acceptance/results' / (run_id + '.md')
    text = '# B09 CLI 收尾状态修复执行证据\n\n总判定：未验收，待验收者判定。\n\n'
    text += '- 对应冻结标准：docs/acceptance/W1-B-v1.md（未修改）。\n'
    text += '- 证据根：outputs/W1-B/' + run_id + '。\n'
    text += '- 用户操作确认时间：未提供；文档生成工具时间：' + p.now() + '。\n'
    text += '- 全部回归日志与实际命令/退出状态：test.log、test-command.json。\n'
    text += '- 本批完整可重跑脚本与运行环境：source-snapshots/run_b09_finalization_evidence.py、runner-command.json、environment.json。\n'
    text += '- 新增测试：test_profile_and_replay_terminal_states_follow_required_evidence、test_existing_output_is_not_changed_on_cli_failure、test_unwritable_terminal_record_does_not_leave_success_artifacts。\n'
    text += '- 计算产物状态固定 computed_pending_finalization；单模板计算 evidence 的 success 仅指该查询，不是 CLI 整轮成功。\n'
    text += '- 唯一已发布 CLI 终态为 final-status.json。必须完成引用核验、environment/network/command 证据后才发布 success。\n'
    text += '- 终态采用同目录临时文件完整写入、flush/fsync 后独占重命名；失败临时文件保留，不是已发布终态。\n'
    if injection_success:
        text += '\n## 合成 CLI 故障注入与正常收尾\n\n'
        text += 'fault-injection-results.json 记录实际调用 main() 的 argv、返回值、受控输出、终态和发布顺序。\n\n'
        text += '| 命令 | 场景 | 实测退出状态 | 终态 | 计算产物状态 | 证据目录 |\n|---|---|---|---|---|---|\n'
        for case in observations:
            text += '| ' + case['command'] + ' | ' + case['fault'] + ' | ' + str(case['exit_status']) + ' | ' + case['terminal']['status'] + ' | ' + case['calculation_status'] + ' | ' + Path(case['output_dir']).name + ' |\n'
        text += '\n每个正常目录具有必需证据与 final-status.json；失败目录保留计算结果/已完成证据及受控失败终态，不留成功画像状态。\n'
    else:
        text += '\n本批测试或证据运行未完成，不作成功声明；失败证据见上述文件。\n'
    text += '\n## 限制与下一步\n\n'
    text += '未运行生产画像/生产重跑，未安装、联网、改源或改冻结标准。旧生产结果及失败历史全部保留，不追改旧 run。\n'
    text += '整个输出目录不可写时，无法保证失败记录落盘；CLI 返回2并明确 failure_evidence_persisted=false，计算产物仍pending，不能解释成成功。该情形有受控测试，不将证据视作可选。\n'
    text += '本批仅 B09 收尾修复；不宣称新增系统隔离、并发攻击防护或业务分析能力。待验收对话复核，再决定是否需要生产重跑。\n'
    with result_index.open('x', encoding='utf-8') as stream:
        stream.write(text)
    files = sorted(path for path in out.rglob('*') if path.is_file()) + source_paths + [result_index]
    artifacts = []
    for path in files:
        payload = path.read_bytes()
        artifacts.append({'path': str(path.relative_to(ROOT)), 'byte_size': len(payload),
            'sha256': hashlib.sha256(payload).hexdigest()})
    save(out, 'manifest.json', {'self_excluded': True, 'files': artifacts})
    print(json.dumps({'test_exit_status': tested.returncode, 'exit_status': status,
        'fault_injection_states_match': injection_success, 'case_count': len(observations),
        'evidence_directory': str(out), 'result_index': str(result_index)}, ensure_ascii=True))
    return status


if __name__ == '__main__':
    sys.exit(main())
