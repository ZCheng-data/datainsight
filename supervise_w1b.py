"""Windows Job supervision. Offline validation only unless separately authorized."""
import ctypes
from ctypes import wintypes as w
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path('D:/MyPythonProjects/datainsight')


class Accounting(ctypes.Structure):
    _fields_ = [('user', ctypes.c_int64), ('kernel', ctypes.c_int64),
                ('period_user', ctypes.c_int64), ('period_kernel', ctypes.c_int64),
                ('faults', w.DWORD), ('total', w.DWORD), ('active', w.DWORD),
                ('terminated', w.DWORD)]


def supervise(command, output, seconds):
    from datainsight.inspection import normalized, check_components, inside, BoundaryError
    output = normalized(output)
    if not inside(output, ROOT / 'outputs/W1-B'):
        raise BoundaryError('output_outside_policy')
    check_components(output)
    if output.exists():
        raise BoundaryError('output_exists')
    output.mkdir(parents=True)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, w.LPCWSTR]
    kernel.CreateJobObjectW.restype = w.HANDLE
    kernel.AssignProcessToJobObject.argtypes = [w.HANDLE, w.HANDLE]
    kernel.AssignProcessToJobObject.restype = w.BOOL
    kernel.TerminateJobObject.argtypes = [w.HANDLE, w.UINT]
    kernel.TerminateJobObject.restype = w.BOOL
    kernel.QueryInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD, ctypes.c_void_p]
    kernel.QueryInformationJobObject.restype = w.BOOL
    kernel.CloseHandle.argtypes = [w.HANDLE]
    job = kernel.CreateJobObjectW(None, None)
    if not job:
        raise OSError('job_creation_failed')
    # No child is launched before assignment succeeds. A wrapper is necessary
    # because Popen does not expose a suspended process's primary thread handle.
    wrapper = 'import sys,subprocess; token=sys.stdin.readline(); sys.exit(subprocess.call(sys.argv[1:]) if token=="GO\\n" else 90)'
    started_at = datetime.now(timezone.utc).isoformat()
    clock = time.perf_counter()
    timed_out = False
    assigned = False
    terminated = False
    process = None
    try:
        with (output / 'stdout.log').open('xb') as stdout, (output / 'stderr.log').open('xb') as stderr:
            process = subprocess.Popen([sys.executable, '-B', '-c', wrapper, *command],
                stdin=subprocess.PIPE, stdout=stdout, stderr=stderr)
            assigned = bool(kernel.AssignProcessToJobObject(job, w.HANDLE(int(process._handle))))
            if not assigned:
                process.kill()
                process.wait(timeout=10)
                raise OSError('job_assignment_failed_no_child_launched')
            process.stdin.write(b'GO\n')
            process.stdin.close()
            try:
                process.wait(timeout=max(0, seconds - (time.perf_counter() - clock)))
            except subprocess.TimeoutExpired:
                timed_out = True
                terminated = bool(kernel.TerminateJobObject(job, 124))
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    pass
            accounting = Accounting()
            deadline = time.perf_counter() + 10
            queried = False
            while True:
                queried = bool(kernel.QueryInformationJobObject(job, 1, ctypes.byref(accounting), ctypes.sizeof(accounting), None))
                if not queried or accounting.active == 0 or time.perf_counter() >= deadline:
                    break
                time.sleep(0.02)
            result = {'argv': command, 'budget_seconds': seconds,
                'started_at': started_at, 'ended_at': datetime.now(timezone.utc).isoformat(),
                'elapsed_seconds': time.perf_counter() - clock, 'timeout': timed_out,
                'job_assigned': assigned, 'terminate_job_succeeded': terminated,
                'parent_exit_status': process.poll(), 'job_query_succeeded': queried,
                'job_active_processes': accounting.active if queried else None,
                'job_total_processes': accounting.total if queried else None,
                'termination_confirmed': process.poll() is not None and queried and accounting.active == 0,
                'scope': 'this supervised process tree only, not whole-system isolation'}
            with (output / 'supervision.json').open('x', encoding='utf-8') as stream:
                json.dump(result, stream, indent=2)
            return result
    finally:
        # No close-as-kill assumption: explicit termination and query above.
        if process is not None and process.poll() is None:
            kernel.TerminateJobObject(job, 124)
        kernel.CloseHandle(job)


if __name__ == '__main__':
    os.environ.update(TEMP=str(ROOT / '.cache/tmp'), TMP=str(ROOT / '.cache/tmp'),
        TMPDIR=str(ROOT / '.cache/tmp'), PYTHONDONTWRITEBYTECODE='1')
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    # Parent creates a child, then both wait. Both must be terminated by the Job.
    waiting = 'import subprocess,sys,time; p=subprocess.Popen([sys.executable,"-B","-c","import time; time.sleep(60)"]); print("controlled_child_started",flush=True); time.sleep(60)'
    result = supervise([sys.executable, '-B', '-c', waiting],
                       ROOT / 'outputs/W1-B' / ('supervision-' + run_id), 2)
    ok = result['timeout'] and result['terminate_job_succeeded'] and result['termination_confirmed'] and result['job_total_processes'] >= 3
    print(json.dumps({'validation_success': ok, **result}, indent=2))
    sys.exit(0 if ok else 2)
