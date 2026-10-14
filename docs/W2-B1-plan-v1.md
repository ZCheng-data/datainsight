# W2-B1：确定性候选方案与 S3 口径审核方案 v1

- 状态：accepted；详细接口、固定口径草案及验收要求已获确认，执行动作仍未授权。
- 批准依据：用户先批准闭环方向及三份文档新建，随后回复“确认”确认详细接口、口径草案与 B101–B112；再回复“批准”授权 P-B1-DOC-F 状态落盘和 low 交接新建。
- 确认者：用户；精确确认时间：未提供，不以保存日期代替。
- 实现／运行／验收：未实现、未运行、未验收。
- 规划／验收：用户指定 sol6.1 high；执行由用户手动转交 sol6.1 low，不切换实际模型，不创建其他 Agent／Session。
- 项目根：`D:\MyPythonProjects\datainsight`。本文是含本机路径的本地契约，不是外部模型 payload。

## 1. 一个最小闭环

核验现有 S2 accept → 从封闭合格方法生成确定性候选方案及口径 → 人工选择并明确确认口径，或拒绝／取消 → 在新 run 保存独立 S3 记录。

候选生成与审核结束于 S3。不会重新统计、执行候选、读取生产 CSV、清洗、执行 SQL、调用模型或自动进入 S4。

### 本轮支持

- 当前唯一注册方法：`M-BEHAVIOUR-RECORDS`，原始记录按 behaviour 代码的固定桶分类计数。
- 使用 W2-A 已验收的合法诊断、accept receipt 和既有画像工具引用；生成方案，不复制业务结果为“新分析结果”。
- 候选数量由注册方法与前提决定，可为零；未知方法 ID 属于输入／注册表错误，不靠忽略它伪装成功。
- 人选择路径与确认口径，候选生成成功不表示人已批准。

### 非目标

DeepSeek 请求／SDK、外发 payload、计费账本实施、自由文本自动理解、任意方法／规则／SQL、GMV、比例、漏斗、日期分组、用户级分析、清洗、S4–S6、完整 W2 或庞大 Agent／安全框架。

W2 使用 DeepSeek 的已确认选择保持。W2-B1 是可复核离线基线；W2-B2 再独立规划有限模型组织／解释与真实调用门控，不默默换模型，也不把 W2-B1 通过冒充 LLM 能力。

## 2. 输入与复用接口

### 固定真实入口

- S2 receipt：`outputs/W2-A/s2-accept-3178ad8b677e49edb91de623be0c3905/decision.json`。
- 关联诊断：`outputs/W2-A/local-syn-3178ad8b677e49edb91de623be0c3905/diagnosis.json`。
- 阶段验收来源：`docs/acceptance/results/W2-A-final-review-v2.md`，W2-A 通过。
- 关联 manifest、终态、引用检查、固定历史画像包和问题／读取契约：只限现有 `verify_decision`／`load_diagnosis` 实际核验需要的文件集合，按 W2-A 已冻结路径边界读取。

实际开始前，执行者先给出可复核的具体读取清单；不得把保存路径或参数当成扩权。无需读取原始 CSV。历史画像版本只代表既有数据版本，不证明当前源 CSV 未变化。

### 已有接口核对

`src/datainsight/feasibility.py`：

- `verify_decision(path)`：核对决定终态、receipt、诊断重建、manifest 与版本绑定。
- `load_diagnosis(path)`：重新核对输入与当前规则，并复算确定性诊断，不运行画像 SQL。
- `decision_check`：允许 accept／request_data／reject／cancel；W2-B1 须另明确只接受 accept，不能将“记录本身有效”当“已受理”。

这些函数是已存在代码，但本规划轮没有调用；真实 receipt 的新进程核验须作为 W2-B1 执行证据，不假称已经完成。

W2-B1 复用现有标准库核验接口，不修改 W2-A。当前 W2-A 的 final-status、read_bytes 和输出函数有固定阶段边界；不得直接用其输出策略写 W2-B1。新阶段只实现自身最小输出／收尾，不借规划搭建通用框架。

### 入口门

- 成功且绑定有效的 accept，合法 supported 诊断，才构成 AcceptedContext。
- reject／cancel／request_data、缺终态、非零状态、篡改或输入／规则变化都停止。
- 真实入口固定上述 receipt；测试使用新受控 fixture／mock，并明确与真实证据分开。
- 用户“继续”“批准规划”不代替真实执行动作许可，也不作为新的 S3 业务确认。

## 3. 候选注册表与确定性生成

拟新增源码封闭注册表，metadata 含稳定 method_id、registry_version、方案／指标定义版本、字段／粒度前提、固定口径、输出 schema 与限制。

规则 ID 沿用 M-BEHAVIOUR-RECORDS，不改 W2-A 规则。方案注册表单独版本化并计算实际字节摘要；诊断规则身份与方案注册表身份分别保存。

生成时：

1. 校验 AcceptedContext 的来源、诊断与 receipt 绑定。
2. 校验 eligible_method_ids 均为封闭注册方法且前提 met；不允许人批准覆盖未知前提。
3. 按稳定 ID 顺序生成候选。当前单一方法不需要业务评分或虚构排序优先级。
4. 每项带证据、明确未满足条件、预期产出与限制。没有合格方法就空集合，不能凑够固定条数。
5. 候选中不生成业务数值、不重新计算已有数字；可引用历史 result 文件，不称已执行本轮分析。

空候选集合的逻辑可用受控上下文测试；不能伪造生产 accept 来演示空集合。输入里出现未知方法、错误结构或版本不一致应操作失败，不包装为成功空候选。

## 4. 唯一候选的指标口径草案

| 口径项 | 明确定义 |
|---|---|
| 事件含义 | 读取后的原始记录及 behaviour 代码；不证明代码对应真实订单或支付 |
| 主体／粒度 | 一条原始读取记录；非独立用户、订单、支付或会话 |
| 指标名称 | 行为代码固定桶的原始记录数 |
| 分子／计数对象 | 各固定桶内记录数；是计数定义，不是本轮计算值 |
| 分母 | not_applicable；不生成占比／转化率 |
| 统计窗口 | 绑定 dataset_version 的全文件范围；不是确认的日期覆盖 |
| 时间单位／时区 | unknown；本方法不用日期分组、时间排序或时间过滤 |
| 固定桶 | pv、fav、cart、buy、missing、other；不展开 other 原文 |
| 分类条件 | pv/fav/cart/buy 为读取后的精确文本匹配；missing 为 NULL；other 为非 NULL 且不在固定代码集 |
| 过滤 | 全局无记录排除；分类谓词不是删除数据或业务过滤 |
| 空值 | behaviour NULL 进入 missing，不填补；其他列空值不排除此项记录 |
| 重复策略 | 完整保留，按原始记录计数；重复候选不等于错误 |
| 大小写／文本 | 不 trim、不改大小写，保持 W1 已验收读取口径 |
| 维度／聚合 | 固定 behaviour 桶；COUNT 记录，不去重、不用金额、不按用户分组 |
| 派生／清洗 | raw_preserved_no_transformation，描述本方案不变换输入；不是 S3.5 清洗批准 |
| 预期输出 | 固定桶与记录计数的结构／名称；不在方案中填写新结果值 |
| 已有证据 | 诊断 reading_schema、behaviours evidence/result、W1 读取契约及封闭模板定义引用 |

分类口径已只读核对 `src/datainsight/profile_templates.py` 的 behaviours 模板；本轮未运行该模板。SQL／模板位置仅作本地依据，方案不接受或生成任意执行 SQL。

口径草案供 S3 人明确确认。批准此规划文档不等于用户已选择候选／确认当次 S3 口径。

## 5. 接口契约（已确认，未实现）

```text
load_s2_accept(decision_ref) -> AcceptedContext
build_candidate_plans(context, registry) -> PlanSet
record_s3_review(plan_set_ref, review, output_dir) -> S3Receipt
```

### AcceptedContext

schema_version、dataset_version、S2 receipt_ref/hash、diagnosis_ref/hash、question_version/hash、diagnostic_rules_id/version/hash、input_manifest_ref/hash、eligible_method_ids、prerequisite_checks、evidence_refs、acceptance_basis、limitations。

只承载已核验上下文，不含原始行、标识值或源读取权限。文件摘要由实际工具计算。复核时以保存 manifest 重新校验，不把初次摘要冒充协同篡改抵抗。

### PlanSet

schema_version、run_id、stage=S3、status=computed_pending_finalization、accepted_context_ref/hash、dataset_version、question_identity、diagnostic_rules_identity、registry_id/version/hash、plan_set_version、candidates、human_review_state=pending、limitations。

每项候选：plan_id/version、method_id、rule_version、question_ref、required/optional_fields、grain、prerequisites、satisfied_evidence、unmet_conditions、metric_definition/version/hash、expected_output_schema、assumptions、risks、limitations。

- 候选语义内容与口径采用规范序列化／实际工具摘要；同输入稳定，run_id／时间可变。
- 不带统计结果值。候选生成的运行成功不改变 human_review_state。
- 固定窗口／空值／重复等元数据是方法定义，不是数据发现；数据声明仍绑定原工具引用。

### ReviewSpec 与 S3Receipt

ReviewSpec：decision=approve／reject／cancel、selected_plan_id/version、metric_definition_hash、confirm_metric_definition、actor、confirmed_at。

- approve 必须精确选择集合内候选且 confirm_metric_definition=true，指标摘要匹配；选项与确认缺任一则不保存批准。
- reject／cancel 不需要候选选择，也不得附伪造选择；明确停止。
- 不支持在审核输入中自由改写指标定义。若要变更口径／方案，提出新版本、影响与批准，再生成新候选；不能边审核边悄改当前标准。
- actor／时间来自真实确认／操作，缺失不代签；同本地信任模型，不声称用户身份认证系统。

S3Receipt：schema_version、独立 review run_id、plan_set_ref/hash、selected_plan_id/version、metric_definition_version/hash、dataset_version、S2／诊断／问题／规则／registry／manifest 绑定、decision、actor、confirmed_at、acceptance_scope=S3_plan_and_metric_only。

保存到新 run，不回写 PlanSet、S2 或旧证据。数据、问题、规则、registry、候选或口径改变则批准失效；重启重新核对，不默认 approve。

`S3_plan_and_metric_only` 不包含 S3.5、S4、查询、清洗或外发权限。不变换原始数据的说明不能自动变成清洗审核记录。

## 6. 拟新增文件与证据

后续获实现权限才新建：

- `src/datainsight/planning.py`：固定入口核验、方案生成／审核 CLI、版本恢复与本阶段收尾。
- `src/datainsight/planning_methods.py`：封闭候选／口径 metadata 与版本。
- `tests/test_w2b1.py`：正常、独立反向、门控／版本／隐私／收尾测试与必要证据生成。

真实 S3 审核配置不预填 approve，不新建“默认用户批准”。受控输入在测试获批后生成到 `outputs/_scratch/<批次>/<用例>/`；先明确包内容与命名，不新增根目录 runner。

拟议独立入口：`python -m datainsight.planning`，子命令 candidates／review。不是当前可执行命令；实现前核对签名，实现后列真实 argv 请求运行许可。

正式输出新建 `outputs/W2-B1/<run_id>/`，不覆盖旧 run。

候选 run 至少含：candidate-plans.json、accepted-context.json、input-manifest.json、reference-check.json、environment.json、network-observation.json、cli-command.json、final-status.json。

审核 run 至少含：s3-review.json、绑定引用／manifest 核验、environment.json、network-observation.json、cli-command.json、final-status.json。候选与审核 run 分开；未收尾计算产物不能当运行成功；必须引用／环境／网络观察／命令证据齐全后才发布 success。

一般临时文件只在 outputs/_scratch 或 .cache/tmp；原子发布 .tmp 必须在目标 run 同目录，是 ADR-003 必要例外，失败残留保留，不迁移／清理。

## 7. 后续权限分组（均未授权）

| 权限 | 拟请求目的与范围 | 必须停止的情况 |
|---|---|---|
| P-B1-IMPL | 仅新增第 6 节两个模块与一个测试文件；标准库，不修改 W1/W2-A | 目标已存在、需要改既有实现或增加其他文件时先报告 |
| P-B1-SYN | 项目 venv 离线运行新合成用例与明确必要的受控接口回归；生成新 scratch／W2-B1 证据 | 不 discover W1/W2-A 全套；不自动清理、安装或生产计算；失败不继续真实入口 |
| P-B1-LOCAL | 对固定真实 S2 receipt 重新核验并生成一次候选 run，仅读必要画像证据，不读 CSV | reject/cancel、绑定变化、校验失败即停止；不新建真实 S2 accept |
| P-B1-S3 | 展示成功候选与口径后用户实际选择并确认，再保存新审核 run | 不使用规划批准代替业务选择；缺确认／引用变化停止，不自动 S4 |
| P-B1-RESULT-DOC | 新建 docs/acceptance/results/<run_id>.md 并更新 INDEX 导航 | 不回写冻结标准、旧结果或旧证据，不自行最终验收 |

每批动作前说明精确输入／写入、argv、cwd、环境变量与停止条件。已有 D 盘解释器／缓存规则保留，实际路径要核对；不安装、不联网、不开外部 API。旧阶段授权不复用。

## 8. 冻结与下一步

验收标准见 `acceptance/W2-B1-v1.md`，已依据用户“确认”标为 frozen；接口、固定口径草案与 B101–B112 内容未变。精确确认时间未提供，不以保存日期代替。ADR-004 保留其原文与批准方向，不据此扩大执行权限或代替实际 S3 决定。

当前详细契约不再重复询问；固定口径草案的技术确认不等于用户选择当次候选或作出 S3 审核。执行对话仍逐批获取第 7 节权限。领域／路径／DeepSeek／D 盘约定不重问。

本轮 P-B1-DOC-F 仅授权本方案／标准确认状态更新和 `handoffs/W2-B1-sol61-low-v1.md` 新建。用户手动转交后先只读核对，再提出当批动作请求；真实运行证据返回后才验收，不一次性交付整个 W2。
