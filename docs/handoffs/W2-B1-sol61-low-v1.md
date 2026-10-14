# W2-B1 · sol6.1 low 自包含执行交接 v1

> 详细契约与 B101–B112 已确认冻结；本文件是执行交接，**不是实现、运行、联网或实际 S3 审核授权**。用户手动转交 low，不自动创建 Agent／Session，不声称切换模型。

## 0. 可复制启动文字

```text
请只读 D:\MyPythonProjects\datainsight\docs\handoffs\W2-B1-sol61-low-v1.md，以及其中必要契约／代码，接续 W2-B1。
你负责用户指定的 sol6.1 low 执行，不宣称已切换模型，不自行最终验收。
详细接口、固定口径草案与 B101–B112 已确认冻结；不重问领域、项目路径、DeepSeek 或 D 盘规则，不重验或重装 W1/W2-A。
这条启动消息仅授权按需本地读取，没有文件修改、命令、安装、联网或 API 权限。
先只读核对，列出具体冲突（无则写无），再给出 P-B1-IMPL 的精确新文件清单、目的与影响，等待批准。
批准后仅做“核验 S2 accept→确定性候选与口径→独立 S3 审核记录”闭环；后续合成测试、真实入口、用户业务审核、结果文档逐批请求权限。
技术标准确认不是用户的实际候选选择，不得默认 approve，不自动启动清洗／S4／W2-B2。
对话只给结论与决策点，60 行以内；获批详细材料放 docs/，不落盘对话推理、讨论或临时文字草稿。
```

## 【目标】

只做 W2-B1：重新核验固定 S2 accept → 从封闭合格方法生成候选方案与完整指标定义 → 用户选择并确认口径，或拒绝／取消 → 新 run 保存独立 S3 receipt。

唯一注册方法为 `M-BEHAVIOUR-RECORDS`。结束于 S3，不执行候选、不重新统计、不读取生产 CSV、不清洗、不执行 SQL、不接模型、不自动进入 S4。

## 【前置状态与权威文件】

项目根：`D:\MyPythonProjects\datainsight`，不是聊天当前工作区。所有相对路径均基于项目根。

先只读：

1. `docs/W2-B1-plan-v1.md`：accepted，详细接口与固定口径草案已确认。
2. `docs/acceptance/W2-B1-v1.md`：frozen，B101–B112 全部必需，条款未变。
3. `docs/decisions/ADR-004-W2B-candidate-and-review-boundary.md`：闭环与模型职责边界。
4. `docs/decisions/ADR-003-directory-and-evidence-layout.md`：目录与原子发布例外。
5. `docs/acceptance/results/W2-A-final-review-v2.md`：W2-A 通过及局限；旧 v1 不通过记录不改。
6. 必要处读 `src/datainsight/feasibility.py`、`feasibility_rules.py`、W1 读取契约与 `profile_templates.py` 的封闭 behaviours 定义；不启动查询。
7. 选择接口回归时按需读既有测试，不 discover 全仓、不扫描 venv／缓存／全部旧 run。

用户“确认”是接口、口径草案与 B101–B112 的冻结依据；随后“批准”仅授权 P-B1-DOC-F 状态落盘与本交接新建。精确确认时间未提供，不以保存或运行时间代替。

ADR-004 保留原先“详细标准 draft”的历史描述，本轮未授权改 ADR；详细标准当前状态以方案与标准文件头为准，不因此重问或修改 ADR。

### 已有环境与能力

- W1、W2-A 已通过，不重新从零验收或安装。
- 既有项目 venv：Python 3.12.9、DuckDB 1.4.1；本闭环仅标准库，不连接／查询 DuckDB。
- W2-A 真实历史画像诊断与用户 S2 accept 已保存；本阶段仍必须重新调用 `verify_decision` 验证实际文件，不只读取 receipt 文本。
- W1 最后生产计算：`outputs/W1-B/final-20261009T061339601505Z/`，修复前协议；修复后合成收尾：`outputs/W1-B/b09-finalization-20261009T063948192695Z/`。两类证据不合并，不补造旧 final-status，不重跑生产。
- W2-B1 未实现／未运行／未验收。文档冻结不等于运行通过。
- W2 使用 DeepSeek 的选择保持；本闭环不调用任何模型。实际接入、准确 provider/model、结构化能力、脱敏 payload 与计费预算门留在 W2-B2 独立规划／授权。

准备包新稿为 `D:\DataInsight-Prep\insight-agent-planner\SKILL.md`；只在实际需要时核对当前相关 references。安装的旧技能不能覆盖用户已确认的新稿，也不安排自动教学／面试交接。

## 【输入：固定真实来源与读取清单】

### 固定 S2 入口

```text
outputs/W2-A/s2-accept-3178ad8b677e49edb91de623be0c3905/decision.json
outputs/W2-A/local-syn-3178ad8b677e49edb91de623be0c3905/diagnosis.json
docs/acceptance/results/W2-A-final-review-v2.md
```

真实 S2 与诊断两个目录内核验需要：

```text
final-status.json
input-manifest.json
reference-check.json
environment.json
network-observation.json
cli-command.json
```

固定历史画像包：

```text
outputs/W1-B/final-20261009T061339601505Z/production/profile.json
outputs/W1-B/final-20261009T061339601505Z/production/fingerprints.json
outputs/W1-B/final-20261009T061339601505Z/production/summary-evidence.json
outputs/W1-B/final-20261009T061339601505Z/production/summary-result.json
outputs/W1-B/final-20261009T061339601505Z/production/columns-evidence.json
outputs/W1-B/final-20261009T061339601505Z/production/columns-result.json
outputs/W1-B/final-20261009T061339601505Z/production/behaviours-evidence.json
outputs/W1-B/final-20261009T061339601505Z/production/behaviours-result.json
outputs/W1-B/final-20261009T061339601505Z/production/duplicates-evidence.json
outputs/W1-B/final-20261009T061339601505Z/production/duplicates-result.json
outputs/W1-B/final-20261009T061339601505Z/production/timestamp-evidence.json
outputs/W1-B/final-20261009T061339601505Z/production/timestamp-result.json
outputs/W1-B/final-20261009T061339601505Z/production-commands.json
docs/acceptance/results/W1-final-acceptance-and-handoff.md
configs/w1b-read-contract-v1.json
configs/w2a-question-v1.json
```

版本核验还需 `feasibility_rules.py` 与本阶段新增注册表的源码字节。读取清单按实际源码核对后再列于真实入口动作请求，不因保存 manifest 有路径就扩大范围。

- 所有来源只读；不得打开 evidence 的 source_path，不执行保存 SQL／参数。
- `dataset_version` 匹配上游已有证据，不重新读取 CSV 计算源哈希。
- 历史生产包采用 W2-A 已验收的精确来源特例；不要要求补造修复后终态。
- `verify_decision` 接受有效的多种决定记录；本阶段 wrapper 必须进一步要求 accept 和合法 supported 诊断，不把“格式有效”当“已受理”。
- 数据、问题、规则、manifest 或 receipt 变化停止；不要自动重做 accept 或为旧批准更新绑定。

## 【输出与写入边界】

### P-B1-IMPL 获批后唯一新增实现名单

| 文件 | 职责 |
|---|---|
| `src/datainsight/planning.py` | 固定来源核验、候选／审核独立 CLI、绑定恢复与本阶段收尾 |
| `src/datainsight/planning_methods.py` | 封闭候选与口径 metadata、稳定版本／摘要 |
| `tests/test_w2b1.py` | 正常／独立反向、版本恢复、人工门、真实发布故障、隐私观察及证据 runner |

目标已存在不得覆盖；需要额外文件或改动既有实现先停止提出精确冲突。不要修改 W1/W2-A 模块、配置、测试、标准、ADR 或旧证据。

不新建预填 approve 的真实审核配置，不在项目根添加 runner。测试支持代码可以放在本测试文件内，但不成为新的产品框架。

### 合成与正式证据

- 合成批次 ID 建议为 `w2b1-syn-<工具生成 uuid>`，必须保存实际值，不手填运行时间或猜摘要。
- 输入固定在 `outputs/_scratch/<批次>/<test_method>/<case_id>/`。
- 合成正式 run 固定在 `outputs/W2-B1/<批次>-<test_method>-<case_id>/`，新目录、无清理。
- 真实候选 run 建议 `outputs/W2-B1/w2b1-candidates-<工具生成 uuid>/`。
- 真实审核 run 建议 `outputs/W2-B1/w2b1-review-<工具生成 uuid>/`，独立于候选。

具体合成包文件／case 命名由执行者在 P-B1-SYN 请求前列明；全部是工具生成的受控聚合画像／问题／receipt，不复制原始业务行或生产源指纹。构造缺件时直接省略，不删除旧文件。

复用上游真实核验函数做合成链测试时，可在测试上下文将 `feasibility.FIXTURE` 指向本轮 scratch，将 `feasibility.OUTPUT` 指向本轮获批的 W2-B1 合成来源目录；只改变测试进程的固定常量，退出恢复，不写 W2-A 原目录、不改变功能源码、不扩展生产入口。patch 范围与其局限须记录，不能让产品 CLI 通过 fixture 选项读取任意目录。

候选 run 至少含：

```text
candidate-plans.json
accepted-context.json
input-manifest.json
reference-check.json
environment.json
network-observation.json
cli-command.json
final-status.json
```

审核 run 至少含 s3-review.json、绑定 manifest／reference-check、environment.json、network-observation.json、cli-command.json、final-status.json。

测试主批次需真实命令／环境、测试日志／汇总、测试与功能源码身份、独立 case 结果、故障矩阵、读取／调用观察、隐私扫描、逐文件清单与保护摘要。实际文件名须在运行请求中列明；报告自引用排除明确，不能无界生成文件或静默截断覆盖。

同目录原子发布 `.tmp` 是必要例外；它不属于一般 scratch，不迁移／自动清理。旧失败 run 与本轮故障 run 原位保留。

### 文档输出

P-B1-RESULT-DOC 获批后只新增 `docs/acceptance/results/<run_id>.md` 并更新 INDEX 的待验收导航。不要改冻结标准或自己标最终通过，不回写旧验收或执行记录。

## 【接口与结构：已确认，不重新设计】

```text
load_s2_accept(decision_ref) -> AcceptedContext
build_candidate_plans(context, registry) -> PlanSet
record_s3_review(plan_set_ref, review, output_dir) -> S3Receipt
```

### AcceptedContext

schema_version、dataset_version、S2 receipt_ref/hash、diagnosis_ref/hash、question_version/hash、diagnostic_rules_id/version/hash、input_manifest_ref/hash、eligible_method_ids、prerequisite_checks、evidence_refs、acceptance_basis、limitations。

包装现有真实验证结果，不信任用户构造的任意上下文。hash 由工具计算，初始摘要不是协同篡改防护。上下文只含摘要／证据，不包含源读取或新计算权限。

### PlanSet／候选

PlanSet：schema_version、run_id、stage=S3、status=computed_pending_finalization、accepted_context_ref/hash、dataset_version、question_identity、diagnostic_rules_identity、registry_id/version/hash、plan_set_version、candidates、human_review_state=pending、limitations。

每项候选：plan_id/version、method_id、rule_version、question_ref、required/optional_fields、grain、prerequisites、satisfied_evidence、unmet_conditions、metric_definition/version/hash、expected_output_schema、assumptions、risks、limitations。

- 只注册 M-BEHAVIOUR-RECORDS；需要 behaviour 列及已核验工具引用，不要求伪造订单语义。
- 前提全部 met 才生成；不允许人确认覆盖 unknown。未知方法或任意规则／SQL作为校验错误拒绝。
- 空候选仅在受控逻辑测试中按合法上下文语义构造，不伪造生产 accept；不凑候选或做商业优先级评分。
- 规则身份与方案 registry 身份分开；源码摘要与候选／指标规范序列化摘要由工具计算。
- 候选不带业务结果值，只引用现有 result；预期 schema 不是已计算结果。

### ReviewSpec／S3Receipt

ReviewSpec：decision=approve／reject／cancel、selected_plan_id/version、metric_definition_hash、confirm_metric_definition、actor、confirmed_at。

approve 必須集合内精确候选／版本，metric_definition_hash 匹配，confirm_metric_definition=true，真实 actor／确认时间；缺任何项拒绝。不接受审核输入中的自由指标改写。reject／cancel 不附伪造选择，保存停止决定但不推进。

S3Receipt：schema_version、独立 review run_id、plan_set_ref/hash、selected_plan_id/version、metric_definition_version/hash、dataset_version、S2／诊断／问题／规则／registry／manifest 绑定、decision、actor、confirmed_at、acceptance_scope=S3_plan_and_metric_only。

数据／问题／规则／registry／候选／metric 变化令旧审核失效；恢复重新核验，不默认 approve，不回写上游。S3 scope 不授权 S3.5、S4、清洗、查询、外发或模型调用。

## 【固定指标口径：不能擅自改】

| 项目 | 定义 |
|---|---|
| 含义／主体／粒度 | 读取后的原始记录及 behaviour 代码；不是订单、支付、独立用户或会话 |
| 指标 | 固定桶原始记录数，不填写新业务值 |
| 计数对象／分子 | 对应桶内记录；不是比例分子 |
| 分母 | not_applicable；不生成占比、转化率 |
| 窗口 | 绑定 dataset_version 的全文件范围；日期覆盖未确认 |
| 时间单位／时区 | unknown；无日期分组、排序或时间过滤 |
| 分类 | pv／fav／cart／buy 精确文本；NULL→missing；其他非 NULL→other，不展开未知原文 |
| 全局过滤 | 无记录排除，桶分类谓词不是删数据 |
| 空值 | behaviour NULL 计入 missing；其他列空值不排除记录；不填补 |
| 重复 | 全部保留，按原始记录计数；重复候选不是错误判定 |
| 文本 | 不 trim、不改大小写，保持 W1 读取契约 |
| 维度／聚合 | 固定 behaviour 桶、COUNT记录；不去重、用金额或按用户分组 |
| 变换／清洗 | raw_preserved_no_transformation；是方案说明，不是 S3.5 批准 |
| 预期产出 | 固定桶与计数字段的 schema／名称，不是新的结果 |
| 依据 | schema、behaviours evidence/result、读取契约、封闭模板定义引用 |

技术标准确认固定此草案，**不是用户的当次 S3 业务决定**。实际成功候选与摘要展示后，用户才能选择并确认。

## 【验收索引：完整要求以 frozen 文件为准】

| ID | 执行者必须提供 |
|---|---|
| B101 | 固定真实 receipt 新进程核验；显式 accept／supported 门；其他决定、缺终态／引用拒绝 |
| B102 | 路径先核对；独立 JSON／schema／类型／版本／大小反向与对应原因，危险目标未打开 |
| B103 | 上下游实际字节、规则与 registry 绑定；独立篡改／缺件／版本错配拒绝，无原始源读取／SQL执行 |
| B104 | 封闭候选、零候选与未知方法反向、稳定内容与源码身份 |
| B105 | 完整固定口径及模板／契约一致性，错误金额／订单／日期／漏斗／去重／过滤不得混入 |
| B106 | 方案结构完整且不带业务值；无依据指标／数值拒绝，预期非结果 |
| B107 | 人工选择与确认门；API／CLI反向；真实 S3 决定由用户作，不预填 approve |
| B108 | 恢复／绑定变更失效、不能审核时改指标、不默认批准，不自动 S4 |
| B109 | 独立新 run、已有输出拒绝、源候选／旧文件本次保护、scope不扩大 |
| B110 | 两条 CLI 正常、各收尾文件故障与真实 publish 的底层持久化／改名故障；真实状态／tmp记录 |
| B111 | 读取／调用观察与输出／错误／trace敏感／指令哨兵扫描；固定范围与排除明确，usage不适用 |
| B112 | 项目解释器／实际 D盘临时、正常反向与必要接口回归、完整命令／清单／保护摘要与待验收文档 |

不要重演 W2-A 累积错误测试缺口：每个主要错误都从可接受基线独立构造，精确断言拒绝原因，缺件创建时省略。异常 mock 不能把功能真实行为全替掉再宣称功能通过。

真实 publish 测试保留正常路径，再按 target 限定 I/O包装／OSError注入临时打开／写入／flush／fsync／rename；不能只 mock 整 publish。失败为非零，无发布 success；失败终态不可写如实报告，tmp残留保留；不扩成真实危险系统攻击。

隐私扫描覆盖合法元数据哨兵的候选／审核／错误／trace与捕获 stdout／stderr；受控 fixture／源码快照分列，不豁免所有报告。枚举只在批准批次与必要固定旧目录，报告自己缺摘要明确，不无限重写证据。

实际测试错误或功能失败须保留证据并停止后续真实入口。实现需要改变既有标准或 W2-A 时报告精确冲突，不能默默加权限／缩断言。

## 【命令与运行申请】

当前尚无 planning CLI／test_w2b1 runner，不冒称命令已存在。本文件给拟议入口，最终 argv 由执行者实现后只读核对并列于运行请求，命令不得先跑后补权限。

合成批次可在 `tests/test_w2b1.py` 内新增证据 runner，拟议入口：

```text
项目 .venv/Scripts/python.exe -B -m test_w2b1 --w2b1-evidence
```

runner 将测试、来源身份、故障／扫描／清单／环境与真实退出状态写新批次，不能自动转到真实入口或选择 S3。由执行者提出必要接口回归的精确方法名，核对不读 CSV、不查询引擎、不自动清理；不运行 W1/W2-A 全套或历史 runner。

真实候选拟议入口：

```text
项目 .venv/Scripts/python.exe -B -m datainsight.planning candidates --output-dir <新候选 run>
```

固定真实 receipt 不因 CLI 用户参数变成任意输入。若要显式指定它，只允许固定精确来源，不扩目录。

审核拟议入口：

```text
项目 .venv/Scripts/python.exe -B -m datainsight.planning review <成功候选引用、用户决定与真实确认字段> --output-dir <新审核 run>
```

具体审核 flags 在实现后报实际完整 argv；候选 ID、指标摘要由工具输出取得，approve 只能用用户明确选择，不使用占位值或规划确认代替。保存原始外层命令／环境与实际 argv；如果 -c wrapper 调用 main，不能把重建模块 argv冒充外层真实 -c命令。

所有获批命令显式项目 cwd，PYTHONPATH 指向项目 src／tests，PYTHONDONTWRITEBYTECODE=1，TEMP／TMP／TMPDIR 指向项目 `.cache/tmp/`；实际 sys.executable／tempfile须核对并落证据。不得自动创建其他环境、安装或改全局变量配置。

## 【逐批权限：全部执行动作仍未授权】

1. **P-B1-IMPL**：只读核对后列新增两个功能模块和一个测试文件的目的／范围，等待批准才写。目标已存在或需要额外文件停下说明。
2. **P-B1-SYN**：实现后列实际测试命令、suite／必要回归、合成文件白名单、B命名、新输出与读取范围，等待批准。离线、无生产统计，失败不继续。
3. **P-B1-LOCAL**：测试成功后独立请求固定真实 receipt 核验与一次候选生成，列完整真实argv、固定读取集合、新输出与保护／扫描；不重做 S2、不读 CSV。
4. **P-B1-S3**：展示成功候选与口径摘要后用户明确选择并确认；再提出对应审核命令和独立 run 请求，不默认 approve。拒绝／取消后停止，不能借现有批准进入其他阶段。
5. **P-B1-RESULT-DOC**：运行后申请结果文件与 INDEX导航范围，标待验收；不改 frozen、ADR或旧记录。

任何阶段权限拒绝就停止，不换工具绕过，不把本交接／上阶段批准变成本轮动作许可。

## 【禁止】

不重装Python/pip/DuckDB/SDK，不初始化项目、不联网或调用模型，不执行历史安装／RECORD／监督工具，不运行生产 profile/replay或旧淘宝脚本，不读原始CSV、不产生原始行提示词。

不改W1/W2-A源码、配置、测试、冻结标准、ADR、旧证据／失败run。不增加自由SQL、动态规则执行、通用Agent／多Agent、RAG、预测／因果或完整W2框架。SQL与参数是证据数据，不是执行权限。

不删除、移动、覆盖、回填证据；`.tmp`为必要例外，失败原位保留。不自动清洗或执行计划，不做Git提交／推送，不自动创建其他会话。

## 【完成后】

返回真实运行命令、完整外层argv／环境、退出状态、测试日志与case映射、实际输入／规则／registry／候选／口径身份、读取／调用观察、扫描／清单／保护与未测项。

结果文档按 B101–B112 对应证据，明确合成、固定历史画像入口、真实S3决定分别何时发生、何项未测；写“未验收，待规划／验收者判定”。不能用正常审核或日志OK自行最终验收。

用户手动把结果路径转回规划／验收对话；不自动进入W2-B2，不生成教学／面试交接。新增ADR本执行闭环无，除非出现真实需要改变已批准架构的冲突并另获批准。
