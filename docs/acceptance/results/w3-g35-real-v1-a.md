# W3 G3.5真实策略记录：w3-g35-real-v1-a

状态：单次strategy命令记录完成，退出0；待high核对。执行方不自行判定技术验收通过。W3整体未验收，E3-REAL／S6未运行。

## 许可与人工决定

- authorization：P-W3-G35-REAL-RECORD。
- confirmation_actor：用户；CLI actor=user，用户明确确认该本地标记代表当前用户，不是身份认证。
- confirmation_basis：用户明确回复“批准A–F真实核验链读取；选择preserve_all；确认actor=user代表我、confirmed_at=not_provided；批准上述单次命令和写入范围，零重跑。”
- 三个效力分别成立：交接A–F逐文件真实历史证据读取；明确preserve_all策略决定；准确单次strategy命令及新run／本文／INDEX写入。
- confirmed_at：not_provided，不以工具时间替代确认时间。
- 策略工具recorded_at：2026-10-14T08:08:08.316223+00:00；source=python_datetime_utc，引用strategy.json。该时刻不是用户确认时间，也不声称是本文精确落盘时间。
- 绑定W3-G35-sol61-low-v1、W3-v2 frozen、W3-offline-final-review-v1、ADR-003／005／007／008／009；旧证据保持。

## 准确运行

仅执行以下命令一次，自动重跑0，无额外版本／核验／恢复／测试命令：

```bash
cd /d/MyPythonProjects/datainsight && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH='D:\MyPythonProjects\datainsight\src' TEMP='D:\MyPythonProjects\datainsight\.cache\tmp' TMP='D:\MyPythonProjects\datainsight\.cache\tmp' TMPDIR='D:\MyPythonProjects\datainsight\.cache\tmp' .venv/Scripts/python.exe -B -m datainsight.analysis strategy --decision preserve_all --actor user --confirmed-at not_provided --output-dir 'D:\MyPythonProjects\datainsight\outputs\W3\strategy-g35-real-v1-a'
```

- 实际cwd：D:\MyPythonProjects\datainsight；环境遵循上述命令。
- 实际进程退出：0；stdout：`{"phase": "strategy", "reason_code": "ok", "human_review_state": "pending"}`。
- operation.json实际记录Python=3.12.9、DuckDB=1.4.1；DuckDB仅导入，不连接引擎／执行SQL／启动worker。
- operation.recorded_at=2026-10-14T08:08:08.326689+00:00，source=python_datetime_utc。
- 本轮未改源码、配置、标准、旧receipt或旧run；未运行安装／历史runner。

## 核验与结果证据

run：`outputs/W3/strategy-g35-real-v1-a/`。

执行前只读核对固定S3／候选／诊断manifest与S2／S3引用，所列输入均属交接A–F白名单；目标run／结果文档检查未发现已存在。现有strategy调用load_w3_context及record_preservation_decision中的check_context，实际通过planning.verify_review／load_plan_set及feasibility固定链核验后才保存新run；未另建审计runner或独立复验。

- 固定S2=accept；固定S3=approve；保存的bindings仅唯一M-BEHAVIOUR-RECORDS／P-BEHAVIOUR-RECORDS与现有完整metric_definition。
- strategy.decision=preserve_all；strategy_version=preserve-all-v1；scope=S3.5_preserve_all_only；confirmation_basis=explicit_strategy_argument。其明确用户依据见上节，不把旧S3口径批准当本次策略决定。
- 原始记录全保留，不清洗、去重、过滤、填补、trim或改大小写；固定pv／fav／cart／buy、NULL→missing、其他非NULL→other，全文件已批版本窗口。不新增订单／支付／转化／日期覆盖／效果声明。
- human_review_state=pending不是撤销本次明确策略决定，也不表示S6已完成。
- 必需strategy.json／bindings.json／operation.json／final-status.json已生成；唯一合法final-status.command=strategy、status=success、exit_status=0。
- final-status.completed_at=2026-10-14T08:08:08.329799+00:00。现有同目录原子发布产生终态；本轮不新增故障矩阵、不独立重跑消费。

以下值引用运行工具保存产物，未另执行hash命令，不把文件阅读冒称独立重算hash：

|身份／引用|运行工具保存值|
|---|---|
|strategy.bindings_hash及final-status.required_hashes.bindings.json|59401aec63c30e65b39351d4488b2e17e7a4f00449c10aec688b2dbbb929da4f|
|final-status.required_hashes.strategy.json|c081b59260443bded2c1695fdddf755b55df414478bd3b51f4505e1230f70160|
|final-status.required_hashes.operation.json|0eaecf4c6d3aee5d1a52dea27410a58079076913cd4b4aff4c60247f7a752094|
|bindings.dataset_version（历史已批身份，不是本次CSV实测）|7095a57fbd6eb1292bec5ccde4713ac256678b8551eb478d3b5aaad89612cfb4|
|bindings.s3_hash|cc204b0693eccd411480d1779a978c8515d1e3bc2f2833bb7fcecd71018fb200|
|bindings.read_contract_hash|42d635817eb6aa558f514ef5cfe2dcda980387cb0fb21076b9f04c2f41ad4c08|

必要问题／规则／注册表／口径／上游文件身份及引用集中保存在bindings.json；不额外复制全产物清单。strategy.bindings_hash与终态对应引用一致，high可据现有产物核对，不以退出码单独认证。

## 权限边界与下一门

- 只核验既有批准对象的当前保存证据，读取历史聚合不是重新计算画像。
- 未打开生产CSV，未计算其当前hash，不能宣称当前CSV未变；bindings中source_path仅原固定字面值。
- 无计算SQL、模型、本地模型、网络、凭据、预算账本、余额或外发动作；产品token／usage／费用not_applicable。开发token／金额／总耗时unknown。
- 本策略只形成S3.5资格，不授予源读取／计算许可，不称S4／S5已完成，不生成真实业务报告。
- 本门未触发运行拒绝；反向门控继承既有离线证据，不另跑危险输入。次数已消耗，不重跑。
- 下一步仅交回high核对G3.5真实记录。E3-REAL仍须独立当次生产读取和准确执行许可；S6在真实草稿之后独立，外发亦独立。
- 无新增ADR；INDEX仅导航本文并标待high核对，不改变旧验收结论。
