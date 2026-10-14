# W2-A 最终验收记录 v1

## 1. 总判定与效力

**总判定：不通过。** 当前必需反向测试及证据未闭合，不可有条件放行。此结论针对本文件列出的当前证据版本，不是否定已成功的正常诊断与 S2 accept 演示。

- 对应冻结标准：[W2-A-v1](../W2-A-v1.md)，frozen；A01–A15 未修改。
- 对应方案：[W2-A-plan-v1](../../W2-A-plan-v1.md)。
- 目录规约：[ADR-003](../../decisions/ADR-003-directory-and-evidence-layout.md)，保持 accepted。
- 执行方记录：[s2-accept-3178ad8b677e49edb91de623be0c3905](s2-accept-3178ad8b677e49edb91de623be0c3905.md)，保留当时“未验收，待规划／验收者判定”状态，不回写。
- 验收者职责：用户指定 sol6.1 high 规划／验收；没有探测或切换实际模型。
- 验收方式：文件工具直接读取已存在运行证据，结合实现与测试断言审查；不以用户描述或执行方自评代替证据。
- 本轮文档权限依据：用户对“新建本记录并更新 INDEX”的请求回复“批准”；精确确认时间未提供，不以文档日期、运行时间代替。
- 本轮没有执行命令、测试、独立哈希计算、安装、联网、外部 API 或实现修改。
- 不解锁 S3／W2-B；不改变 W1 通过判定，不重新开启 B01–B09。

本轮最小闭环是验收结论落盘与导航同步，不是补测运行。本文的后续补证要求不构成写代码或运行授权。

## 2. 直接读取的证据

项目根：`D:\MyPythonProjects\datainsight`。以下路径相对项目根。

### 2.1 受控合成批次

根：`outputs/W2-A/syn-3178ad8b677e49edb91de623be0c3905/`。

直接读取：

- `test.log`
- `batch-result.json`
- `batch-command.json`
- `cli-finalization-7.json`
- `decide-fault-6.json`
- `test_A13_no_source_open_or_sql_execution-reads.json`

`test.log` 记录 23 tests、5.397s、OK；`batch-result.json` 记录 tests_run=23、failures=0、errors=0、exit_status=0、final_acceptance=not_performed。上述数值直接引用工具产物，不是本轮重新运行或估计。

日志证明所列测试运行成功，不证明断言覆盖了每个冻结要求。故障矩阵其他用例通过日志和对应测试源码核对；本轮没有逐一打开所有子 run 或把有限读取说成全批次文件审计。

### 2.2 固定历史画像输入诊断

根：`outputs/W2-A/local-syn-3178ad8b677e49edb91de623be0c3905/`。

直接读取 `diagnosis.json`、`input-manifest.json`、`reference-check.json`、`environment.json`、`network-observation.json`、`cli-command.json`、`final-status.json`。

观察：

- request_state=valid、capability=supported、合格方法仅 M-BEHAVIOUR-RECORDS、gaps 为空。
- 必要前提引用 schema 与 behaviours 工具结果；质量观察引用 columns／duplicates／timestamp。
- diagnosis.status=computed_pending_finalization、human_decision_state=pending。
- final-status.status=success、exit_status=0，完成时间 `2026-10-09T09:04:24.201196+00:00`。
- reference-check 明确 acceptance_basis=accepted_legacy_production、source_kind=historical_production。

目录名称含 syn 不能作为合成输入判据。该 run 只是对已验收历史聚合画像的诊断，不是新生产统计或当前源 CSV 校验。

### 2.3 独立 S2 决定

根：`outputs/W2-A/s2-accept-3178ad8b677e49edb91de623be0c3905/`。

直接读取 `decision.json`、`input-manifest.json`、`reference-check.json`、`environment.json`、`network-observation.json`、`cli-command.json`、`final-status.json`。

观察：

- receipt.decision=accept、actor=user、acceptance_scope=S2_only。
- receipt 引用上述诊断 run，包含 diagnosis_hash、dataset_version、question_version/hash、ruleset_version/hash、input_manifest_sha256。
- receipt 的绑定字段与诊断／manifest 中相应已保存字段一致；这只是保存字段的读取比对，本轮未独立重算字节摘要。
- final-status.status=success、exit_status=0，完成时间 `2026-10-09T09:40:26.020352+00:00`。
- confirmed_at=`2026-10-09T09:40:25.855605+00:00` 是执行记录所说明的工具记录操作时间，不是用户消息的精确时间。
- 执行结果文档记载用户曾明确选择 accept 并单独批准命令；本轮没有读取另一执行会话的原始批准消息，不把 receipt 当身份认证或独立权限审计。

决定独立保存，原诊断仍 pending；正常闭环没有把运行成功自动当作人工受理。业务 accept 不代表阶段验收通过，不授权后续执行。

### 2.4 代码与测试审查

直接读取／定位：

- `src/datainsight/feasibility.py`
- `src/datainsight/feasibility_rules.py`
- `tests/test_w2a.py`
- `configs/w2a-question-v1.json`
- 本阶段冻结标准及执行结果／INDEX。

本轮没有全仓差异审计、源 CSV 读取、W1 重新验收、完整运行文件枚举或全系统监控。

## 3. A01–A15 逐项判定

“通过”仅指冻结范围内已审查证据足够支持该项，不代表未测的通用能力。各项局限不自动成为新增要求；“不通过”仅基于必需证据缺口。全部必需项闭合前总判定不通过。

| ID | 判定 | 已核对证据／断言 | 原因与边界 |
|---|---|---|---|
| A01 | 通过（限冻结输入范围） | 历史诊断 reference-check／终态；日志中的 current_protocol_and_old_success_rejection、pending_failed_missing_terminal；feasibility.py:195–240 | 精确 legacy 特例与 fixture 新协议分支分开；其他路径受固定边界拒绝，不泛化旧 success。缺终态测试使用 mock，不能宣传真实新生产协议实测。 |
| A02 | 不通过 | test.log；test_w2a.py:140–160、338–351；feasibility.py:98–151、212–222 | 路径、大小、重复键、非有限数与类型已有运行测试；但额外键／未知版本／错误 schema 连续修改同一输入，后两项可能仍因 extra 键拒绝，不能证明其独立拦截。 |
| A03 | 不通过 | 历史 manifest／reference-check；test_w2a.py:162–174；feasibility.py:241–305 | 已验证结果引用、结果篡改和指纹错配；缺读取契约变化、实际关联文件缺失等针对性反向证据。源码存在检查不能替代这些必需运行证明。 |
| A04 | 通过（结构化问题范围） | 配置；test_w2a.py:176–185；feasibility.py:316–336、524–562 | 无问题／未知 intent／额外 SQL、路径、规则、字段映射受控测试，未知请求无合格候选；不宣称支持自由文本解析。 |
| A05 | 通过 | 实际 diagnosis 两条 met、单一合格方法；test_w2a.py:187–194；feasibility_rules.py:49–63 | 原始记录计数前提有 schema／工具引用，未转换为订单／支付或新比例；没有新统计计算。 |
| A06 | 通过（规则层负向） | test_w2a.py:196–203；feasibility_rules.py:64–69；test.log | GMV 无合格方法，列金额字段／定义缺口，不产生 GMV 值。冻结标准允许规则层负向证据，不要求额外真实 GMV CLI run。 |
| A07 | 通过（受控 snapshot 范围） | test_w2a.py:196–207；规则与诊断 limitations | 缺工具引用为 conditional，缺字段为 unsupported，严格漏斗不入候选。snapshot 单测不扩大 CLI 画像契约，也不确认日期／时区／事件顺序。 |
| A08 | 通过（固定观察输出范围） | 实际 quality_observations／limitations；test_w2a.py:187–194；feasibility_rules.py:9–16、36–41 | 质量观察固定引用工具而不清洗／推断。fixture 主要是零值，非零重复、other 和小样本的独立语义覆盖不足，保持局限；不因此扩为新计算或新方法要求。 |
| A09 | 通过 | test_w2a.py:209–214；规则源码与 diagnosis 的规则身份 | 同输入稳定、未知规则拒绝、候选可为空。ruleset_hash 只覆盖规则源码，符合规则摘要要求，不宣称整个实现的完整性认证。 |
| A10 | 通过（本地人工记录范围） | 实际独立 accept receipt；test_w2a.py:216–226；decide 正常／故障日志 | 运行与受理分离；条件不足不能 accept；缺 actor／时间的 API 反向已运行。reject／cancel 测试是受控决定，不冒充用户业务选择。 |
| A11 | 通过（合成恢复与绑定范围） | test_w2a.py:228–243、296–312、353–365；实际 receipt 绑定字段 | 已有 load_diagnosis／verify_decision 合成恢复与版本变更拒绝测试；不自动 S3。真实 receipt 未在独立新进程重启 verify_decision，保留未测，不额外要求为本轮阻塞。 |
| A12 | 不通过 | cli-finalization-7.json、decide-fault-6.json；test_w2a.py:245–252、268–294、314–336；feasibility.py:493–505、594–609 | diagnose 发布失败整体 mock publish；decide 故障矩阵止于命令证据，没有经真实 publish 的 CLI 发布失败。helper 改名失败只证明残留 tmp，无两条 CLI 持久化／发布故障完整闭合。 |
| A13 | 不通过 | reads.json；两真实 run 网络观察；test_w2a.py:254–266、187–194 | 有适配层读取观察、部分哨兵断言及零产品模型标记；缺输出／错误／trace 的哨兵扫描范围与结果报告，不能仅从 blocked_events=[] 推出隐私验收完成。 |
| A14 | 不通过 | test_w2a.py:367–373；实际 environment、helper tmp 测试 | 已存在输出拒绝、实际 D 盘临时路径和 tmp 保留有依据；实际产物仅有文件族导航而无完整清单，目录保护／扫描范围证据尚未闭合。不要求补造本批旧证据“运行前”哈希。 |
| A15 | 不通过 | test.log、batch-result、batch-command、两真实 CLI 命令与执行文档、INDEX | 所选测试及两项 W1 接口回归成功，阶段记录与导航分开；但上述必需反向及扫描／产物证据缺口未补齐，尚不能满足全部正常／反向与证据交付。 |

以上不是按测试数量打分，不计算或推广“准确率”。整体阻塞是 A02、A03、A12 以及 A13–A15 的必需证据充分性，不允许把这些安全、隐私与证据项作为非阻塞遗留放行。

## 4. 最小补测／补证要求

下一闭环只关闭下列缺口，不重发实现、不改接口、不放宽标准。补测需另行批准测试文件修改、命令和新证据目录；本文件不授权执行。

### R1：独立输入反向（A02）

定位：`tests/test_w2a.py` 的 `test_A02_json_strictness`，当前第 140 行附近；生产检查参考 `feasibility.py` 的 `load_accepted_profile`。

- 从合法基线为每个错误创建独立合成输入，不能保留前一个错误。
- 分别覆盖 extra 键、schema_version 未知、reading_schema 错误；先确认相应基线能合法载入。
- 断言失败原因对应各自校验，例如 invalid_object_keys／profile_identity／reading_schema，而不仅是任意 BoundaryError。
- 不改标准或为了通过而删除反向项；不修改旧 fixture／旧 run。

### R2：输入关联完整性（A03）

定位：`tests/test_w2a.py` 的 A03 输入完整性测试；检查函数为 `load_accepted_profile`。

- 使用新受控合成包补读取契约摘要／版本不符、实际必需关联文件缺失、run／dataset_version／引用错配的独立用例。
- 不修改真实 `configs/w1b-read-contract-v1.json` 或 W1 生产包。必要时把模块的契约路径指向获批的新合成副本，明确 mock 范围。
- 文件缺失通过构造缺件的新包证明，不删除或移动旧证据。
- 保存用例身份、实际拒绝原因、运行退出状态；已有结果篡改／指纹测试继续保留回归。
- 这是目标缺口补测，不要求穷尽每个文件的每一字节，也不宣称协同篡改防御。

### R3：经真实发布路径的 CLI 故障（A12）

定位：`tests/test_w2a.py` 的两个 A12 CLI 故障测试与 publication helper 测试；发布函数为 `feasibility.py:493` 的 `publish`，错误收尾为 `main`。

- 正常用例继续保留；受控 CLI 输入可用合成包／mock，不运行 W1 生产计算。
- diagnose、decide 均经真实 `publish`，在临时写入、flush／fsync、rename 等持久化／发布环节注入针对性 I/O 失败，而不是整函数 mock 后替代证明。
- 保存实际 argv、故障位置、返回值、最终状态、计算状态、源诊断不变检查、tmp 路径及是否残留。
- 必须非零，无已发布 success；失败终态不能写入时明确 failure_evidence_persisted=false。
- `.tmp` 是 ADR-003 的原子发布必要例外，必须同目录／同文件系统，失败残留原位保留，不迁移或清理。
- 不扩为全系统崩溃恢复或并发攻击测试；现有代码能否正确通过这些用例须由真实运行证明。只有实际失败才提出最小实现修复及独立权限。

### R4：隐私与产物范围报告（A13–A15）

定位：`tests/test_w2a.py` 的 A13 读取／哨兵测试，以及获批的补证运行记录流程。

- 在新受控 fixture 注入明确的原始行／标识／敏感文本哨兵；按冻结范围核对它们不能通过诊断、决定、错误输出或 trace 泄露，也不能诱发读取／执行。
- 新证据报告明确扫描哪些文件／标准输出／错误输出，哪些只包含受控输入哨兵、哪些是产品输出，避免把源 fixture 故意含哨兵当产品泄露。
- 扫描既有真实 run 可只读，报告写新补证 run；不重新发起真实 accept，不补造旧日志。
- 生成实际逐文件产物清单，明确包含哪些主批次、合成子 run、诊断 run、决定 run；限界枚举，不扫描全仓／venv／原始数据。
- 记录工具取得的路径、摘要（如使用）、命令、环境与退出状态；枚举或扫描有上限／遗漏就明确报告，不能声称完整。
- 不要求恢复不存在的历史运行前哈希。现在计算的摘要只能证明现在观察到的内容／本次只读前后状态，不能冒充此前运行前状态。
- 补证后重跑本轮正常／反向及已明确选择的必要 W1 接口回归，保留所有旧证据；不要重验 W1 或称两项接口回归为 W1 全回归。

## 5. 已确认能力与未测边界

### 可保留成果

- 固定历史聚合画像的原始记录前提诊断正常运行。
- 独立 S2 accept 的保存与有限版本绑定，不回写诊断。
- 封闭方法集、结构化问题、规则／质量观察分离及基础反向测试。
- D 盘项目解释器及实际生效 tempfile 路径的运行证据。
- 历史来源、合成测试、真实诊断、人工决定的证据类别正确区分。

### 不得据此宣称

- A01–A15 全部通过、完整 W2／S0–S6 Agent 或 S3/W2-B 已解锁。
- 当前原始 CSV 已重新校验、W1 修复后完整生产 CLI 实测。
- DeepSeek 调用、usage、费用或效果实测。
- 完整敏感输出扫描、所有故障环节已测、完整旧证据前后审计。
- 真实 Windows junction 攻击防御、同机并发路径替换防护、全系统网络隔离或协同篡改防御。

历史 W1 最后生产计算根仍为 `outputs/W1-B/final-20261009T061339601505Z/`；修复后合成收尾根仍为 `outputs/W1-B/b09-finalization-20261009T063948192695Z/`。W2-A 不把它们合并为同一次运行。

## 6. 证据与文档保护

- 本轮仅新建本文件并更新 INDEX 的判定导航，不改执行方结果、冻结标准、源码／配置、ADR 或旧证据。
- 所有 `outputs/<阶段>/<run_id>/` 保持稳定，不移动、删除、覆盖或回填。
- 新补证必须使用新 run，新的详细结果另存；未来复验通过也不抹掉本次不通过记录。
- 一般临时工具文件只在 `outputs/_scratch/` 或 `.cache/tmp/`；run 内原子发布 `.tmp` 是必要例外，不是待清理项。
- 本文件是审定验收结论与补证要求，不是聊天推理、讨论存档或临时文字草稿。

## 7. 下一步、决策与权限

待用户产品决策：本轮无。无需重新选择领域、路径、DeepSeek 或 D 盘规则。

新增 ADR：本轮无；补证不改变架构或冻结标准，不为通过而新增放宽条款。

下一步建议：仅制定并执行 R1–R4 补测闭环，返回真实证据后再复验。执行文件修改、命令、扫描／枚举、结果文档及 INDEX 更新各自需说明精确范围并取得新批准；旧阶段权限和本轮文档批准不能复用。

本轮未新增执行交接文件，未启动补测。当前阶段总判定保持 **不通过**，正常 accept 记录仍原位保留，但不解锁后续阶段。
