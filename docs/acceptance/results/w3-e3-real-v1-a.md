# W3 E3-REAL执行交回：w3-e3-real-v1-a

状态：现有execute单次运行退出0，实际计算／S5／本地草稿及成功终态生成；未验收，待high按W3-v2判定。执行方不自行判定W3通过。human_review_state=pending，S6／外发未授权、未运行。

## 许可依据

- authorization：P-W3-E3-REAL-V1-A。
- confirmation_actor：用户。
- confirmation_basis：用户明确回复“批准 P-W3-E3-REAL-V1-A：本次固定策略及白名单核验链读取；固定CSV前后hash、严格解析和固定计算；上述单次命令及本地写入范围，零重跑。”
- confirmed_at：not_provided；不以工具时刻、日期或run_id代填确认时间。
- 本次许可包括固定真实策略、交接第1–3节逐文件白名单核验链重新读取；唯一CSV父前hash、worker再次前hash、严格解析／固定查询、父后hash及后置核验；准确单次execute、本run及本文／INDEX写入。一次命令不是源只读取一遍。
- 已有效preserve_all引用真实strategy-g35-real-v1-a，不重新选择策略，不更新旧receipt。
- bound_versions：W3-v2 frozen、ADR-003／005／007／008／009、W3-offline-final-review-v1、W3-G35-final-review-v1、W3-E3-REAL-sol61-low-v1。
- 工具recorded_at：2026-10-14T08:18:47.481022+00:00；来源python_datetime_utc，引用本run operation.json。不是用户确认时间或本文精确落盘时间。

## 准确命令与实际运行

```bash
cd /d/MyPythonProjects/datainsight && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH='D:\MyPythonProjects\datainsight\src' TEMP='D:\MyPythonProjects\datainsight\.cache\tmp' TMP='D:\MyPythonProjects\datainsight\.cache\tmp' TMPDIR='D:\MyPythonProjects\datainsight\.cache\tmp' .venv/Scripts/python.exe -B -m datainsight.analysis execute --strategy 'D:\MyPythonProjects\datainsight\outputs\W3\strategy-g35-real-v1-a\strategy.json' --output-dir 'D:\MyPythonProjects\datainsight\outputs\W3\analysis-e3-real-v1-a'
```

仅执行一次，零重跑。没有追加版本／hash／probe／prepare／verify／测试／replay／取时命令，也没有修改源码、配置、标准或安装依赖。

- 实际进程退出0；stdout：`{"phase": "execute", "reason_code": "ok", "human_review_state": "pending"}`。
- cwd为D:\MyPythonProjects\datainsight；进程环境按上面完整命令，字节码关闭，临时目录为批准D盘路径。
- operation／计算证据保存Python3.12.9、DuckDB1.4.1。
- 工具配置观测：memory_limit=256.0 MiB、threads=1、项目.cache/duckdb/tmp及extensions；autoinstall_known_extensions、autoload_known_extensions、allow_unsigned_extensions=false；enable_external_access=true，仅在固定本地来源控制下使用，不宣称DuckDB原生网络隔离。
- 固定worker exitcode=0、reaped=true、terminated=false。工具query_count=5，对应配置SELECT、strict、schema、behaviours和summary；不是源打开次数。
- deadline_seconds=180，为合作式阶段检查与worker监督设计限额，不是本批耗时或OS硬实时证明。产品模型usage／费用not_applicable，开发token／费用／总耗时unknown。

## 源与已批身份

本run `calculation-evidence.json`保存新运行父进程实测：

|阶段|SHA-256|bytes_read|工具开始／结束|
|---|---|---|---|
|before|7095a57fbd6eb1292bec5ccde4713ac256678b8551eb478d3b5aaad89612cfb4|39876537|2026-10-14T08:18:43.968862+00:00 / 2026-10-14T08:18:44.003262+00:00|
|after|7095a57fbd6eb1292bec5ccde4713ac256678b8551eb478d3b5aaad89612cfb4|39876537|2026-10-14T08:18:45.615778+00:00 / 2026-10-14T08:18:45.644915+00:00|

新父前hash匹配策略bindings已批dataset_version，父后hash及bytes_read一致；不是复制历史画像指纹。worker在计算前按现有代码再次hash并匹配批准版本才计算，其独立指纹未单独落盘，不冒称保存了第三份指纹产物。

唯一源是交接固定UserBehavior.csv，只读、未复制／清洗／修改、没有采样或输出原始行。固定上游及策略在实际execute／worker入口重新消费，后置check_context／load_strategy完成；未扩展来源或更新批准对象。当前保存必要身份见bindings.json。

## 计算、S5及草稿证据

唯一M-BEHAVIOUR-RECORDS／P-BEHAVIOUR-RECORDS，严格五列VARCHAR；全文件原始记录全保留，精确文本分桶，不trim、改大小写、去重、过滤或填补。

以下数值直接引用本run result及calculation-evidence工具结果：

|bucket|raw record count|工具引用|
|---|---:|---|
|pv|940045|result.json#/buckets/pv|
|fav|29353|result.json#/buckets/fav|
|cart|57861|result.json#/buckets/cart|
|buy|21315|result.json#/buckets/buy|
|missing|0|result.json#/buckets/missing|
|other|0|result.json#/buckets/other|

所有桶声明绑定 `calculation-evidence.json#/sql/behaviours`；实际固定SQL、源参数与SQL字节hash均已保存在该文件，可由工具重跑，不再另运行。辅助row_count=1048574、strict_row_count=1048574，仅作为覆盖证据；桶和一致由实际calculate及S5执行层工具验证，模型未重新计算。不把row_count作为比例分母或新业务方法。

- validation.json：execution=pass、metric=pass、boundary=pass，各reason_code=ok，引用calculation-evidence.json。
- report.md由固定宿主模板生成，每个桶值引用结果及固定SQL；写后确定性渲染回读、必要文件hash核对均在现有execute成功发布前完成。
- report为本地draft，human_review_state=pending；仅代码原始记录数，不称订单／支付、用户数、比例／转化、GMV、日期／效果或因果结论。
- 正常执行结果不替代源真实性、天然业务含义、总体代表性或独立S6确认。

## 必要产物与唯一终态

run：`outputs/W3/analysis-e3-real-v1-a/`。

bindings.json、result.json、calculation-evidence.json、validation.json、report.md、operation.json及final-status.json已生成。唯一合法终态command=execute、status=success、exit_status=0，completed_at=2026-10-14T08:18:47.497719+00:00，human_review_state=pending。

必要工具hash引用：

|产物／身份|保存SHA-256|
|---|---|
|bindings.json|59401aec63c30e65b39351d4488b2e17e7a4f00449c10aec688b2dbbb929da4f|
|result.json|020942cc3f09d73b28d8aa4daf2ced9d92c754cafa9491c44b410b493d299861|
|calculation-evidence.json|4fc1d869fb4411db9c28ed09fdef24224d3668ce6b3cb45b3b1a2690ee89417e|
|validation.json|7a49f84cf7e30306958e6a5f7a93a3c41b736d9eb3bfd5860a54a9472b1d85ec|
|report.md|a843329fb63a5ce8638a348667cef31e082673a2252022691a98e1c2c5b380bd|
|operation.json|01fa6b9b9fd28fe29359f95d40a961a2b67a7ced1353d7f130b43290cce5248a|
|strategy.json绑定|c081b59260443bded2c1695fdddf755b55df414478bd3b51f4505e1230f70160|
|读取契约|42d635817eb6aa558f514ef5cfe2dcda980387cb0fb21076b9f04c2f41ad4c08|

这些是本次运行工具保存值与执行内核验，不把本轮文件阅读冒称独立hash重算。终态在必要产物完成和绑定、同一deadline检查之后同目录原子发布。不另建全产物清单、hash审计或恢复报告。

## 交回、保持与未测

- 本次新增真实源身份、唯一方法计算、S5和pending草稿，为W3-v2 D303／D304–D311真实产物及D312提供新证明场，待high核对；执行者不自行判定通过。
- 前序诊断／G3.5已通过保持，反向／故障继承限定离线最终验收及R2／R3证据；没有在真实源制造故障或重跑矩阵。
- 本次没有模型／本地模型、网络、凭据、预算账本或外发动作；不声称OS总内存／硬实时或全系统网络隔离。
- 本轮未触发安全失败或发现新的执行阻塞；一次命令额度已消耗，不能自动重跑。
- 未进行S6人工业务解释确认、未发布报告；下一步仅high一次技术验收。后续S6和外发各自独立。
- 历史生产画像与修复后合成收尾分别保留；本次是独立W3真实run，不冒称W1补跑。旧标准／run／receipt均不改，新增ADR无。
