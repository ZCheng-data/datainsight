# W3 offline execution — w3-e3o-v1-b

未验收，待规划／验收方判定。

状态：不完整，退出码1；不得进入真实G3.5／E3。

证据：`outputs/W3/offline-w3-e3o-v1-b/`。实际命令：`.venv/Scripts/python.exe -B -m test_w3 --w3-evidence --batch-id w3-e3o-v1-b`。

Python3.12.9／DuckDB1.4.1已工具核验。cwd与PYTHONPATH／TEMP／TMP／TMPDIR遵循P-W3-E3-OFFLINE-v1。

|标准|实测状态|
|---|---|
| D301 | 部分：实际合成核验链；缺完整变化矩阵 |
| D302 | 部分：明确决定／reject／cancel；缺完整绑定矩阵 |
| D303 | 部分：合成源hash／固定路径；缺坏解析矩阵 |
| D304 | 部分：真实DuckDB与独立csv／Counter一致性测试 |
| D305 | 部分：局部配置／文档边界／过期预算；缺实际超时回收 |
| D306 | 部分：三层基线与执行层独立拒绝 |
| D307 | 部分：参数变化；缺完整口径矩阵 |
| D308 | 部分：任意text及无依据claim拒绝 |
| D309 | 部分：确定性草稿；缺完整发布链 |
| D310 | 部分：独占输出；缺故障矩阵 |
| D311 | 部分：worker策略／来源拒绝；缺泄露／调用直接断言 |
| D312 | 未测：真实门未授权 |

详见case-results.json实际expected／actual；结果不由runner返回值单独认证。
