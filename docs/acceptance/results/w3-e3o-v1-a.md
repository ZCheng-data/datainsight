# W3 offline execution — w3-e3o-v1-a

未验收，待规划／验收方判定。

状态：不完整，退出码1；不得进入真实G3.5／E3。

证据：`outputs/W3/offline-w3-e3o-v1-a/`。实际命令：`.venv/Scripts/python.exe -B -m test_w3 --w3-evidence --batch-id w3-e3o-v1-a`。

Python3.12.9／DuckDB1.4.1已工具核验。cwd与PYTHONPATH／TEMP／TMP／TMPDIR遵循P-W3-E3-OFFLINE-v1。

|标准|实测状态|
|---|---|
| D301 | 未测：本批提前停止 |
| D302 | 未测：本批提前停止 |
| D303 | 未测：本批提前停止 |
| D304 | 未测：本批提前停止 |
| D305 | 未测：本批提前停止 |
| D306 | 未测：本批提前停止 |
| D307 | 未测：本批提前停止 |
| D308 | 未测：本批提前停止 |
| D309 | 未测：本批提前停止 |
| D310 | 未测：本批提前停止 |
| D311 | 未测：本批提前停止 |
| D312 | 未测：本批提前停止 |

详见case-results.json实际expected／actual；结果不由runner返回值单独认证。
