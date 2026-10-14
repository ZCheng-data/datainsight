# W3 R3 offline execution

未验收，待high技术判定；W3总验收未进行。

Authorization: P-W3-E3-OFFLINE-R3; actor=用户; confirmed_at=not_provided.
Command: .venv/Scripts/python.exe -B -m test_w3 --w3-r3-evidence --batch-id w3-e3o-r3-a
cwd: D:\MyPythonProjects\datainsight
Environment: PYTHONDONTWRITEBYTECODE=1; PYTHONPATH=project src;tests; TEMP/TMP/TMPDIR=project .cache/tmp.
Python: 3.12.9; DuckDB: 1.4.1
Actual exit: 0; offline_test_status=passed

|case|actual|expected|assertion|
|---|---|---|---|
| baseline_actual_worker_S5_report_terminal | success | success | passed |
| M1_missing_strategy_terminal | evidence_missing_or_size | evidence_missing_or_size | passed |
| M2_configuration_mismatch | resource_configuration_mismatch | resource_configuration_mismatch | passed |
| M3_post_hash_expiry | execution_deadline | execution_deadline | passed |
| M3_success_staging_expiry | execution_deadline | execution_deadline | passed |
| regression_no_overwrite | output_exists/terminal_exists | output_exists/terminal_exists | passed |
| regression_required_write_failure_safe_cleanup | nonzero_failed_terminal | nonzero_failed_terminal | passed |

Evidence: outputs/W3/offline-w3-e3o-r3-a/; actual details in case-results.json.
Inherited: outputs/W3/offline-w3-e3o-r2-b/ under ADR-009 and W3-v2; old results unchanged.
remaining_offline: []
Deferred: real fixed chain, G3.5 decision, real source hash and D312 not authorized/not_run.
Deadline is cooperative checks plus supervised worker, not OS hard realtime or total-memory isolation.
No model/network/credential action requested; existing R2 evidence and unchanged paths inherited.
recorded_at from operation.json: Python UTC tool time; development tokens/cost unknown.
