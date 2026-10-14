# W3自包含执行交接 v1：唯一方法的计算—校验—本地草稿

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

- 状态：accepted／待执行授权；接口、资源、验收及命令契约形式已确认，内容未变；不是当前已存在的功能命令，也不是可直接启动的权限。
- confirmation_actor：用户。
- confirmation_basis：用户先确认八项方向边界并批准合批文档落盘，随后对“一次确认W3方案／标准／交接的详细安排并冻结”的建议回复“确认”；据此执行P-W3-DOC-F，仅保存确认／冻结状态和同步INDEX。
- confirmed_at：not_provided。
- recorded_at：null；recorded_at_source：not_available；recorded_at_status：unavailable。
- recorded_at_reason：本次确认状态保存仅使用文件工具，未给可信精确时刻，不估计、借用历史时间或执行未授权取时命令。
- authorization_scope：P-W3-DOC-F仅W3方案、标准、low交接确认／冻结状态与INDEX导航更新；不授权代码／测试／真实摘要或CSV工具读取／策略／网络／API。
- bound_versions：ADR-008、W3-plan-v1 accepted、W3-v1 frozen；ADR-003／005／007及旧frozen保持。

## 【目标】

本轮只补一个证明场：固定有效S3 → 独立G3.5原始记录全保留 → 独立当次读取许可 → 唯一`M-BEHAVIOUR-RECORDS`真实计算 → S5执行／口径／边界三层校验 → 本地报告草稿与唯一终态 → 一次交回规划／验收。

结束于S5，human_review_state=pending；其后独立S6人工业务解释确认才能称完整S4→S5→S6闭环。本轮不实现S6记录／外发，不替人确认。

## 【职责与前置状态】

- 你是用户指定sol6.1 low执行角色，写明确实现、测试与真实证据；不声称切换实际模型，不启动其他Agent／Session，不自行验收通过。
- W1、W2-A、W2-B1通过。W2离线基线通过、阶段停止续作；W2-B2整体未验收／真实调用暂停。L1／静态限定通过保持，不重跑。
- ADR-008停止真实模型解释续作，W3不依赖它；W3零模型调用，包括本地模型。token、usage、provider成本not_applicable，不操作预算账本／密钥。
- 项目venv已有Python3.12.9／DuckDB1.4.1；本轮不安装、建环境或运行历史安装工具。依赖实际版本不符停止。
- 历史生产画像／模板重跑是修复前证据；修复后收尾是另一合成批次。新W3真实计算不得回填或冒称W1修复后生产运行。

启动只读：ADR-008、本交接、W3-plan-v1、W3-v1及需要的当前函数；不要从零重验或读取CSV。W3-v1已frozen；若实际版本／内容不符则停止。先提出本交接范围内的精确离线合批预授权，获批后才实现／运行；技能／文件不赋予工具读取业务摘要或命令执行权。

## 【固定输入】

项目根/cwd：`D:\MyPythonProjects\datainsight`。

- S3：`outputs/W2-B1/w2b1-review-219e79901d08444bab62c6e61f6e2211/s3-review.json`。
- 候选：`outputs/W2-B1/w2b1-candidates-1f9fa1e612fa4c19b48181111a3a35d6/candidate-plans.json`。
- S2：`outputs/W2-A/s2-accept-3178ad8b677e49edb91de623be0c3905/decision.json`。
- 问题：`configs/w2a-question-v1.json`，behaviour_record_counts／raw_record，不放开文件入口。
- 读取契约：`configs/w1b-read-contract-v1.json`；方法定义在`src/datainsight/planning_methods.py`。
- 固定模板：`src/datainsight/profile_templates.py`的BEHAVIOURS和辅助SUMMARY；严格解析用现有READ_RELATION及必要聚合／零行schema检查。
- 真实源：`D:\大数据项目\电商用户行为分析\第9章\UserBehavior.csv`，仅当次独立读取许可之后只读。
- 真实画像／核验链：仅现有`planning.verify_review`／`load_plan_set`必要集合，真实工具执行读取须独立许可；不扫全部outputs／旧淘宝项目。

使用阶段已有部分证据但完整业务闭环尚缺。不能把旧画像数复制成新计算，也不能用现有source_path字段扩权。源字节hash必须匹配核验后的已批数据版本，变化停止并交回，不自动重新受理／批准。

## 【输出与可修改范围】

仅新增两份功能／测试文件：

1. `src/datainsight/analysis.py`：固定W3门、策略receipt、受控worker计算／S5／报告与CLI。
2. `tests/test_w3.py`：独立参考、正常／反向／故障和一个合成证据runner。

运行获批后只新增：

- `tests/fixtures/w3/<batch_id>/`：有限合成CSV；原始合成行不打印或放提示词。
- `outputs/_scratch/<batch_id>/`：合成上游／决定包；明确synthetic，不伪装真实用户批准。
- `outputs/W3/offline-<batch_id>/`：test.log、case-results.json、reference-results.json、batch-result.json、operation.json及必要故障子run。
- `outputs/W3/strategy-<run_id>/`：strategy.json、bindings.json、operation.json、final-status.json。
- `outputs/W3/analysis-<run_id>/`：bindings.json、calculation-evidence.json、result.json、validation.json、report.md、operation.json、final-status.json。
- `.cache/tmp/`及现有`.cache/duckdb/tmp`／`extensions`：批准进程可控临时位置，不清理旧缓存。
- `docs/acceptance/results/<batch_id-or-run_id>.md`与INDEX：一次记录本批结果，不自行通过。

新名称必须检查不存在；不得覆盖、删除、移动、回填旧run／frozen／receipt／源码／配置／fixture。不得新增根目录runner、通用方法引擎或全系统审计框架。需要修改旧功能、新依赖、增加文件或提高限额立即停止请求。

## 【接口：先落实契约，再实现】

以下均是待实现，不是已存在接口：

```text
load_w3_context(s3_review_ref: Path) -> ExecutionContext
record_preservation_decision(context: ExecutionContext, decision: StrategySpec,
                             output_dir: Path) -> StrategyReceipt
execute_verified_plan(strategy_ref: Path, output_dir: Path) -> W3Run
validate_s5(context: ExecutionContext, strategy: StrategyReceipt,
            calculation: CalculationEvidence) -> ValidationResult
render_report(claims: ValidatedClaims, evidence: CalculationEvidence) -> bytes
main(argv=None) -> int
```

最小字段：

- ExecutionContext：固定有效approve、method／plan、完整已批口径、数据／问题／规则／方法／口径版本与实际hash、S2／S3必要引用；不含原始行或执行权限。
- StrategySpec：preserve_all／reject／cancel、actor、confirmed_at；不默认preserve_all，其他清洗策略拒绝。
- StrategyReceipt：独立run、决定、actor／confirmation_basis、confirmed_at、工具recorded_at及来源、数据／方案／问题／规则／方法／口径／策略身份与必要引用；scope=S3.5_preserve_all_only。
- CalculationEvidence：源前后工具hash、契约hash、实际固定SQL／参数／模板hash、六桶结果／辅助row_count及实际结果hash、版本／环境／资源／状态。
- ValidationResult：execution／metric／boundary各pass／fail、准确reason_code与证据引用。
- ValidatedClaims：仅behaviour_bucket_raw_record_count＋固定bucket＋工具value_ref／evidence_ref；拒绝任意text、新类型、新指标或数值直接输入。
- W3Run：pending计算状态／三层结果／必要引用／唯一终态，草稿human_review_state=pending。

复用`planning.verify_review`／`load_plan_set`、`planning_methods`、`inspection`源／路径／hash及`profile`严格契约／结果校验。不要为了减少旧manifest或重复函数调用改W1／W2。

现有`profile.execute_profile_template`没有本轮资源监督接口：不能仅调用它就宣称有超时。新模块内部用固定模板和局部DuckDB连接／worker补本轮必要控制，不复制整套画像或通用SQL执行器。

## 【唯一计算口径与资源】

一条原始读取记录；behaviour精确pv／fav／cart／buy，NULL→missing，其余非NULL→other；全文件版本窗口。全保留、不去重、不trim／规范大小写、不填补／过滤。不报订单／支付／独立用户／比例／转化／日期／效果。

允许固定SELECT／WITH：BEHAVIOURS、辅助SUMMARY及必要严格解析聚合／schema检查；禁止自由SQL、多语句／管理语句及外部URI。辅助row_count仅作S5桶覆盖核验，不变成新业务方法。

已确认但尚未实测的设计值：

- DuckDB局部宿主config：memory_limit=256MiB、threads=1；沿用D盘临时／扩展目录，关闭自动扩展安装／加载；固定SELECT核对实际配置，不执行SET。
- E3整体deadline180秒，源hash按块检查；固定worker使用剩余时间，超时终止／回收，不重试；只启动已有venv的本模块，不接用户可控命令／shell。不得宣称OS级总内存硬限制或全系统隔离。
- 六桶聚合一行，单结果64KiB；每个JSON／草稿1MiB。超限拒绝，不截断／提限。设计值不是实测，运行失败不得自动调整。
- 错误捕获只输出安全phase／reason，禁止打印DuckDB异常raw（可能含原始行／路径片段）、标识值、密钥或完整环境。

## 【验收：一次列全】

权威清单为已frozen的`docs/acceptance/W3-v1.md`的D301–D312；不得自行缩条款或改变设计上限。正常测试用真实DuckDB＋独立csv／Counter参考工具，不能用预设结果mock证明计算正确。

必须覆盖：

- 上游合法链；reject/cancel／未知方法／缺终态／问题、数据、规则、注册表、口径各独立变化拒绝。
- G3.5明确选择；缺决定／停止决定／错误策略／旧绑定拒绝；新confirmed_at与recorded_at分开，不重构旧schema。
- 固定来源／路径／严格解析；源前后hash和已批版本；合法baseline下坏解析／身份变化拒绝。
- NULL／other／重复／大小写和空格保留，工具桶和与辅助row_count相等；非法结果schema／类型／字节变化／缺证据拒绝。
- 局部资源config与受控worker超时终止／回收；结果／文档超量不截断。
- S5三层各独立拒绝：执行证据错配；过滤／分母／粒度等口径变化；订单／支付／转化／日期／效果等无依据claim。
- 报告数值及引用来自工具；修改报告或引用拒绝成功；三层全部通过才生成可用草稿，保持pending人工状态。
- 已有输出拒绝；必要文件写入及终态open/write/flush/fsync/rename的有效故障注入，非零无合法success；tmp保留，双收尾失败明确披露。
- 不请求模型／网络、不读取凭据；错误敏感片段不打印；固定worker不能绕过来源／策略校验。
- 最终必须有独立许可后的新增真实E3结果、三层校验、草稿及终态；离线证据不能代替它。

每个主要负向有合法独立基线、只改一个条件，报告actual／expected／reason_code和query_count／发布状态；不让更早错误掩盖目标检查。危险路径／故障用受控mock，不攻击真实目标或旧证据。

不要求跨run完整清单、扫描范围报告、同一结论反复新进程恢复；保留直接断言、必要引用／hash和消费入口核验，不对所有自然语言／native调用宣称认证。

## 【命令契约与授权：不立即执行】

以下是拟新增入口和准确命令形式，**尚不存在、未获运行许可**。执行前须核对实施版本、actor、batch／run ID、冻结标准与授权范围；把占位符替换为本次获批值，不能按本交接自动生成真实批准。

所有批次用项目`.venv/Scripts/python.exe`；工作目录显式项目根，进程变量PYTHONPATH含项目src／tests（Windows路径列表用分号）、PYTHONDONTWRITEBYTECODE=1，TEMP／TMP／TMPDIR指向项目`.cache/tmp`。Git Bash可用：

```bash
cd /d/MyPythonProjects/datainsight && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH='D:\MyPythonProjects\datainsight\src;D:\MyPythonProjects\datainsight\tests' TEMP='D:\MyPythonProjects\datainsight\.cache\tmp' TMP='D:\MyPythonProjects\datainsight\.cache\tmp' TMPDIR='D:\MyPythonProjects\datainsight\.cache\tmp' .venv/Scripts/python.exe -B -m test_w3 --w3-evidence --batch-id <approved_batch_id>
```

runner只执行本轮合成测试与必要直接接口断言，不discover旧测试套件、不读取真实画像／CSV。它应按本交接路径生成新证据／结果文档，已存在batch拒绝。

策略门拟议argv（同一cwd／环境）：

```text
.venv/Scripts/python.exe -B -m datainsight.analysis strategy
  --decision <preserve_all|reject|cancel>
  --actor <actual_actor>
  --confirmed-at <user_literal_or_not_provided>
  --output-dir D:\MyPythonProjects\datainsight\outputs\W3\strategy-<approved_run_id>
```

只在获批真实上游／摘要工具读取范围内核验；先展示唯一口径，再取得真实人工决定。actor／确认依据不伪造，功能运行工具独立取recorded_at。命令本身不授予源CSV读取许可。

E3真实执行拟议argv（同一cwd／环境）：

```text
.venv/Scripts/python.exe -B -m datainsight.analysis execute
  --strategy D:\MyPythonProjects\datainsight\outputs\W3\strategy-<approved_run_id>\strategy.json
  --output-dir D:\MyPythonProjects\datainsight\outputs\W3\analysis-<approved_run_id>
```

这一次许可必须明确包含固定CSV按块hash、严格解析、固定聚合及后hash、必要核验链读取和本地结果文档，不隐含全量画像／重跑。对真实源最多一次E3入口执行；前后hash和方法查询是已披露的内部动作，不称“只打开源一次”。

## 【批次顺序与停止条件】

1. **F3**：已完成详细安排确认；标准frozen、方案／交接accepted，内容未变。冻结只确认契约，不授权实施／运行。
2. **E3-OFFLINE**：一次精确预授权新增两文件、合成fixtures／scratch、命令／证据／结果文档；可候选批准首次＋至多一次合成重跑，修正只限这两文件内本契约缺陷。首批通知后在范围内连续做完交回，不按文件拆批。次数／修复范围须用户明确批准。
3. **离线技术验收**：执行者交回真实结果，high判定限定离线是否通过；离线未通过不继续真实门。
4. **G3.5**：独立真实核验链读取许可＋独立人工策略选择，再记录；缺件／版本变化／reject／cancel停止。
5. **E3-REAL**：独立当次真实读取和准确命令授权，一次完成S4→S5→草稿／文档交回；失败不自动重跑或提高资源，不更改口径。
6. **W3技术验收**：high据真实证据判定；**随后S6**由用户另行决定与记录，不自动转阶段。

每批开始一句话说明目的／范围／命令；用户叫停则停止新动作。新依赖、旧功能修改、上限／方法／口径变更、超出批准路径、次数耗尽或未知能力均暂停请求。真实读取重跑必须新许可，即使合成次数仍有余额。

## 【完成后一次交回】

- 结果文档路径、运行命令／环境／退出、必要证据路径与D301–D312逐项实测／未测状态。
- 合成参考和负向／故障汇总、新真实结果／S5／草稿／终态分别列示；失败保留原因与部分产物，未知不填成成功。
- 指定旧文件保护通过独占新增、输出拒绝直接断言及必要身份绑定说明，不增加全历史清单或重验上游。
- INDEX仅导航新结果，记录“未验收，待规划／验收方判定”；不改标准／旧结果，不自行标通过。
- 对话40行以内，只给结论／状态／下一门；不生成教学交接、额外Agent／Session或对话存档。
