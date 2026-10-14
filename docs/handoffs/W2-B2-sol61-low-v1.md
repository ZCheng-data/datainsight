# W2-B2 · sol6.1 low 自包含执行交接 v1

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

- 目的：只实现一次有界 DeepSeek 方案解释闭环；先离线门控／mock，再按实际配置核对与独立批准决定是否能调用。
- confirmation_actor：用户。
- confirmation_basis：用户确认详细接口、payload 白名单、调用／预算门与 C201–C212，随后批准 P-B2-DOC-F 状态落盘和本交接新建。
- confirmed_at：not_provided。
- recorded_at：null；recorded_at_source：not_available；recorded_at_status：unavailable。
- recorded_at_reason：本轮文件工具未提供精确记录时间，没有运行取时命令，不估计或借用历史运行时间。
- authorization_scope：仅规划文档确认状态更新与本交接新建；不授权实现、测试命令、联网核对、凭据读取、外发或付费请求。
- 当前阶段：未实现、未运行、未验收；详细标准已冻结，实际服务／价格／余额／累计预算数值未核对。

## 0. 可复制的新执行对话启动文字

```text
请只读 D:\MyPythonProjects\datainsight\docs\handoffs\W2-B2-sol61-low-v1.md 及必要契约／代码，接续 W2-B2。
你负责用户指定 sol6.1 low 执行，不宣称切换实际模型，不自行最终验收。
先只读核对，报告具体冲突（无则写无），列 P-B2-IMPL 的精确新文件清单和目的，等待批准。
详细契约及 C201–C212 已冻结，不重问领域、路径、DeepSeek、D盘规则，不重验或重装 W1/W2-A/W2-B1。
先实现并测试离线 mock、payload、响应校验及预算停止门；mock只用受控假服务／假usage／假费率，不能配置成真实付费许可。
准确 endpoint/model、结构化能力、token上界、价格／余额／累计限额仍待核对；没有独立 CHECK/POLICY/OUTBOUND/CALL 授权不得联网、读密钥或请求API。
S3 approve 不是外发批准；准备好的完整实际body与目标／policy需展示后另获批准，真实调用最多一次、零自动重试。
不读原始CSV、不运行SQL、不改候选／指标／S3、不自动进入清洗或S4，不修改既有实现／标准／证据，不创建其他Agent／Session。
每批修改或命令先说明精确范围并等待确认；错误／未知计费停止、不自动兜底。
对话只给结论与决策点，60行以内；详细结果获批后放docs/，不落盘对话推理／讨论／临时文字草稿。运行后由用户转回规划／验收方验收。
```

## 【目标】

重新核验已批准方案 → 编译完整最小请求 → 用户审核外发与预算 → 工具持久预留 → 单次 DeepSeek 生成 → 结构／引用／安全校验、真实 usage 与工具费用核算 → 本地解释草稿和证据。

模型只能解释现有单方法与口径。既有确定性方案是权威基线；模型不改候选／metric，不决定受理、清洗或分析路径，不计算业务数字、不执行SQL。

自由解释输出仅 `structurally_valid_draft`、`human_review_state=pending`。结构校验不能认证全部语义；不要称它是新数据发现、已批准业务结论或自动行动。

## 【前置状态与权威文件】

项目根：`D:\MyPythonProjects\datainsight`，不是聊天工作区。

先只读：

1. `docs/W2-B2-plan-v1.md`：accepted；接口、payload、预算协议及设计边界。
2. `docs/acceptance/W2-B2-v1.md`：frozen，C201–C212 全部必需，条款未变。
3. `docs/decisions/ADR-006-W2B2-model-explanation-and-call-gates.md`：方向与有限模型职责。
4. `docs/decisions/ADR-003-directory-and-evidence-layout.md`：永久证据、scratch、原子发布例外。
5. `docs/decisions/ADR-005-approval-responsibility-and-confirmation-time.md`：技术责任与时间记录。
6. `docs/acceptance/results/W2-B1-final-review-v2.md`：前置阶段通过及能力边界。
7. 必要处读 `src/datainsight/planning.py`、`planning_methods.py`、`feasibility.py`、`feasibility_rules.py`；测试复用必要助手时只读对应测试，不运行其历史 runner。
8. 原读取契约与源码封闭画像模板仅作为定义／引用核对，不执行查询。

ADR-006 保留其原先 draft 的历史描述，本轮未改；当前详细标准以方案／验收文件头为准，不据此重新询问冻结或自行改 ADR。

W1、W2-A、W2-B1 已通过，不从零复验或重装。已有项目 Python 3.12.9 与 DuckDB 1.4.1；本闭环默认标准库，不启动数据库引擎。

W1 修复前最后生产计算与修复后合成收尾依旧分开，历史结果不能冒称修复后生产实测。当前 CSV 未再次核验；本阶段只读已验收摘要，不重新统计。

新稿约定以用户指定准备包 `D:\DataInsight-Prep\insight-agent-planner\SKILL.md` 为准；安装旧技能不得覆盖新稿或引入自动教学／全项目生成。准备包不是项目仓库。

## 【固定本地输入与核验】

```text
outputs/W2-B1/w2b1-review-219e79901d08444bab62c6e61f6e2211/s3-review.json
outputs/W2-B1/w2b1-candidates-1f9fa1e612fa4c19b48181111a3a35d6/candidate-plans.json
docs/acceptance/results/W2-B1-final-review-v2.md
```

上述两run的终态、manifest、引用检查、context，以及现有 `planning.verify_review`／`load_plan_set`／上游核验需要的固定W2-A receipt／诊断、历史画像包、契约／问题／规则／模板可按需读取。真实准备动作前列完整精确清单，不给任意目录扫描权限。

- 调用真实 `verify_review`，再要求 decision=approve、confirm_metric_definition=true、集合内候选与metric摘要匹配；验证有效的 cancel／reject 不能放行模型请求。
- 当前唯一选定方法 M-BEHAVIOUR-RECORDS，候选 P-BEHAVIOUR-RECORDS v1。身份从工具读取核验，不从本交接猜摘要。
- 核验上游当前字节与manifest、规则／registry；变化停止，不重做批准、不为旧记录更新绑定。
- row_count 只能来自核验后的固定历史 `summary-result.json` 及对应 evidence，保存本地可重跑引用，不把模型生成或手写值当工具统计。
- SQL／parameters／source_path 是证据数据，不获得执行／读取权限；原始CSV不属于允许输入。
- 上游历史confirmed_at原位保留，引用说明旧语义；不改上游schema或把旧S3时间当新外发时间。

## 【文件范围】

### P-B2-IMPL 可申请的新建文件

| 文件 | 职责 |
|---|---|
| `src/datainsight/explanation.py` | approve核验、最小payload、引用／解释schema、本阶段CLI与收尾 |
| `src/datainsight/deepseek_call.py` | 固定provider有界非流式transport、安全响应／usage提取，不带自动重试 |
| `src/datainsight/call_budget.py` | 唯一批准scope的追加事件、累计预留／结算／未知计费停止与最小排他 |
| `tests/test_w2b2.py` | 独立反向、mock transport、预算恢复／竞争、真实发布路径故障、隐私扫描及证据runner |

只新建，存在则停止，不覆盖。不要修改W1/W2-A/W2-B1源码、测试、配置、标准、ADR或旧run。无需根目录runner；支持测试代码可在本测试文件中，不建设通用Agent／多provider框架。

无密钥真实policy `configs/w2b2-call-policy-v1.json` **不在 P-B2-IMPL 权限内**。只能在实际核对并 P-B2-POLICY 获批后新建；未知真实参数不填示例值冒充已批准配置。

实际协议／计数能力尚未核对。离线代码应提供明确“未配置→拒绝”的接口与受控mock，不猜model ID、价格或返回分类来让真实入口运行。若实现必须先核对官方协议，先报告具体依赖，请求P-B2-CHECK；不能偷偷联网或把整个实现分组当核对许可。

新增SDK／tokenizer等依赖不默认批准。无法用现有工具可靠计数时保持付费入口拒绝；另提精确版本、来源、安装／缓存D盘范围，不降预算标准。

### 普通证据与mock位置

- mock主批次：`outputs/W2-B2/w2b2-mock-<工具生成uuid>/`。
- fixture：`outputs/_scratch/<batch>/<test_method>/<case_id>/`。
- mock子run：`outputs/W2-B2/<batch>-<短case>-<阶段>/`，测试前验证现有identifier限制，禁止放宽限制。
- prepare：`outputs/W2-B2/w2b2-prepare-<工具生成uuid>/`。
- 外发授权：`outputs/W2-B2/w2b2-outbound-<工具生成uuid>/`，新独立记录，不回写prepare。
- 实际调用：`outputs/W2-B2/w2b2-call-<工具生成uuid>/`。
- 真实配置核对：另一个获批 `w2b2-check-<uuid>` run，非敏感资料／来源记录，不发生成请求。

所有实际case、文件白名单、suite与命令在各运行申请中列明。新uuid由工具生成，不伪造时间／耗时／数值。已存在输出拒绝；重跑使用新run和新权限。

准备证据至少：approved-plan.json、payload.json、alias-map.json、input-manifest.json、privacy-check.json、reference-check.json、environment.json、cli-command.json、final-status.json。

外发记录至少：outbound-authorization.json、binding-check.json、environment／cli-command及合法终态；绑定实际request body、endpoint/model、schema、policy／价格／预算及上游版本。不能只用文件approved=true或聊天旧许可建立边界对象。

调用证据至少：request-metadata.json（不含秘密头）、authorization引用、budget-check.json、账本事件引用、validated-response.json或安全failure.json、usage.json、cost.json、explanation-draft.json（合法时）、input-manifest.json、reference-check.json、environment.json、cli-command.json、network-observation.json、final-status.json。失败／缺usage不补造成功字段，按实际状态保存安全未知。

测试证据需完整命令／环境／源码身份、test.log、独立case结果、发送计数／顺序、预算事件、故障／恢复结果、隐私扫描、逐文件清单、当前保护摘要及batch-result/status。具体文件名在动作申请中列清楚，自引用排除明确，不把所有错误报告豁免扫描。

### 追加预算证据run

路径：`outputs/W2-B2/budget-<实际批准scope_id>/`，唯一scope，真实policy批准前不创建生产scope。

事件：`event-<单调序号>-<类型>.json`，类型reservation／attempt_started／settlement／unknown_charge／reconciliation。每个事件独占发布、不覆盖／移动／删除，绑定policy、request_id、前序及实际工具结果。新增事件是已批准scope协议，不是改旧证据。

mock scope只在本批明确批准的新合成位置，用synthetic标识，不被真实入口接受，不能以它作为真实余额／累计账本。

最小排他状态文件位置在运行申请中精确列出，限D盘批准工具状态目录；不得让锁内容扩大权限。正常完成的锁释放必须在该批明确说明所用机制；故障／残留锁不自动清除或借换scope绕过。不删除预算事件。

一般工具临时在outputs/_scratch或.cache/tmp；终态／事件原子发布 `.tmp` 留目标同目录／同文件系统，必要例外，不迁移／当垃圾清理。证据目录稳定，失败同样保留。

## 【接口与结构：已确认，不重选产品边界】

```text
load_approved_plan(review_ref) -> ApprovedPlan
build_reviewable_payload(plan) -> PayloadDraft
request_explanation(approved_payload, call_policy) -> ProviderResult
validate_explanation(result, references) -> ExplanationDraft
```

- ApprovedPlan：S3／plan／metric／S2／data／rule／registry身份、本地引用、允许方法与引用registry，不携带新访问权限。
- PayloadDraft：完整request_body与实际字节摘要、目标／model／schema身份、local_alias_map_ref、privacy_check、manifest，state=needs_outbound_approval。
- ApprovedPayload：宿主重新核验真实外发记录形成，绑定上述字节／目标／policy／上游及一次许可；调用入口拒绝任意JSON伪造批准。
- CallPolicy：明确provider/endpoint/model、credential来源名（非值）、全部timeout／大小／计费上界、计数工具依据、价格／余额、scope与累计限额。必需项未知就失败，不设隐含真实默认。
- ProviderResult：受控HTTP状态、实际model／finish状态、已检查body或安全失败码、真实usage及可用性，禁止敏感raw内容作日志字段。
- ExplanationDraft：上游／payload／schema身份、固定引用解释、宿主工具值渲染、validation_state、limitations、human_review_state=pending，不产生approve或新指标。

技术schema实现细节可以沿项目惯例；涉及新外发内容、预算口径、模型行为等重大变化先报告，不能按实现便利修改冻结条款。

## 【payload：完整body白名单】

首次仅：

1. 固定任务：解释已批准原始记录计数方案及前提／边界，不推荐新分析。
2. 必需schema：behaviour／VARCHAR。省略user_id、goods_id、category_id、timestamp等不必要字段。
3. 固定口径：pv/fav/cart/buy精确匹配、NULL→missing、其余非NULL→other；全文件版本窗口、无分母、时间unknown、不筛／不去重／不改文本；不证明订单／支付。
4. 固定历史工具row_count作为唯一聚合值；核验其本地证据，不能发送其他桶实际计数、时间极值或用户基数。
5. 局部alias p_selected／schema_behaviour／metric_records／stat_row_count；alias→路径／hash映射只留本地。
6. 不确认的业务语义／日期覆盖与当前CSV未重新验证等限制。

禁止把整个plan/context/receipt/evidence/Markdown外发，禁止本机路径、run_id、源SQL／参数、数据hash、原始行、标识／hash／伪匿名ID、逐用户特征／分组、密钥、未知枚举或自由文本样例进入请求。

固定六代码是方法定义，不是源枚举；此请求没有低频分组，不自行添加阈值或用户分组来“丰富解释”。row_count如需删或换要呈现具体改动并重新批准，不静默改body。

审核覆盖system、user、response schema、model／采样／输出上限等全部JSON字段；保存规范真实发送字节摘要。endpoint与非敏感envelope展示，Authorization值只在发送前进程内装配，不保存完整headers。

SDK／客户端若额外注入字段会改变body，必须展示再批准；不能批准一个文件而实际发送另一组messages。白名单构造是主防线，扫描只证明指定范围，不宣称自动匿名化。

## 【响应与草稿校验】

结构：schema_version、selected_plan_alias、explanation_sections（section_id/text/reference_aliases）、numeric_mentions（value_ref/display_role）。固定section_id为purpose／prerequisites／metric_scope／limitations。

- numeric_mentions只允许stat_row_count引用，模型不填数，宿主引用工具值渲染。
- text不允许直接输出数字／百分比／日期值；常见工具外数值、方法／指标越界、订单／支付／因果／效果误述要有明确反向拦截。
- 严格JSON拒绝重复键、非有限数、额外字段／错误类型／版本、未知alias、工具调用／SQL／新指标／批准字段、超量内容；超限不截断后当合法。
- 拒答、空响应、截断、invalid JSON受控失败；不提取代码块补成JSON、不默默修引用／数值，不为修复再次请求。
- 句子全部隐含数量或语义不能由schema完全证明；通过状态只叫structurally_valid_draft，不认证业务正确。人审阅前始终pending。

raw回复和错误体有界内存处理，先检查敏感回显／合法性，不把违规raw保存为“调试证据”。失败只保存安全reason、检查范围与安全可用usage；密钥、禁止body、raw头及错误异常中的敏感内容不得进入trace／stdout／stderr。合法响应可保存但仍是草稿。

## 【真实provider／预算核对：当前未知，不能猜】

首请求前需要实际证据和用户配置确认：精确DeepSeek endpoint/model、HTTPS固定目标／证书、非流式结构化模式、凭据来源名、真实费率版本与币种、余额依据、完整输入token可靠上界、全部计费输出可强制上界、累计请求／input/output token／金额上限、唯一scope与有效期。

- 不向用户索要聊天里的密钥；只批准专用进程来源名，P-B2-CALL后该进程读值，不读全环境、不回显。
- 不假定某model／价格／余额，不使用20–30元充值计划作调用上限，不默认余额全部可花。
- 不按字符数估token、不使用未批准外部计数服务。可靠官方保证上界或经验证model相容计数工具才可覆盖完整body。
- max_tokens不能直接当所有model的全部计费输出上界；若额外推理类别未知或不可控，停止，不选另一个model绕过。
- 首真实请求前冻结准确policy／rate／scope，缺值拒绝付费入口；离线假费率只能用于合成oracle。
- CHECK需要联网／余额查询／读取用户资料时，精确列URL／动作／是否认证／请求／费用与内容，等待批准。不做paid能力probe，不创建自动检查请求。

已冻结设计限制：一次明确许可最多一次生成尝试；自动重试0；非流式；整个请求总时间上限60秒；响应体64KiB；redirect拒绝。不是实测，不能用每次read重新给60秒替代整体deadline，也不能超限后截断回包装作合法。

HTTP默认代理、重定向、SDK重试或隐式model路由不得扩目标。实际环境需要代理等例外时停止提出独立目标／权限变化，不偷偷继承全局配置。

## 【账本预留、结算与失败】

1. 重新核验上游、payload许可、实际policy／price／balance和完整scope事件；缺件／不一致／残留未发布事件／锁冲突停止，不当零。
2. 受控单写者排他下工具计算预留，用最高适用费率，不预设cache命中。费用Decimal或明确最小计费单位，向上预留规则清楚。
3. 持久reservation与attempt_started均确认成功后才准发送，发送顺序有mock观察。保守记录尝试／预留可早于实际发送，但报告真实transport调用计数须区分为0／已尝试／未知，不能称未发送就一定被计费。
4. 未结算／崩溃窗口预留跨重启占额，不自动释放／重发；run／policy名变化不能归零，更不能新建替代scope躲累计。
5. 实际usage的输入／输出／cache／reasoning分类和实际model经核验才工具计费；必须绑定有来源费率，不按字符串长度或估计填usage。
6. 费用仅称按provider usage计算的成本，没有账单对照不称实际扣款认证。invalid解释仍可能消费，不删收费事件或自动重试。
7. 超时、错误、缺usage／不相容usage、超预留或中断：保留预留，追加unknown_charge并暂停后续付费，不记零／释放。结算落盘失败同样不成功。
8. 后来reconciliation另批新run／追加事件，不改旧unknown、原响应或原终态。

单scope恢复／损坏／竞争反向必须真实测试，不能只用内存计数。预算架构限当前单写者，不宣称分布式事务或协同篡改防御。

## 【验收索引】

完整权威条款见frozen文件，下面只是交接索引。

| ID | 必须交回 |
|---|---|
| C201 | 真实approve／口径核验、固定来源及上游变化拒绝，prepare独立证据 |
| C202 | 完整body白名单／各层独立注入／隐私报告；禁止内容未发送断言 |
| C203 | 实际body／目标／policy／上游绑定的单次外发许可，变更／重启消费拒绝 |
| C204 | 准确服务／model／能力资料、HTTPS／凭据安全与transport反向，不隐式换路由 |
| C205 | 可靠token输入上界、输出全部计费上界、实际rate／balance／限额与工具预留 |
| C206 | 跨run账本、发送前持久顺序、限额／损坏／竞争／崩溃恢复拒绝 |
| C207 | 一次attempt、无重试、整体超时／有界body／拒redirect及实际调用状态 |
| C208 | 合法与独立异常响应、引用／宿主渲染、安全草稿状态；无静默修复 |
| C209 | 真usage／model、工具费用、实际预算结算或unknown保留，不假零 |
| C210 | 请求／响应／错误／trace／streams安全扫描、违规raw不落盘、秘密不回显 |
| C211 | 新run／旧文件保护、已有输出拒绝、prepare/call/ledger逐持久化故障，tmp保留 |
| C212 | mock与真实生成分别证据；全门满足的一次真实请求、usage/cost/settlement/草稿齐全 |

所有主要反向独立合法基线，单条件变化并断言相应原因／是否发送。禁止积累错误后冒称独立覆盖。真实publish／ledger底层write/flush/fsync/rename故障不得只整函数mock；发送前失败调用数为0，发送后证据不足按风险状态诚实保留。

mock真实请求次数须为0；provider能力／usage／真实币额不能由mock证明。若真实配置／门控未满足，交付“离线门控已测试／真实调用未验收”，不宣布W2-B2整体通过、不静默换模型或取消标准。

## 【逐批权限与命令纪律】

当前所有执行分组未授权。每批修改／命令先列精确路径、目的、读取／写入、实际argv、cwd、环境变量／凭据来源名、停止条件，等待确认。

1. P-B2-IMPL：只新建三个功能模块和一个测试文件，离线代码／mock，不运行、不建真实policy。
2. P-B2-MOCK：实际runner与fixture白名单核对后运行受控正常／反向，生成新批次／scope；无任何网络／真实key。可以在test_w2b2.py内证据runner，拟议入口 `项目python -B -m test_w2b2 --w2b2-evidence`，当前不存在，实际命令实现后再请求。
3. P-B2-CHECK：只核对批准资料／实际服务能力与余额方式，不发生成／paid probe。读取确需联网另批准，不能用本地实现许可代替。
4. P-B2-POLICY：实际model／费率／上界／余额／累计数字批准后，才新建无密钥policy、批准scope初始事件与限定锁状态；不得偷偷填默认。
5. P-B2-PREPARE：独立批准固定本地链核验、真实完整body准备与扫描，写新prepare；不外发。
6. P-B2-OUTBOUND：人查看实际完整body、目标/model、预留与budget身份，明确是否外发，保存新许可记录。未给时间confirmed_at=not_provided，工具另取recorded_at，不代签。
7. P-B2-CALL：再次核验实际批准对象后，批准准确命令与专用credential来源名、固定目标、一项请求、新调用run与预算追加／结算；该进程可按批准读key但不向模型或日志披露。失败停止不重试。
8. P-B2-RESULT-DOC：新增 `docs/acceptance/results/<run_id>.md` 并更新INDEX的实际阶段／待验收链接，不改旧结论或自行通过。

相邻步骤只有精确披露后用户明确同次批准才能合并；首次OUTBOUND必须在实际payload可见后。技术契约冻结、文档批准、S3approve都不是网络／费用授权。

运行项目解释器 `.venv/Scripts/python.exe`，cwd项目根，PYTHONPATH指项目src/tests，PYTHONDONTWRITEBYTECODE=1，TEMP/TMP/TMPDIR指项目.cache/tmp；记录实际sys.executable／tempfile生效值，不只抄变量。未获运行许可不为路径查询提前执行命令。

## 【停止与禁止】

配置／费率／上界／限额／usage未知、路径异常、测试失败、泄露、上游变化、账本损坏／锁残留、预留不足、证据收尾失败就停止。不安装兜底、不换model／endpoint、不提高金额、不自动重试或释放未知计费预留。

不初始化／重装项目、不运行历史安装／RECORD／生产profile/replay、不读取CSV或原始行、不改已有源码／标准／配置／证据，不做Git提交／推送、不自动创建会话。

不得上传目录、日志、local aliases或凭据；可获批外发的只有审核过body和必要认证头。官方文档／余额查询也是联网动作另批，不以“没有调用生成模型”为理由自动进行。

## 【完成后】

返回mock／配置核对／prepare／outbound／真实call各自实际状态、命令、输入／policy／price／scope身份、真实usage／工具费用与账本事件、正常／反向日志、扫描／清单／保护及未测项。调用失败如实保留费用未知与是否落盘，不包装成成功。

时间记录按ADR-005，不改上游旧confirmed_at；新批准不提供字面时间记not_provided，recorded_at由获批工具实际取得、独立来源。解释草稿技术校验不由用户批准代替；技术判定回交规划／验收方。

执行结果写“未验收，待规划／验收方判定”。C212没有真实闭环证据不得称阶段通过；用户手动转回结果路径后只读验收，不自动进入S4或下一付费尝试，不生成额外教学／面试交接。
