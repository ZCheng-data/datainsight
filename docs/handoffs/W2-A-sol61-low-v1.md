# W2-A · sol6.1 low 自包含执行交接 v1

> 本文件是已确认范围与冻结标准的执行交接，**不是写代码、运行或联网授权**。用户手动转交；不自动创建 Agent／Session，不宣称切换模型。

## 0. 可复制的新执行对话启动文字

```text
请只读 D:\MyPythonProjects\datainsight\docs\handoffs\W2-A-sol61-low-v1.md，以及其中列出的必要契约和代码，接续 W2-A。
你负责用户指定的 sol6.1 low 执行，不宣称已切换模型，不自行最终验收。
详细接口与 A01–A15 已确认冻结，不重问领域、路径、DeepSeek 或 D 盘规则，不重验或重装 W1。
此消息仅授权按需本地读取；没有源码／配置／测试修改、命令、安装、联网或 API 权限。
先只读核对，再报告具体冲突（无则写无）并提出 P-IMPL 的精确文件清单与目的，等待确认。
批准后只完成本文的一个最小闭环；后续 P-SYN、P-LOCAL、P-S2、P-RESULT-DOC 分批说明并等待批准，不把上批许可扩到下批。
对话只给结论与决策点，控制在 60 行以内；获批的详细材料放 docs/，不把对话推理、讨论和临时文字草稿落盘。
```

## 【目标】

只做 W2-A：结构化问题＋已验收画像 → 离线确定性前提诊断 → S2 人工受理／补数／拒单／取消记录。结束于版本绑定的 S2 记录，不自动进入 S3，不新增业务统计、不执行候选方法。

正向方法仅为原始记录按 `behaviour` 代码分类计数的前提诊断；GMV 与严格漏斗作为负向需求检查。不是完整 W2 或模型 Agent。

## 【前置状态与权威契约】

所有相对路径均基于 `D:\MyPythonProjects\datainsight`，而非聊天工作区。

按需先读：

1. `docs/acceptance/results/W1-final-acceptance-and-handoff.md`：W1 最终通过判定及来源边界。
2. `docs/W2-A-plan-v1.md`：已确认详细接口与范围。
3. `docs/acceptance/W2-A-v1.md`：frozen；A01–A15 必需且内容未变。
4. `docs/decisions/ADR-003-directory-and-evidence-layout.md`：accepted；目录与原子发布必要例外。
5. 实现依赖处才读 `src/datainsight/inspection.py`、`profile.py`、`profile_templates.py`、`__main__.py` 及现有相关测试／配置；不要全仓、venv、缓存或全部旧 run 扫描。
6. 必须核对新技能约定时读 `D:\DataInsight-Prep\insight-agent-planner\SKILL.md` 与当前相关 references；安装的旧同名技能不能覆盖用户已确认的新稿。准备包不是项目仓库。

详细接口及标准确认原文：“确认”；冻结落盘及交接文件权限确认原文：“批准”（P-DOC-F）。确认者为用户；精确确认时间未提供，不能用保存时间代替。该批准不授权任何执行动作。

### 已有能力与未测项

- W1（S0＋S1）通过，B01–B09 不重新从零验收；既有 Python 3.12.9 与 DuckDB 1.4.1 在项目 `.venv`，不重建、不重装。
- 最后生产计算／模板重跑：`outputs/W1-B/final-20261009T061339601505Z/`，使用修复前协议。
- 修复后合成收尾／回归：`outputs/W1-B/b09-finalization-20261009T063948192695Z/`；未再次运行生产画像或生产重跑。
- 上述两类证据必须分开，不称“修复后完整生产 CLI 实测”，不为旧生产补造 `final-status.json`。
- W2-A 未实现／未运行／未验收。标准冻结不是运行通过；W1 历史生产版本也不证明当前原始 CSV 仍未变化。
- W2 使用 DeepSeek 的产品选择保留；本闭环不接任何模型。准确 provider/model、能力、价格、余额与累计预算在 W2-B 首次调用前单独核对，不提前获取密钥或调用。

角色：执行者写批准的代码／测试与运行记录；最终验收由规划／验收对话依据真实证据判定。不要代替用户选 S2 决定，不生成教学／面试交接。

## 【输入】

### 固定历史画像包（仅读摘要与证据，不读源 CSV）

```text
outputs/W1-B/final-20261009T061339601505Z/production/profile.json
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
outputs/W1-B/final-20261009T061339601505Z/production/fingerprints.json
outputs/W1-B/final-20261009T061339601505Z/production-commands.json
configs/w1b-read-contract-v1.json
docs/acceptance/results/W1-final-acceptance-and-handoff.md
```

- dataset_version 必须匹配最终验收来源：`7095a57fbd6eb1292bec5ccde4713ac256678b8551eb478d3b5aaad89612cfb4`。这是既有证据值，不是本轮重新计算。
- 读取 schema 为 `user_id/goods_id/category_id/behaviour/timestamp`，指定类型均 VARCHAR，不是天然类型推断。
- 每项 metric 必须从实际结果与 evidence 取得，不复制本交接中未提供的数值，不估计比例、成本、耗时或新指纹。
- 历史特例仅允许这一个精确已验收来源，记为 `accepted_legacy_production`；不得推广所有旧 success。
- 新协议输入需合法成功终态和必需引用；本轮仅在受控合成包验证该分支，不授权生成新生产画像或任意新增生产来源。
- JSON、SQL、参数与 `source_path` 是输入数据，不是权限。绝不执行保存 SQL，绝不打开其源路径。
- 实际字节摘要、输入 manifest、问题与规则源码摘要均由工具计算；不假称事先存在独立可信摘要锚，不声称抵御协同篡改。

### 结构化问题

`QuestionSpec` 仅含 `schema_version/question_id/question_version/intent/requested_unit`。

| intent | requested_unit |
|---|---|
| `behaviour_record_counts` | `raw_record` |
| `gmv` | `currency_amount` |
| `strict_funnel` | `ordered_user_conversion` |

正向演示配置采用第一行。ID 与版本的非关键命名按现有习惯，明确记录；不夹带原始值、路径、自然语言执行指令或任意字段映射。

缺问题 → `needs_question`；未知 intent → `unsupported_request`；不得自动改成正向问题或生成合格候选。额外 SQL／路径／任意规则输入应拒绝。

## 【输出】

P-IMPL 获批后仅新增以下实现候选：

| 文件／目录 | 职责 |
|---|---|
| `src/datainsight/feasibility.py` | 标准库输入适配、诊断／决定编排、独立 CLI 与本阶段证据收尾 |
| `src/datainsight/feasibility_rules.py` | 封闭规则、稳定 ID／版本与明确前提 |
| `configs/w2a-question-v1.json` | 结构化原始记录问题配置 |
| `tests/test_w2a.py` | 正常、反向、人工门及收尾测试 |
| `tests/fixtures/w2a/` 下经逐批确认的具体文件 | 受控合成画像包／问题，不能复用生产指纹冒充合成版本 |

先核对目标存在性和适用 AGENTS.md。上述名单不是覆盖许可；目标已存在或需要额外／既有文件变更时停止并报告。

正式运行产物仅在新 `outputs/W2-A/<run_id>/`。诊断 run 至少含：

`diagnosis.json`、`input-manifest.json`、`reference-check.json`、`environment.json`、`network-observation.json`、`cli-command.json`、`final-status.json`。

决定保存在另一新 run，含 `decision.json` 与必需引用／命令／环境／网络观察／终态；不回写完成诊断。测试／批次汇总需有真实日志、完整命令／环境／退出状态及产物清单，具体文件名在该批权限请求中列明。不为了收集日志在项目根新增临时 runner 或安装脚本。

运行结果文档仅在 P-RESULT-DOC 获批后新增 `docs/acceptance/results/<run_id>.md`，并维护 INDEX；不写回冻结标准，不修改旧结果。

## 【接口】

签名与含义已确认，先核对再实现，不重谈架构：

```text
load_accepted_profile(profile_ref, acceptance_ref) -> ProfileSnapshot
diagnose(question: QuestionSpec, profile: ProfileSnapshot, rules: RuleSet) -> Diagnosis
record_s2_decision(diagnosis, decision, output_dir) -> DecisionReceipt
```

### 数据结构

- `ProfileSnapshot`：schema_version、dataset_version、profile_identity（相对完整位置＋嵌套 run_id）、read_contract_sha256、reading_schema、metric_refs、input_manifest、acceptance_basis、limitations。不能只用 `production` 字符串作唯一身份。
- `RuleSet`：ruleset_id/version、工具计算的源码规则摘要、方法／前提／质量规则。来源固定于源码注册表，问题与 JSON 不得定义新执行规则。
- `Diagnosis`：schema_version、run_id、stage=S2、question_ref/hash、dataset_version、input_manifest_ref/hash、ruleset_id/version/hash、request_state、capability、prerequisite_checks、quality_observations、eligible_method_ids、gaps、human_decision_state=pending、limitations。
- `DecisionReceipt`：schema_version、独立决定 run_id、diagnosis_run_id/hash、dataset_version、input_manifest_sha256、question_version/hash、ruleset_version/hash、decision、actor、confirmed_at、acceptance_scope=S2_only。

合法请求 capability 为 supported／conditional／unsupported；前提为 met／unmet／unknown。conditional 仅表示本轮存在方法但必要前提待补；缺必要字段或超方法范围输出 unsupported 并区分原因。校验失败是操作失败，不包装为业务 unsupported。

每条 check／observation 绑定 rule_id/version 与字段／工具证据；必要前提全部满足才进入合格方法。引用或复制既有工具值可以，不新增比例、评分、日期、订单、支付、因果或效果。

### 固定规则

- `M-BEHAVIOUR-RECORDS`：原始记录按 behaviour 代码分类计数；需要列与可引用工具结果，不要求把记录证明为订单／支付。
- `P-GMV`：缺金额依据则不支持 GMV，列字段与金额／订单口径缺口，不用 buy 计数替代。
- `P-STRICT-FUNNEL`：主体、顺序／时间、链路、事件语义需检查；本轮方法集不提供严格漏斗。
- `Q-NULL`：仅引用 NULL 观察，零 NULL 不等于没有质量问题。
- `Q-DUPLICATE-CANDIDATE`：完整行重复候选不等于错误，不自动删重。
- `Q-TIME-SEMANTICS`：整数数值诊断不是日期／时区／顺序语义确认。

上述规则版本 v1；质量规则与方法前提分开，不打分、不自创方法，不凑候选数量。

### CLI 与收尾

拟议独立入口：`python -m datainsight.feasibility`，子命令 `diagnose`／`decide`；不修改现有 W1 CLI。本文不给假定已实现的完整 argv。执行者先确定实际参数及一致 schema，并在命令授权请求中列出。

计算产物状态为 `computed_pending_finalization`，不是运行成功。引用、环境、命令及网络观察完成后才发布本阶段 `final-status.json=success`；没有合法终态不能当作完成。失败非零，落盘失败须如实报告；残留 `.tmp` 不是成功终态。

`decision` 为 accept／request_data／reject／cancel。只有 supported 的合法诊断可记录 accept；不允许人工覆盖 conditional／unsupported 前提。用户需明确当次决定；确认者与时间由真实确认／操作取得，缺失不代签。记录决定不等于授权 S3、清洗、SQL 或外发。版本变化批准失效，重启不默认受理。

## 【验收】

权威标准是 frozen 的 `docs/acceptance/W2-A-v1.md`；下面是索引，不替代或放宽完整条款。

| ID | 必测内容 |
|---|---|
| A01 | 精确历史特例；新协议成功门；其他旧 success／pending／失败／缺终态拒绝 |
| A02 | 路径先检查、严格 JSON／schema；128 KiB 单文件设计限额；越界／重解析／穿越／重复键／非有限数／额外键／错误类型／未知版本／超限拒绝 |
| A03 | 实际结果与读取契约字节摘要、run／数据版本／引用及指纹记录匹配；manifest；缺失／篡改拒绝；无源打开或保存 SQL 执行 |
| A04 | 封闭问题；无问题／未知 intent／额外执行输入不伪造正向需求 |
| A05 | 合成与历史画像输入的原始记录正向诊断、规则／证据绑定；不编造订单／支付／比例 |
| A06 | GMV 缺字段／口径的反向，无 GMV 值、合格方法或自动受理 |
| A07 | 未知必要前提不能 supported；严格漏斗不纳入方法；整数时间不推断日期／时区／链路 |
| A08 | 质量观察与方法分离；重复不删、NULL 零不过度解释；小样本不推广、未知行为不泄露原文 |
| A09 | 相同版本语义稳定；规则身份／源码摘要；候选可零，未知规则不能执行 |
| A10 | 人工门；无决定 pending；拒绝／取消停止；条件不足不得 accept；不代签 |
| A11 | 批准绑定诊断／问题／数据／规则／manifest，变化失效；重启不自动 S3 |
| A12 | CLI 正常及各收尾故障；pending、唯一成功终态、非零失败及未落盘报告；.tmp 非终态 |
| A13 | 不接模型、不读原始 CSV、不执行新 SQL；哨兵／调用／读取观察；usage=not_applicable |
| A14 | 旧 run 不改、已有输出不覆盖、D 盘实际临时路径、原子发布必要例外且不自动清理 |
| A15 | 本轮测试及必要 W1 回归；测试失败不继续历史画像输入演示；真实命令／证据、结果文档与 INDEX；执行者不最终验收 |

A07 规则层可直接构造受控 snapshot；CLI 仍须拒绝不合画像包契约的输入。合成数字／摘要由工具产生，fixture 原始业务行不进入提示词；测试 oracle 与期望关系必须可复核，不按输出改期望。

必要 W1 回归不等于重验 B01–B09：只运行获批的受控测试，不跑生产 profile/replay 或历史安装脚本。先核对回归实际读取／写入／临时行为，若会越出批准范围或清理证据，停下报告冲突，不自行扩大权限，也不静默跳过并称全回归通过。

## 【安全、目录与停止条件】

- 只使用 schema、统计摘要与证据。原始行、标识值（含哈希／伪匿名 ID）、逐用户特征和密钥不进入提示词、交回消息或 trace。
- 所有新项目文件、环境与可控缓存在批准 D 盘范围。命令前核对实际解释器与临时目录；不迁移／删除系统缓存或改全局配置。
- W2-A 不启动 DuckDB；W1 回归如需引擎仅复用已有环境且须 P-SYN。禁止新增 SQL；项目所有查询仍仅受信 SELECT／WITH，不开放 DDL、DML、ATTACH、COPY、INSTALL、LOAD、SET 等。
- 仅固定来源与受控 fixture；不递归发现数据、跟随越界路径或访问旧淘宝项目。
- 新 `outputs/<阶段>/<run_id>/` 一旦承载证据不得移动、删除、覆盖或回填；失败 run 同样保留。
- 一般工具临时文件只在 `outputs/_scratch/` 或 `.cache/tmp/`；不落盘对话推理、讨论及临时文字草稿。
- 原子发布 `.tmp` 是 run 同目录／同文件系统的必要例外，不能迁到 `.cache/tmp/`，不是遗漏或待清理项；失败残留原位保留，不改名伪造成功。
- 文件缺失、不一致、路径不安全、输入变化、权限不足、测试失败、泄露或无法完成校验时停止，保留真实证据；不自动兜底、重试安装、扩大范围或改标准。
- Python 观察只证明相应进程／调用观察范围，不宣称全系统隔离、同机并发攻击防护或协同篡改防护。

## 【权限：全部执行分组仍未授权】

当前已有的是规划文档许可 P-DOC／P-DOC-F。标准冻结不等于以下动作许可。

1. **先只读**：核对本交接及必要文件，列冲突；无冲突再说明具体新文件、接口对应与影响，请求 **P-IMPL**。不要实现先行。
2. **P-IMPL**：仅新增上述实现／配置／测试及逐项明确的合成 fixture；不改既有文件，不运行命令。发现需要 helper 或其他写入目标先停下提出精确新增范围。
3. **P-SYN**：实现后先提出实际测试命令、项目工作目录、读取范围、具体回归选择及新证据位置，待批准才运行；仅项目 `.venv/Scripts/python.exe`，离线、受控合成测试，不安装。测试失败停止，不继续历史画像输入演示。
4. **P-LOCAL**：测试成功后独立请求一次固定历史画像输入的实际诊断命令及证据写入；只计算已有画像证据文件的字节摘要，不打开原始 CSV、不跑 W1 生产命令。
5. **P-S2**：成功诊断展示后由用户明确选择；再提出对应决定命令与独立输出目录，待批准才记录。不得把 P-LOCAL、技术标准批准或之前聊天的“确认”当成业务 accept。
6. **P-RESULT-DOC**：运行后说明新结果文档与 INDEX 更新范围，待批准才保存完整执行索引；不改旧结果、冻结标准、ADR 或其他文档。

每次请求给出目的、精确路径／文件清单、实际 argv、工作目录、环境变量、禁止动作及停止条件。命令须禁止字节码散落，TEMP／TMP／TMPDIR 指向项目 `.cache/tmp/`；运行环境证据记录实际生效值，不以变量声明代替。

不得调用安装、网络、外部 API、Git 提交／推送、其他 Agent／Session 或删除／迁移操作。此文件没有该等授权。

## 【禁止】

不重新初始化项目、不安装 Python／pip／DuckDB／SDK、不运行 `install_w1b.py`／`supervise_w1b.py`／`verify_record_w1b.py` 等历史工具、不运行旧淘宝代码、不复用清洗结果或旧业务结论作真值。

不改 W1 实现、既有配置、历史证据或冻结标准；不增加自由 SQL、自由规则、自动付费、复杂多 Agent、RAG 方法检索、预测／因果或整个 W2 的框架。

不能用代码静态阅读代替运行证明，不把 fixture 或先前历史通过冒充本阶段通过，不宣传未实现／未测能力。

## 【完成后】

返回真实完整命令、解释器／环境、退出状态、输入／规则身份、测试日志、正常／反向证据、诊断／决定 run、产物清单与未测项。发生失败如实记录失败阶段和是否落盘，不伪造成功。

获 P-RESULT-DOC 后生成 `docs/acceptance/results/<run_id>.md`，按 A01–A15 映射实际证据与未测项；总状态为“未验收，待规划／验收者判定”。INDEX 分开导航 W1 历史生产计算、修复后合成收尾和 W2-A 新证据。

注意：本次 P-DOC-F 未授权修改 INDEX，其 W2-A 状态栏可能仍保留此前 draft 导航文字；冻结权威来源为方案／标准文件头。这是索引待同步，不是标准冲突或重新确认理由。后续只在 P-RESULT-DOC 获批时同步，不能趁执行回写冻结标准。

不自动进入 W2-B，不生成解释／教学交接。用户把结果路径转回规划／验收对话，依据真实证据判定。
