# W2-B2：一次有界 DeepSeek 方案解释闭环 v1

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

- 文档状态：accepted；详细契约、payload白名单、调用／预算门与验收安排已获用户确认，执行动作仍未授权。
- 前置：W2-B1 通过，见 `acceptance/results/W2-B1-final-review-v2.md`。
- 本阶段：未实现、未运行、未验收。离线测试／真实 API 能力均未证明。
- confirmation_actor：用户；confirmation_basis：用户先确认闭环及三份文档新建，随后回复“确认”确认详细接口、payload白名单、调用／预算门与C201–C212验收安排；再回复“批准”授权P-B2-DOC-F状态落盘与low交接新建。
- confirmed_at：not_provided；recorded_at：null；recorded_at_source：not_available；recorded_at_status：unavailable。
- recorded_at_reason：本轮文件工具未返回精确记录时间，不执行未授权取时命令，不估算或借用历史运行时间。
- authorization_scope：此前仅新建三份规划文档；本轮P-B2-DOC-F仅追加本方案／标准确认状态更新与`handoffs/W2-B2-sol61-low-v1.md`新建。没有实现、运行、联网、密钥读取或付费请求权限。
- 项目根：`D:\MyPythonProjects\datainsight`。本文件含本地路径，只在本地使用，不作为请求 payload。
- 角色：规划／验收为用户指定 sol6.1 high，执行由用户手动转交 sol6.1 low，不切换实际模型或自动创建其他 Agent／Session。

## 1. 一个最小闭环与非目标

重新核验已批准方案 → 编译并展示完整脱敏请求 → 人批准本次外发及明确预算 → 工具预留累计额度 → 单次 DeepSeek 请求 → 严格响应／引用校验与实际 usage／费用核算 → 本地解释草稿与新运行证据。

先离线 mock 验证契约／门控／失败路径；只有独立核对并获批才能运行真实请求。一次请求，无自动重试、自动修复请求或能力探测调用。草稿只解释现有方案，不改变方法、候选、指标或 S3 决定，不执行 SQL，不自动推进 S4。

不在本闭环做：模型工具调用、模型 SQL、联网检索、自由规则／新方法、GMV／漏斗／日期统计、业务建议自动批准、清洗、完整 Agent 框架、流式输出、多 provider、复杂并发账本或自动报告外发。

W2 使用 DeepSeek 不重问。20–30 元是既有充值计划，不是实际余额、请求额度或费用预测。产品 provider/model 必须显式配置，不能由聊天客户端当前模型接管。

## 2. 固定本地输入与已有接口

- S3 记录：`outputs/W2-B1/w2b1-review-219e79901d08444bab62c6e61f6e2211/s3-review.json`。
- 候选：`outputs/W2-B1/w2b1-candidates-1f9fa1e612fa4c19b48181111a3a35d6/candidate-plans.json`。
- 当前验收来源：`docs/acceptance/results/W2-B1-final-review-v2.md`。
- 其余本地文件只限现有 `planning.verify_review`／`load_plan_set`／W2-A 核验链必要的 manifest、终态、引用检查、规则、问题、读取契约、历史画像及模板。

执行者在真实本地准备前列精确读取清单。`verify_review` 也能核验 reject／cancel；W2-B2 wrapper 须另要求 decision=approve、confirm_metric_definition=true、集合内候选及口径摘要匹配。

入口调用是后续执行动作，本规划轮只读接口，未运行它。任何上游绑定变化停止；不得自动重做 S2/S3 决定或更新旧证据。不读取源 CSV、不运行保存 SQL，不重新计算业务统计。

上游 receipt 的历史 confirmed_at 已说明为工具操作时间；按 ADR-005 原位保留，不能用它作为新外发确认时间。本阶段新授权记录独立使用 confirmed_at 与 recorded_at。

## 3. 首次 payload：最小必要白名单

### 3.1 允许内容

首次请求只使用下列宿主编译的结构，不将整个 candidate、context、receipt、evidence 或验收 Markdown 传入模型：

- 固定任务说明：解释这一已批准记录计数方案，列前提与边界；不推荐或计算新方法／指标。
- 必需 schema：behaviour／VARCHAR。省略 user_id、goods_id、category_id、timestamp 等本轮解释不需要的字段。
- 固定方法与口径：原始读取记录粒度、六个固定桶定义、全文件版本窗口、无分母、时间语义 unknown、不筛／不删重／不转换文本；由白名单模板组织，不复制输入自由文本。
- 必要聚合摘要：仅既有 summary 工具返回的 row_count，通过本地证据核验后引用。若准备过程中判断该摘要并非必要或不允许外发，先呈现改动并重新批准 payload，不静默换包。
- 外发引用别名：本轮局部 alias，如 p_selected／schema_behaviour／metric_records／stat_row_count，映射只留本地。不外发本机路径、run_id、数据内容哈希、源 SQL／参数、已保存批准原文。
- 明确限制：未知业务事件语义、未知日期覆盖、方案不是订单／支付／GMV／漏斗结果，当前源 CSV 未再次校验。

不发送用户／商品／类别标识值及其哈希／伪匿名值、逐用户分组、自由文本样例、低频枚举或具体小组统计。首次摘要无按标识分组，不发送行为桶实际计数、时间极值或用户基数；因此没有为本轮新设低频分组阈值的必要。六个固定代码是已批准方法定义，不是从源数据提取的未知枚举。

### 3.2 完整请求审核，而非只审 user message

PayloadDraft 保存完整待发送 JSON body 的规范字节／摘要，覆盖系统消息、用户消息、响应 schema、模型名、采样／输出限制及所有发送字段。请求 envelope 的 endpoint、方法与非敏感头单独展示；密钥／Authorization 值只在调用时装配，不保存、不回显。

完整 body 各层按白名单检查、固定 schema／引用类型检查、敏感哨兵／路径及自由文本注入反向；白名单构造是主防线，字符串扫描不能宣称万能匿名化。错误／trace 同样不能携带密钥或被禁止内容。

请求 body、endpoint/model、policy／费率／预算身份和上游口径全部绑定到本次外发批准。任何变更重新确认；本地路径映射与权限记录不进入请求。

## 4. 首次真实调用的未知项与停止门

现有 `configs/` 没有 W2-B2 provider/model 或预算配置。准确 endpoint、API model ID、结构化能力、密钥来源、价格、余额与限额当前均记待核对，不能默认猜测。

真实请求前必须独立完成并保存非敏感核对结果：

| 项目 | 必需证据／停止条件 |
|---|---|
| provider／endpoint／model | 用户批准的明确 DeepSeek 服务、HTTPS endpoint、精确 model ID；与官方能力／调用文档相符；未知或配置隐式继承则停止 |
| 响应能力 | 可用非流式响应、结构化模式及本地严格校验路径；不能把文档支持当实际成功；不默默换模型，缺能力保持基线 |
| 密钥来源 | 批准的进程环境变量名或专用凭据来源；不要求用户贴密钥、不读取全环境、不落盘值；无凭据停止 |
| 价格／余额 | 有版本／来源／获取时间的费率与用户确认的实际余额依据；币种／计费单位明确；不估计已充值或可用资金 |
| token 上界 | 能用已验证的模型相容计数工具或官方保证的可靠上界覆盖完整输入；输出上限能强制限制，并覆盖该 model 的全部计费输出类别 |
| 累计限额 | 请求数、输入／输出 token、费用上限、账本范围与有效期由人明确确认；额度覆盖本请求的最高费用，不以余额或充值计划代替 |
| 外发与请求许可 | 审核完整 body／目标／费用预留及当批动作后明确批准；S3 approve／文档批准不包含外发 |

不能用字符数猜 token，不能把 `max_tokens` 直接当所有模型全部计费输出上界；如果模型另计推理 token，必须明确其计费与可控边界，否则不发请求。不为取计数引入未授权第三方计数服务或 paid probe；新增计数依赖需要独立安装／D 盘权限。

文档核对、余额页面访问或 provider 查询均是独立联网动作。本轮没有授权它们；未来执行者逐项列目的、数据与费用，不能为了“准备”先联网或试请求。

### 单请求设计默认

下列设计约束已确认冻结，不是实测：每次明确调用授权最多一项生成请求；自动重试=0；非流式；总请求超时上限 60 秒；响应体上限 64 KiB；重定向=拒绝。若实际服务与这些控制不相容，提出具体冲突，不自行放宽。

累计请求／token／金额上限不填数值占位。方案结构可以先冻结；真实限额、费率与 model 需在首请求前另以批准配置冻结，未填就拒绝付费入口。超时后取消本地等待不代表服务未处理或未计费。

## 5. 最小持久账本与费用协议

### 5.1 一个已批准预算 scope

建议唯一预算 scope 为 W2-B2 首次验证用途，精确 scope_id 后续配置获批。不能换 run／配置名或重新建 scope 把累计计数归零。拒绝未经批准的替代 scope。

账本根：`outputs/W2-B2/budget-<批准scope_id>/`。它是本阶段明确批准的追加式预算证据 run，不存可随意清除的缓存。事件文件一次写入、不覆盖；追加事件不改变既有文件。与其他 run 一样不得移动／删除。仅其自身发布必须的同目录 `.tmp` 适用 ADR-003 例外。

事件名建议 `event-<单调序号>-<事件类型>.json`，记录 policy 身份、request_id、引用与实际工具结果；类型 reservation／attempt_started／settlement／unknown_charge／reconciliation。事件内容与所需摘要由工具计算，budget policy 的初始批准摘要是本地锚，不发送。

### 5.2 发送前事务顺序

1. 核验上游、实际 payload、外发批准、policy／price／balance 与完整账本；读取缺件、损坏／冲突或残留未发布事件就停止，不将其当零。
2. 同一 scope 同时只允许一个调用；执行期明确单写者。实现最小排他机制并用受控测试证明并发请求不会双重预留，不建设多用户平台。锁状态只在批准 D 盘工具状态位置，不自动清理故障锁。
3. 工具根据输入上界、输出上限与最高适用费率计算最高预留费用，不假定 cache-hit 折扣。费用使用十进制／明确最小计费单位，避免浮点少预留；若按预留上界舍入须向上且记规则。
4. 预算覆盖失败／超时，请求计数至少包含每次尝试，任何取不到计费的尝试保留风险额度。
5. reservation 和 attempt_started 事件持久化并确认成功后才准发送。不能先发请求后补账；崩溃窗口中的未结算预留继续占额，恢复时不能自动重发。

### 5.3 响应后结算

- HTTP 成功仍需响应、结构、引用、usage 和价格核验。provider 返回的真实输入／输出／cache／reasoning 等计费分类与实际 model 对齐；不得按文字长度伪造。
- 费用仅由工具对实际 usage 和有版本费率计算；明确“按 provider usage 计算的成本”，没有账单对照不称已核验扣款。
- 实际费用超过预留、usage 不相容／缺失、超时、连接中断或服务错误计费未知：保留预留，追加 unknown_charge，暂停后续付费调用。不得直接记零或释放。
- provider 错误但实际已计费也算请求／费用，不因解释无效删掉消费记录。解释校验失败不触发新请求。
- 结算／证据写入失败保留不确定状态，本 run 非成功；不能用内存中费用估计宣称闭环完成。
- 后来获得账单／usage 的人工补核只在另获授权的新 run 与新 reconciliation 事件说明，不改旧 unknown 事件或原响应。

最小账本只承担本 scope 的累计上界、失败占额与重启拒绝重复；不宣称银行式交易、抵御同机协同篡改或分布式并发。

## 6. 响应结构与解释校验

推荐结构化返回：schema_version、selected_plan_alias、explanation_sections（section_id、text、reference_aliases）、numeric_mentions（value_ref、display_role）。不接工具调用、自由 SQL、额外方法／指标／业务结果／审核决定。

- section_id 为固定的 purpose／prerequisites／metric_scope／limitations；每节绑定本地允许的口径或证据 alias。
- numeric_mentions 只允许引用宿主提供的 stat_row_count；模型不返回数值，宿主从已核验工具值渲染。引用不等于模型已理解该统计的业务意义。
- 自由 text 不允许直接输出数字／百分比／日期等值表达；常见工具外数值、方法越界、订单／支付／因果／效果等反向明确校验。严格 JSON 拒绝重复键、非有限数、额外键、错误类型、未知 alias、不支持版本及超量内容，不截断后假称有效。
- 指标定义、方法、S3 身份由宿主提供且不让模型回写。输出中新增指定指标／值／批准字段即失败。
- 人工解释文字需要人审阅。句子中的所有中文隐含数量／语义误导不能靠 JSON／字符串验证完全证明；自动校验通过状态仅叫 structurally_valid_draft，不叫业务结论通过。明确潜在遗漏，不宣称语义完整性。
- 模型返回拒答、空内容、截断或 invalid JSON 都受控失败；不提取代码块、补字段、静默改数或“再请求一次修好”。

模型回复及错误体是非可信输入。先有界在内存处理，检查敏感回显与 schema；被禁止内容不落盘／不回显，保存 reason_code、检查范围、状态与可安全引用的 usage 元数据。不得把 raw HTTP body、headers 或凭据写通用 trace。合法已校验响应与草稿可在获批 run 保存；明确不是自动批准的发现或业务动作。

## 7. 接口契约（已确认，未实现）

```text
load_approved_plan(review_ref) -> ApprovedPlan
build_reviewable_payload(plan) -> PayloadDraft
request_explanation(approved_payload, call_policy) -> ProviderResult
validate_explanation(result, references) -> ExplanationDraft
```

- ApprovedPlan：schema_version、S3／plan／metric／S2／data／rule／registry 身份及本地引用、允许方法与口径、允许证据／值 registry；不携带额外来源权限。
- PayloadDraft：request_body、实际字节摘要、发送目标／model／schema 身份、local_alias_map_ref、privacy_check_ref、input_manifest_ref、state=needs_outbound_approval。local_alias_map 不进入 request_body。
- ApprovedPayload：由宿主重新核验真实外发记录形成的边界对象，绑定 PayloadDraft 字节与目标、policy 身份、确认依据、一次调用范围；不接受仅靠 JSON 设置 approved=true。
- CallPolicy：明确 provider/endpoint/model、credential_source_name（不含值）、timeout／体积／输出边界、token计数依据、price身份、balance依据、累计scope／上限；缺必需参数失败。
- ProviderResult：request_id、HTTP受控状态、实际model／finish状态、结构化body或安全失败码、usage及可得性、计费分类；敏感内容仅在受限内存判断，不作日志字段。
- ExplanationDraft：schema_version、run_id、上游／payload／schema身份、校验过的引用／解释、宿主渲染数值引用、validation_state、limitations、human_review_state=pending。不生成approve或新指标。

接口与上述结构已确认，不等于现有实现；技术schema细化须遵循本契约，不能在执行阶段自定重大外发或计费产品口径。准确provider/model、费率、余额及累计数值限额仍需实际核对后另行冻结配置，不以本次契约确认代替。

## 8. 拟新增文件与证据（未授权实施）

建议只新建：

- `src/datainsight/explanation.py`：批准方案、payload构造、响应校验、独立CLI与收尾。
- `src/datainsight/deepseek_call.py`：单 provider 的有界非流式请求、安全usage提取；优先现有标准库，不先安装 SDK。
- `src/datainsight/call_budget.py`：本阶段最小追加式账本、预留／结算／不确定停止。
- `tests/test_w2b2.py`：独立反向、mock transport、预算恢复／发布故障与隐私扫描证据。
- `configs/w2b2-call-policy-v1.json`：首请求前经实际核对与独立批准才新建；无密钥值，必需未知项不填伪值。

依赖选择是实施默认，不证明标准库已能满足实际 model/token 能力。若可靠计数或协议需要新依赖，先解释来源、版本与D盘安装范围，另获授权；不得执行到一半自动装包或降低预算门。

普通正式证据 `outputs/W2-B2/<run_id>/`；mock fixture `outputs/_scratch/<batch>/<case>/`；账本见第5节。拟议CLI prepare／explain，当前不存在命令。

准备run拟含 approved-plan.json、payload.json、alias-map.json、input-manifest.json、privacy-check.json、environment.json、command证据和final-status；外发批准另新run，不回写准备结果。调用run拟含请求非敏感摘要／authorization引用、budget-check与事件引用、安全validated-response或failure、usage与cost、explanation-draft、环境／命令／网络范围／终态。所有实际文件名及参数在详细交接／动作请求中明确。

计算／响应处理状态仍待最终收尾；仅全部必需引用、usage／费用／账本和环境证据齐全才发布该次调用success。草稿有效与账本完成分开，缺任一不宣称真实最小闭环通过。失败run与原子发布tmp保留。

## 9. 精确权限分组（当前均未授权）

| 权限 | 目的与候选范围 | 不包含 |
|---|---|---|
| P-B2-IMPL | 新增第8节四个模块／测试，实际按文件说明；mock不接外部服务 | 不改W1/W2-A/W2-B1、标准、配置／凭据，不运行／安装 |
| P-B2-MOCK | 项目venv离线运行受控正常／反向／预算故障／隐私扫描，新scratch与W2-B2证据 | 不请求模型、官方站点、余额或计数外部API |
| P-B2-CHECK | 单独列实际provider文档／余额核对来源与必要联网／用户提供资料方式 | 不自动生成请求、不读取密钥值、不付费probe；实际方式另批 |
| P-B2-POLICY | 实際model／费率／上界／余额／累计限额确认后新建无密钥policy及唯一budget scope初始记录 | 不把充值计划当许可，不初始化替代账本归零 |
| P-B2-PREPARE | 固定已批准方案重新核验，生成本地完整payload与privacy证据 | 不外发、不运行CSV、不再approve方案 |
| P-B2-OUTBOUND | 用户审阅实际body／目标／限额后新建独立外发许可记录 | 不等于S4或后续多次调用许可 |
| P-B2-CALL | 批准准确命令、credential来源名、目标、payload／policy、一次请求、新run与预算事件写入 | 不重试、换model、扩大额度、代理跳转或上传额外文件 |
| P-B2-RESULT-DOC | 新建结果索引并更新INDEX，实际mock／准备／真实调用分类 | 不改标准、旧证据或自行最终验收 |

权限可以在完整精确披露后由用户同次批准相邻步骤，但不能从“确认方案”隐含获得。首次外发仍在实际payload可见后批准；技术条款判定责任按文档头声明。

## 10. 下一步与待决定

验收见 `acceptance/W2-B2-v1.md`，已依据用户确认标为frozen；C201–C212内容未变。ADR-006保留原批准方向及历史draft表述，当前状态以方案／标准文件头为准；本轮未授权修改ADR，也不扩大实际调用许可。

详细接口、payload白名单／草稿语义、单次调用门与验收安排不再重复询问。准确provider/model、费率、余额与累计数值限额仍延后到明确的首请求核对；未确认就停止付费入口，不提前询问密钥或猜数。

若mock通过但真实门不满足，交付明确“离线门控已测／真实调用未验收”，不能称整个W2-B2模型闭环通过。保留W2-B1基线，不静默换模型或为了进度取消付费安全门。

low交接见 `handoffs/W2-B2-sol61-low-v1.md`，用户手动转交；执行者先只读核对并逐批获取权限。P-B2-DOC-F仅文档状态更新及交接新建，不运行项目、不联网、不读取密钥。真实证据返回后由规划／验收方技术判定。
