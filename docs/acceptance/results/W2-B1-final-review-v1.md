# W2-B1 最终验收记录 v1

## 1. 总判定与责任

**总判定：不通过。** 正常候选生成与独立 S3 approve 已运行成功，但必需的上游依赖变化反向及本阶段已有输出保护用例未闭合，不能有条件放行。

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

- 冻结标准：[W2-B1-v1](../W2-B1-v1.md)，保持 frozen，B101–B112 不改。
- 方案：[W2-B1-plan-v1](../../W2-B1-plan-v1.md)。
- 原执行记录：[w2b1-review-219e79901d08444bab62c6e61f6e2211](w2b1-review-219e79901d08444bab62c6e61f6e2211.md)，保留当时“未验收”的原文。
- 技术验收责任：规划／验收方；用户指定职责为 sol6.1 high，不表示实际模型路由被切换。
- 文档动作授权：用户对“新建本记录并更新 INDEX”的请求回复“批准”，并提出新增项目记录规范；不授权测试修改、实现修复、命令或补测。
- confirmation_actor：用户。
- confirmed_at：not_provided。
- recorded_at：null。
- recorded_at_source：not_available。
- recorded_at_status：unavailable。
- recorded_at_reason：本轮文件工具未返回精确记录时间，没有执行取时命令；不得估计或使用历史运行时间代替。
- 记录规范：[ADR-005](../../decisions/ADR-005-approval-responsibility-and-confirmation-time.md)。规范仅约束新记录／模板，不改变本验收标准或补测范围。

本轮最小闭环是只读技术验收结论落盘与 INDEX 同步。没有执行项目、测试、安装、联网、模型调用或独立重算摘要。

业务 approve 表示用户选择方案／确认口径，不等于技术验收通过；原 approve 记录不修改，当前不通过也不捏造或撤销其历史业务选择。本阶段暂不进入 W2-B2 或 S4。

## 2. 方法与直接证据

项目根：`D:\MyPythonProjects\datainsight`；以下相对路径均基于项目根。

先读取用户指定执行结果与 INDEX，再依据冻结标准追查 JSON、日志、源码和运行时测试快照。执行方自评、完成描述及 test.log OK 不单独作为通过依据。

### 2.1 合成运行

- 首次失败根：`outputs/W2-B1/w2b1-syn-4c27236f9fcf4f88bf5ab0e4d969b80d/`。
- 修正后成功根：`outputs/W2-B1/w2b1-syn-60e61a5474ca4536bca9a5fff29487e4/`。

直接读取首次 batch-result.json：errors=1、failures=0、tests_run=15、exit_status=2，发布矩阵 missing_fault_cases 非空。结合执行记录，失败为合成长 run 名触发 invalid_identifier；原失败保留，没有放宽功能 identifier。

直接读取成功批次 test.log 与 batch-result：15 tests、79.602s、OK；failures=0、errors=0、exit_status=0、missing_fault_cases=[]、uncovered_paths=[]、protection_unchanged=true。数字来自工具结果，不是本次重新运行或估计。

成功批次还直接读取／定向核对：

- source-snapshots/test_w2b1.py：实际运行的测试、合成链、case 与 runner。
- case-results.json：独立上游变更与候选／receipt 字段变更映射。
- fault-results.json：正常、底层发布故障及逐证据文件写入故障。
- privacy-scan.json、artifact-inventory.json：扫描范围、findings、自引用排除与产物导航。
- source-identity.json、protected-files-after.json：源码身份及指定保护项。

suite 为 PlanningLogicTests、PlanningChainTests 加两项已明确的 W1 接口用例：test_unknown_template_before_connection、test_result_boundaries_and_nested_types。不是 W1 全回归，也没有重新运行 W2-A 全套或生产 CSV。

成功批次实际功能身份记录：planning.py 摘要 `fba945459dc0462b580484d398beeaae81191cddc1021cdd737b3c28cc602a23`，planning_methods.py 摘要 `c158f87f997a07404d9faddfa578a72f19f56c607b8d2316f86db80f2b9cbc30`；测试快照摘要 `6ef98086dbfe0337ab927b2f59ba770c6be09e848e8c8957d772ad7936924002`。仅引用已保存工具值，本验收者未独立计算。

### 2.2 固定真实 S2 核验与候选

候选根：`outputs/W2-B1/w2b1-candidates-1f9fa1e612fa4c19b48181111a3a35d6/`。

直接读取：candidate-plans.json、accepted-context.json 必要部分、reference-check.json、final-status.json、environment.json、network-observation.json。

独立观察根：`outputs/W2-B1/w2b1-local-observation-1f9fa1e612fa4c19b48181111a3a35d6/`，直接读取 operation.json。

观察：

- 候选仅 P-BEHAVIOUR-RECORDS v1／M-BEHAVIOUR-RECORDS，口径是固定桶原始记录数，工具证据只引用路径／摘要，不把已有 values 填作新结果。
- candidate-plans.status=computed_pending_finalization、human_review_state=pending。
- final-status=success、exit_status=0；完成时间 `2026-10-10T04:57:53.268255+00:00`。
- operation 记录 cli_exit_status=0、protection_unchanged=true、sentinel_findings=[]，列出候选八个实际文件的路径／大小／工具摘要。
- 真实入口外层调用见执行文档的完整 -c 转录；代码通过 load_s2_accept／verify_decision／load_diagnosis 重核验，而不是只查看 receipt 中 accept。

真实入口读取的是历史画像摘要与证据，不是重新读取生产 CSV。它支持核验已有文件版本绑定，不证明当前 CSV 未变化。

### 2.3 用户 S3 审核

根：`outputs/W2-B1/w2b1-review-219e79901d08444bab62c6e61f6e2211/`。

使用文件工具读取该目录的全部七个 JSON：s3-review、input-manifest、reference-check、environment、network-observation、cli-command、final-status；并用目录 Glob 核对文件导航。

观察：

- decision=approve、selected_plan_id=P-BEHAVIOUR-RECORDS、selected_plan_version=v1、confirm_metric_definition=true、actor=user。
- acceptance_scope=S3_plan_and_metric_only，不授权 S3.5、S4、查询、清洗或外发。
- receipt 绑定 plan_set、metric、S2、诊断、问题、规则、registry 和 manifest；保存字段与候选／引用相符。本轮只对照保存值，未独立重算字节。
- final-status=success、exit_status=0，完成时间 `2026-10-10T05:07:23.227623+00:00`。
- 执行文档记载用户明确选择并确认口径后独立批准命令。本轮没有读取另一会话的原批准消息，不把 receipt 当用户身份认证系统。

历史 receipt.confirmed_at=`2026-10-10T05:07:22.472485+00:00`，执行文档说明它是工具记录操作时间，不是用户消息精确时间。按 ADR-005，旧记录原位保留，引用时不得将该值冒称用户提供的确认时间；本轮不修改 schema 或历史字段。

### 2.4 代码审查

直接读取 planning.py、planning_methods.py，结合运行时测试快照逐项审查。关键函数：load_s2_accept、build_candidate_plans、new_run、load_plan_set、review_check、record_s3_review、verify_review、main。

本轮没有全仓差异／权限审计，没有独立打开全部子 run。重点补充核对候选发布改名故障目录及 candidate-plans 的 pending 状态：仅有 .tmp 残留，无发布成功终态；.tmp 内容不能当作 success。

## 3. B101–B112 逐项判定

“通过”限于冻结能力与已审查证据；未测局限不自动升级为新增要求。“不通过”仅针对下列既有必需项证据缺口，不意味着已经证明功能有缺陷。

| ID | 判定 | 证据及断言依据 | 范围／原因 |
|---|---|---|---|
| B101 | 通过 | 真实候选／operation；测试快照 test_B101_real_verifiers_and_other_decisions；planning.py:26–72 | 真实入口独立进程重核验，非accept的三种决定被拒绝；不把格式有效当已受理，不宣称身份认证。 |
| B102 | 通过（受控边界范围） | 快照独立 parser／路径／版本／类型／超限／reparse 测试及日志 | 主要错误单文件独立变更，危险打开断言、严格共享parser；重解析为mock，不是实际junction攻击。 |
| B103 | 不通过 | 独立上游变更test_B103_independent_upstream_mutations、缺件用例；planning.py:26、156 | 当前已测问题版本、receipt结构／版本与终态等；未证明上游数据／诊断规则／当前方法注册表实际身份变化导致旧候选失效。保存字段变更不代替依赖变化。 |
| B104 | 通过 | test_B104_stable_and_closed、registry源码与真实候选 | 方法封闭、未知方法／自定义SQL拒绝、逻辑空集合不凑数；空集合是受控逻辑上下文，不伪造生产accept。 |
| B105 | 通过 | 固定metric、模板／契约一致断言、metric-definition变更拒绝、真实candidate | 全文件版本窗口、固定桶、无分母／比例、原始记录保留口径明确；不执行模板，不扩为订单或日期计算。 |
| B106 | 通过 | no-business-values断言、candidate-value注入拒绝、真实candidate | 预期输出schema与结果分开，无新业务值；未穷举每个额外指标词汇不是新的阻塞要求。 |
| B107 | 通过（本地人工记录范围） | API独立review错误、CLI反向及真实receipt | 选定ID/version、指标摘要、显式确认与actor/time必需；规划批准不当业务许可。旧时间语义如上明确。 |
| B108 | 不通过 | verify_review恢复、独立plan/receipt字段变更；planning.py:231 | 现有metric／registry_hash保存值与receipt dataset/scope变更拒绝；缺上游实际依赖变化后旧审核失效的针对性证据，与B103同一缺口。 |
| B109 | 不通过 | 合成源候选前后摘要、真实候选保护、scope；planning.py:99–107、281–283 | 本阶段已有输出拒绝且原文件集合／字节不变的必需测试不存在；W2-A测试不能替代新new_run／main。 |
| B110 | 通过（合成I/O范围） | fault-results、missing_fault_cases=[]、真实publish包装、pending实物 | 两CLI正常／逐证据写入／底层open/write/flush/fsync/rename已测，失败非零无发布success、tmp保留；不是系统崩溃证明。故障计算状态报告未逐项展开保持局限。 |
| B111 | 通过（限定哨兵与观察范围） | 合成privacy-scan findings=[]、streams、调用观察；真实候选限定扫描 | 合法元数据探针进入受控链，输出／错误扫描范围明确；真实审核未专项扫描、非全面敏感值/native审计，保持未测，不另加当前阻塞。 |
| B112 | 不通过（待必需项闭合） | 测试日志、环境／命令、inventory、结果／INDEX | 已有正常与故障测试、两项接口回归及导航；B103/B108/B109必需反向缺口尚未完成，不能因15tests OK判全项满足。 |

当前阻塞仅为两类：上游依赖变化拒绝证据（B103/B108），本阶段已有输出保护测试（B109），B112随必需补测闭合。隐私、安全、证据必需项不能降为非阻塞遗留放行。

## 4. 最小补测闭环（不授权执行）

### T1：实际依赖身份变化令旧候选／审核失效

定位：`tests/test_w2b1.py` 的 test_B103_independent_upstream_mutations、test_B108_independent_plan_and_receipt_bindings；被测恢复入口 load_plan_set／verify_review。

现有用例改变 candidate 的 registry_hash、receipt 的dataset_version或scope，能证明保存内容不一致被拒绝，但不能证明当前上游依赖改变会使既有批准失效。

最小新增证据：

1. 每项由完整合法合成链创建成功候选与受控审核，先证明其生成／恢复有效。
2. 分别独立改变当前上游数据版本／输入身份、诊断规则身份、方法注册表身份。测试真实依赖重新核验／重建路径，不仅修改旧产物里的绑定字段。
3. 核对新上下文生成或旧上下文复用会按已冻结契约拒绝；旧候选恢复与旧S3审核恢复均拒绝，不默认继续。
4. 可以用只针对新合成输入的字节读取patch或当前规则／registry注册函数身份patch，明确范围；不能改真实功能源码／配置／旧证据或完全mock掉验证入口。
5. 保存合法基线、实际变更对象、身份、预期／实际reason_code及拒绝路径，不能用前一个错误掩盖下一项。

不要求穷举所有源码字节或攻击方式；只补已冻结数据／规则／registry变化类。现有问题版本与保存值错配用例保留回归，不删、不改期望凑通过。

### T2：已有输出拒绝且内容不变

定位：`tests/test_w2b1.py`，被测 `planning.new_run`、`planning.main`。

1. 在本轮新受控输出目录建立待保护文件／标记；不在旧正式run试写或试覆盖。
2. candidates与review分别调用实际main，output-dir指定已存在合成目录。
3. 断言output_exists／非零，原文件集合与实际字节摘要不变，没有新终态、临时或其他文件写入。
4. 必要时监控文件打开模式，证明不触发写入；review使用合法受控候选，不能用上游错误代替既有输出拒绝。
5. 现有new_run存在性逻辑也应由受控测试覆盖；不降低identifier/path门，不修改旧W2-A函数。

### 实施纪律

- 先只补测试与新受控fixture／证据，不预先修改功能实现。
- 只有真实测试失败且定位为功能缺陷才提出最小实现修复，另行请求文件／函数与复测授权；本验收没有确认实现缺陷。
- 补测使用新run，保留旧失败与成功记录，结果另存；不回填当前批次。
- 不重跑生产CSV、不重验W1/W2-A、不重新发起真实S2或S3批准、不接DeepSeek、不增加当前补测范围。
- 记录／模板采用ADR-005不等于修改功能时间字段；当前补测不包含时间schema重构、历史迁移或新的时间测试。

## 5. 可保留成果与未测边界

### 可保留

- 正常确定性候选与完整固定口径已实际生成。
- 固定真实S2 receipt已独立进程重核验，独立S3业务选择／确认已记录。
- 方案／指标与统计结果分离，scope保持S3-only。
- 合成真实发布路径故障、限定隐私哨兵与产物导航已实现并运行。
- 首次长合成命名失败原位保留，单文件测试命名修正没有放宽功能边界。

### 保持未测，不自动新增阻塞

- 真实review未另跑独立恢复、审核前后源候选保护摘要或专项文件／stdout/stderr扫描；真实审核目录没有独立工具摘要清单。本轮文件读取／Glob不冒充这些未运行工具报告。
- 全部上游源码变化穷举、全面真实敏感值审计、系统崩溃／native隔离／并发替换／协同篡改防护。
- 当前生产CSV新哈希、新生产统计、自由SQL、模型／计费或S4能力。

W1最后生产计算与修复后合成收尾依旧分开；本次候选／review是历史画像上的新阶段运行，不是新CSV生产计算。

## 6. 权限与下一步

本轮仅新增本最终验收记录、ADR-005，并更新INDEX当前判定／规范导航。冻结标准、接口、已有产物与时间值保持原状，没有执行任何测试或命令。

新增ADR-005只约束记录与模板；不是技术标准或功能变更，也不扩大T1–T2范围。用户对范围／目的／验收安排的确认不承担当时未验证技术条款的认证责任。

待用户产品决策：本轮无。低档补测执行交接：本轮尚未新增。下一步可申请T1–T2自包含交接，再由执行对话逐批请求测试文件修改、新fixture／证据运行和结果文档权限。旧阶段权限与本轮文档批准不复用。

当前总判定保持 **不通过**，暂不进入W2-B2、S3.5或S4。补测返回真实证据后规划／验收方再复验，保留本次历史记录。
