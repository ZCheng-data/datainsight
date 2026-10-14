# W3 offline execution — w3-e3o-r2-b

未验收，待规划／验收方判定。

状态：不完整，退出码1；不得进入真实G3.5／E3。

证据：`outputs/W3/offline-w3-e3o-r2-b/`。实际命令：`.venv/Scripts/python.exe -B -m test_w3 --w3-evidence --batch-id w3-e3o-r2-b`。

Python3.12.9／DuckDB1.4.1已工具核验。cwd与PYTHONPATH／TEMP／TMP／TMPDIR遵循P-W3-E3-OFFLINE-R2。

|标准|实测状态|
|---|---|
| D301 | 部分实测；请按case-results核对本ID直接用例，跨层用例另列；不表示完整覆盖 |
| D302 | 部分实测；请按case-results核对本ID直接用例，跨层用例另列；不表示完整覆盖 |
| D303 | 部分实测；请按case-results核对本ID直接用例，跨层用例另列；不表示完整覆盖 |
| D304 | 部分实测；请按case-results核对本ID直接用例，跨层用例另列；不表示完整覆盖 |
| D305 | 部分实测；请按case-results核对本ID直接用例，跨层用例另列；不表示完整覆盖 |
| D306 | 部分实测；请按case-results核对本ID直接用例，跨层用例另列；不表示完整覆盖 |
| D307 | 部分实测；请按case-results核对本ID直接用例，跨层用例另列；不表示完整覆盖 |
| D308 | 部分实测；请按case-results核对本ID直接用例，跨层用例另列；不表示完整覆盖 |
| D309 | 部分实测；请按case-results核对本ID直接用例，跨层用例另列；不表示完整覆盖 |
| D310 | 部分实测；请按case-results核对本ID直接用例，跨层用例另列；不表示完整覆盖 |
| D311 | 部分实测；请按case-results核对本ID直接用例，跨层用例另列；不表示完整覆盖 |
| D312 | 真实部分未授权、未运行 |

实际未闭合项：
- D301 dataset mutation and accurate per-case baseline/reason matrix
- D302 missing terminal and all strategy identity mutations
- D303 link path controlled rejection
- D305 configuration fault and exact byte boundaries
- D310 required-artifact open/write/flush/fsync matrix (only save failure covered)
- D311 provider-specific direct assertions
- D312 real proof not authorized

详见case-results.json实际expected／actual；结果不由runner返回值单独认证。
