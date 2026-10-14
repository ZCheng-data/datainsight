# W2-A：离线确定性诊断与 S2 人工受理记录方案 v1

- 文档状态：accepted；详细接口与对应验收标准已获用户确认，执行动作仍未授权。
- 批准依据：用户回复“确认”，确认详细接口与 A01–A15 验收；随后回复“批准”，授权 P-DOC-F 冻结状态落盘及 low 交接文档。
- 确认者：用户；精确确认时间：未提供，不以文档保存日期替代。
- 运行／验收状态：未实现、未运行、未验收。
- 规划／验收职责：用户指定 sol6.1 high；本文件不切换实际模型。
- 唯一执行者：用户手动转交 sol6.1 low；执行交接见 `handoffs/W2-A-sol61-low-v1.md`，不创建 Agent／Session，不自动执行。
- 项目根：`D:\MyPythonProjects\datainsight`；当前聊天工作区不是项目根，后续命令必须显式绑定项目路径。
- 本地使用：文件包含本机路径与证据引用，不作为 DeepSeek 请求 payload。

## 1. 一个最小闭环

结构化问题 + 已验收 W1 画像 → 确定性前提诊断 → 支持／有条件／不支持或补充问题 → 人工受理／补数／拒单／取消 → 带版本绑定的独立记录。

演示到 S2 人工记录即结束，不自动进入 S3，不执行候选方法，不新增业务统计。

### 范围

- 只读现有 W1 画像、对应工具证据及本地验收来源。
- 支持原始记录按 `behaviour` 代码分类计数的前提诊断；字段语义不确认时只描述代码，不解释订单／支付。
- GMV 与严格漏斗作为明确的负向需求检查，不纳入本轮可执行候选。
- 方法前提与质量观察分开。NULL／重复候选不自动变成拒单或清洗理由。
- 本轮不调用 DeepSeek；已确认的 W2 DeepSeek 选择保留，实际接入及首次调用门控在 W2-B。

### 非目标

自由文本自动理解、自由 SQL、重新读取生产 CSV、W1 生产重跑、新增 DuckDB 查询、清洗、S3 方案／指标口径最终确认、S4 计算、复杂框架、provider SDK、安装、网络、付费 API、README 全项目改写。

## 2. 已有接口核对与复用边界

| 现有位置 | 核对结果 | W2-A 处理 |
|---|---|---|
| `src/datainsight/profile.py` 的 `run_profile` | 当前返回 `computed_pending_finalization` | 不调用，不把计算返回值当成功输入 |
| 同文件 `verify_profile_references` | 核对画像引用、结果字节摘要及读取契约 | 借鉴其检查要求；不修改 W1，也不把其调用当零计算或零依赖证明 |
| 同文件 `validate_profile_result` | 封闭模板结果形状与类型 | 新适配层保持相同数据口径，不新增统计定义 |
| `src/datainsight/__main__.py` 的 `profile_entry` | 必需收尾后发布 `final-status.json` | 不修改或复跑 W1；W2-A 自己发布本阶段终态 |
| 同文件 `publish_final_status` | run 内同目录 `.tmp` 原子发布 | 遵守 ADR-003 必要例外；不迁到 `.cache/tmp/` |

W2-A 拟新增独立的标准库模块入口，避免改动 W1 `inspect/profile/replay` 命令。具体函数与 CLI 契约已获确认，尚未实现，不能称已存在。

## 3. 输入信任与历史来源

### 3.1 唯一历史生产输入

- 画像：`outputs/W1-B/final-20261009T061339601505Z/production/profile.json`。
- 关联：同目录五个固定模板的 `*-evidence.json`、`*-result.json` 及 `fingerprints.json`；证据指定的读取契约仅允许 `configs/w1b-read-contract-v1.json`。
- 本地验收来源：`docs/acceptance/results/W1-final-acceptance-and-handoff.md`。
- 必要运行索引：`outputs/W1-B/final-20261009T061339601505Z/production-commands.json`。
- dataset_version 必须匹配 W1 最终验收记录；实际指纹引用检查由执行工具完成，不在本文件估计新的哈希。

历史生产是修复前真实计算证据，没有当前协议的 `final-status.json`。允许该精确来源的本地验收特例，不追改或补造旧终态。特例不能推广为“所有 profile.status=success 均可接受”。

修复后收尾依据位于 `outputs/W1-B/b09-finalization-20261009T063948192695Z/`，是合成 CLI 正常／故障测试证据；只说明收尾协议，不为生产画像提供新的生产最终状态。W2-A 接受历史画像不代表验证当前原始 CSV 仍未变化。

### 3.2 本轮最小信任模型

- 宿主固定生产输入及本地验收来源，不允许问题 JSON／保存 SQL／证据参数扩大路径或执行权限。
- 读取前检查路径及重解析组件；受控合成测试走独立 fixture 来源，不能借 fixture 模式读取任意生产目录。
- 严格 JSON：拒绝重复键、非有限数、错误类型、额外键及不受支持版本。
- 核对 profile、template evidence、result 的 run／数据版本与引用关系，实际结果文件字节 SHA-256，以及读取契约字节 SHA-256。
- 核对前后源指纹记录内部一致，但不再打开其 `source_path`；保存 SQL 仅是重跑证据，不执行。
- W2-A 为本次实际读取的输入建立 manifest：每个固定文件的相对路径及工具计算的字节摘要。诊断与人工记录绑定这个 manifest，输入变化即失效。
- manifest 的初始摘要须由执行者在获批的本地运行中计算。本文不编造 manifest 数值，不假称已经建立独立可信哈希锚。
- 不宣称抵御画像、证据、摘要和验收文件被同一参与者协同篡改；继承 W1 本地受控信任边界。

### 3.3 后续新画像

若以后新增当前协议画像，必须有 `final-status.json=success`、匹配 run 和必需引用；pending、失败、缺终态均拒绝。本轮不因此授权生成新的生产画像。合成输入用 fixture 测试此分支，不能用测试通过冒充新生产证据。

## 4. 封闭问题与规则

### 4.1 问题输入

`QuestionSpec` 字段：

- `schema_version`、`question_id`、`question_version`。
- `intent`：`behaviour_record_counts`／`gmv`／`strict_funnel`。
- `requested_unit`：分别限制为 `raw_record`／`currency_amount`／`ordered_user_conversion`，不接受任意字符串单位。

不接受自动推断的自然语言业务问题、SQL、文件路径、任意规则或任意字段映射。缺问题输出 `needs_question`，不得按目录或现有字段伪造需求。未知 intent 输出 `unsupported_request`，不能默默退回记录计数。

### 4.2 规则内容（稳定 ID，版本 v1）

| 规则 | 检查及候选边界 | 证据 |
|---|---|---|
| `M-BEHAVIOUR-RECORDS` | 只允许原始记录按 behaviour 代码分类计数；需要该列与可引用工具结果；不承诺订单、支付、独立用户或转化率 | reading_schema、behaviours evidence/result、读取契约 |
| `P-GMV` | 检查金额字段与金额／订单口径缺口；当前缺金额依据，不支持 GMV，不用 buy 计数替代 | reading_schema；缺失语义明确为 unknown |
| `P-STRICT-FUNNEL` | 检查主体、顺序／时间语义、链路定义和事件含义；当前未确认；本轮方法集不提供严格漏斗 | reading_schema、timestamp 诊断及 limitations；未确认前提 |
| `Q-NULL` | 引用工具的列 NULL 观察，不计算新比例，不把 NULL 为零等同于无质量问题 | columns evidence/result |
| `Q-DUPLICATE-CANDIDATE` | 引用完整行重复候选，保留原数据；不自动删重、不解释业务重复合法性 | duplicates evidence/result |
| `Q-TIME-SEMANTICS` | 数值整数诊断与日期／时区／顺序语义分离，未确认保持 unknown | timestamp evidence/result、limitations |

质量规则只产生 observation；是否影响方法前提必须由明确的方法规则给出，不采用隐含分数或质量评分。候选可为空。

### 4.3 状态

- `request_state`：`valid`／`needs_question`／`unsupported_request`。
- 合法请求的 `capability`：`supported`／`conditional`／`unsupported`。
- 前提状态：`met`／`unmet`／`unknown`，同时给证据或缺口。
- `conditional` 表示存在本轮封闭方法，但至少一项必要前提待补充；不能进入合格候选。
- 缺必要字段或方法不在本轮集合，输出 `unsupported` 并区分 `missing_prerequisite` 与 `outside_method_scope`。
- 合格候选只来自已满足全部前提的方法 ID，不能把人工批准用于覆盖未知前提。
- 数据／证据校验错误属于操作失败，不包装成“业务不支持”的成功诊断。

## 5. 接口契约（已确认，未实现）

以下仅为签名与结构，不含实现。

```text
load_accepted_profile(profile_ref, acceptance_ref) -> ProfileSnapshot
diagnose(question: QuestionSpec, profile: ProfileSnapshot, rules: RuleSet) -> Diagnosis
record_s2_decision(diagnosis, decision, output_dir) -> DecisionReceipt
```

### ProfileSnapshot

`schema_version`、`dataset_version`、`profile_identity`（项目相对路径与嵌套 run_id，不能只用 production 字符串）、`read_contract_sha256`、`reading_schema`、`metric_refs`、`input_manifest`、`acceptance_basis`、`limitations`。

`acceptance_basis` 区分 `accepted_legacy_production` 与 `current_protocol_success`；fixture 单独标明，不伪装生产。

### RuleSet

`ruleset_id`、`ruleset_version`、工具计算的源码规则摘要、方法规则、前提规则、质量规则。规则固定于源码注册表，不提供 JSON 中自定义执行规则入口。

### Diagnosis

`schema_version`、`run_id`、`stage=S2`、`question_ref`／问题字节摘要、`dataset_version`、`input_manifest_ref`／摘要、`ruleset_id/version/hash`、`request_state`、`capability`、`prerequisite_checks`、`quality_observations`、`eligible_method_ids`、`gaps`、`human_decision_state=pending`、`limitations`。

每条 check／observation 带 `rule_id/version`、字段或工具证据引用。数值只使用工具结果引用或原值，不产生模型估计、新比例、评分或业务成效。

诊断计算完成时仍是 `computed_pending_finalization`；必需引用／环境／命令／网络观察完成后，由本阶段 `final-status.json` 表示运行成功。运行成功与人工受理分开。

### DecisionReceipt

`schema_version`、独立决定 run_id、`diagnosis_run_id`／诊断字节摘要、`dataset_version`、`input_manifest_sha256`、`question_version/hash`、`ruleset_version/hash`、`decision`、`actor`、`confirmed_at`、`acceptance_scope`。

- `decision`：`accept`／`request_data`／`reject`／`cancel`。
- `accept` 只能对合法且 supported 的诊断记录；conditional／unsupported 不得靠人工记录变成合格。
- 确认者与确认时间来自当次真实人工操作，不代签；缺失则拒绝记录批准。
- `acceptance_scope=S2_only`：不授权 S3 路径、指标口径、清洗、SQL、外发或模型请求。
- 决定保存在新 run，不修改已完成诊断。重启读取需重新核对全部绑定；旧决定不自动触发下一阶段。

## 6. 拟新增文件与演示入口

详细契约已确认；获得各批动作授权后，唯一执行者拟新增：

- `src/datainsight/feasibility.py`：标准库输入适配、诊断编排、独立 CLI 与证据收尾。
- `src/datainsight/feasibility_rules.py`：封闭规则与稳定版本。
- `configs/w2a-question-v1.json`：获批结构化描述性问题，不含源数据值或路径。
- `tests/test_w2a.py`：正常、反向及收尾／人工门测试。
- `tests/fixtures/w2a/`：受控合成画像包与问题，用途、文件清单和工具生成摘要记录在测试证据里。

不改 W1 源码、安装工具、原配置、冻结标准与旧证据；若实施发现必须改动既有文件，停止并提出精确冲突。

拟议入口为 `python -m datainsight.feasibility` 下的 `diagnose` 与 `decide` 子命令：前者使用固定生产输入及指定获批问题；后者引用已有成功诊断并显式输入决定。不存在当前可执行命令；执行者须在实现后提供实际可重跑命令，不把本稿当运行日志。

诊断 run 拟含 `diagnosis.json`、`input-manifest.json`、`reference-check.json`、`environment.json`、`network-observation.json`、`cli-command.json`、`final-status.json`；决定 run 拟含 `decision.json` 及同类必需收尾证据。仅原子发布必要 `.tmp` 可以在 run 中暂存。

## 7. 后续精确权限分组（均未授权）

下列是权限候选，不是本轮 P-DOC 的延伸。

| 权限 | 目的与范围 | 禁止／停止 |
|---|---|---|
| P-IMPL | 新增第 6 节列出的模块、问题配置和合成测试文件；只使用标准库 | 不改既有实现、不安装依赖、不生成整 W2；目标已存在或范围变化即停 |
| P-SYN | 以项目 `.venv/Scripts/python.exe` 离线运行本轮合成测试及必要 W1 回归；生成新 `outputs/W2-A/<run_id>/` 证据，实际临时路径为批准 D 盘目录 | 不运行历史安装脚本、W1 生产 profile/replay；失败不继续生产画像输入诊断 |
| P-LOCAL | 只读第 3.1 节固定历史画像包／本地验收来源、规则源码和问题配置；计算实际文件摘要并演示一次诊断，写新 W2-A run | 不打开原始 CSV、不新增 SQL、不扫描任意目录、不把合成证据冒充生产 |
| P-S2 | 展示成功诊断后由用户明确选择；在新 run 保存真实人工决定 | P-LOCAL 不包含默认 accept；缺确认／引用变化即停，不推进 S3 |
| P-RESULT-DOC | 运行后新建 `docs/acceptance/results/<run_id>.md` 并更新 INDEX 导航 | 不写回冻结标准、不改旧结果、不自行宣布最终通过 |

后续命令须由执行者逐批说明实际 argv、工作目录、输入输出、环境变量及停止条件并取得批准。本稿不授权任何命令。

环境约束：仅项目已有 venv；不重新安装 DuckDB，不启动引擎。TEMP／TMP／TMPDIR 指向项目 `.cache/tmp/`，禁止字节码散落；受控合成测试不接触未授权真实危险目标。Python 网络观察不宣称全系统隔离。

## 8. 冻结与下一步

详细验收见 `acceptance/W2-A-v1.md`，已依据用户“确认”记为 frozen；本文件第 3–6 节详细契约同步获确认。精确确认时间未提供，不用生成时间代替；接口、范围与 A01–A15 内容未变。

目录规约见 `decisions/ADR-003-directory-and-evidence-layout.md`，保持 accepted。此 ADR 不批准 W2-A 实现。

后续待用户决定：执行对话逐批提出并取得第 7 节动作权限。详细契约不再重复询问；保留已确认的领域、路径、DeepSeek 和 D 盘规则。

本轮 P-DOC-F 仅授权确认状态更新和 `handoffs/W2-A-sol61-low-v1.md` 自包含交接新建，不授权实现或运行。用户手动转交后，执行对话先只读核对，再请求当批动作权限。运行证据返回后，规划／验收对话再判定 W2-A，不凭本方案宣称通过。
