# W2-B1 最终验收记录 v2：T1–T2 复验通过

## 1. 当前最终判定与责任

**总判定：通过。阻塞项：无。**

T1–T2 已关闭 v1 指出的当前上游依赖变化拒绝与本阶段已有输出保护缺口；结合原已通过项，W2-B1 在冻结的固定本地来源、确定性候选及 S3 口径审核范围内通过。

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

- 冻结标准：[W2-B1-v1](../W2-B1-v1.md)，B101–B112 保持 frozen，条款未改。
- 方案：[W2-B1-plan-v1](../../W2-B1-plan-v1.md)，接口与口径未改。
- 历史判定：[W2-B1-final-review-v1](W2-B1-final-review-v1.md)，当时“不通过”及依据原位保留。
- 原执行记录：[候选与独立 S3 approve](w2b1-review-219e79901d08444bab62c6e61f6e2211.md)，不回写其当时“未验收”状态。
- 补测交接：[T1–T2 low 交接](../../handoffs/W2-B1-T1-T2-sol61-low-v1.md)。
- 补测执行记录：[w2b1-t1t2-8811bf4a7b404d3cac7222b32ff6a021](w2b1-t1t2-8811bf4a7b404d3cac7222b32ff6a021.md)，保留其“待复验”原文。
- 规划／验收职责：用户指定 sol6.1 high；没有探测或切换实际模型。
- 文档动作授权依据：用户对“新建 v2 并更新 INDEX”的请求回复“批准”。
- confirmation_actor：用户。
- confirmed_at：not_provided。
- recorded_at：null。
- recorded_at_source：not_available。
- recorded_at_status：unavailable。
- recorded_at_reason：本轮文件工具未返回可信精确记录时间，没有执行取时命令，不以补测时间、会话日期或估计时刻代替。
- authorization_scope：仅新建本文件并更新 INDEX 导航；不改标准、实现、执行记录或旧证据，不新增运行。
- 记录规范：[ADR-005](../../decisions/ADR-005-approval-responsibility-and-confirmation-time.md)。

本轮最小闭环是复验结论落盘与入口同步。不是新一次执行，也不是用户重新作出业务 approve。

已验收能力：有效 S2 accept 重新核验 → 封闭合格方法生成确定性候选与完整指标口径 → 用户明确选择与确认，或停止 → 独立、版本绑定的 S3 记录。结束于 S3，不包括清洗、SQL 执行、S4 或模型接入。

## 2. 复验方法与证据

项目根：`D:\MyPythonProjects\datainsight`。下列路径相对项目根。

先只读用户指定的补测结果与 INDEX，再直接读取运行产物和运行时测试源码快照，核对实际断言与拒绝路径。没有把“low 已补测”、执行方自评、batch-status=success 或测试数量单独作为通过理由。

本次没有运行项目或测试，没有独立重算文件摘要，没有修改代码或标准。摘要比较依据已保存工具报告及其生成／比较代码；不冒称本验收者执行了独立字节计算。

### 2.1 新补测批次

证据根：`outputs/W2-B1/w2b1-t1t2-8811bf4a7b404d3cac7222b32ff6a021/`。以下简称 B。

直接读取／按需定向核对：

- batch-command.json、batch-environment.json、source-identity.json。
- test.log、batch-result.json、batch-status.json。
- authorization-record.json。
- t1-dependency-results.json：按 case 与 checks 定向读取，核对 data／rules／registry 的变更对象、三个入口与 actual／expected／matches。
- t2-existing-output-results.json：目标及源候选 before／after、实际返回／异常原因、stdout／stderr、写入观察与终态存在性。
- source-snapshots/test_w2b1.py：T1、T2、runner、保护、扫描、清单与完成条件。
- protected-files-before.json、protected-files-after.json、privacy-scan.json、artifact-inventory.json、fault-results.json 的必要字段与范围。

直接核对的实物包括：T2 review 的新 target 目录仅有 marker.json；T1 registry 基线合成 review 的合法成功终态。未逐个独立打开全部子 run；不将定向报告审查冒称全文件独立审计。

### 2.2 工具运行原值

- test.log：17 tests、105.675s、OK。
- batch-result：tests_run=17、failures=0、errors=0、exit_status=0、t1_t2_complete=true、missing_fault_cases=[]、uncovered_paths=[]、protection_unchanged=true、final_acceptance=not_performed。
- batch-status：started_at=`2026-10-10T06:30:00.727778+00:00`，completed_at=`2026-10-10T06:31:55.214375+00:00`，status=success、exit_status=0。

这些是运行工具产物的已保存值，不是本次重新运行或估计。批次成功只指测试／补证流程，故障子 run 的预期失败不能被当作正常功能成功。

suite 为 PlanningLogicTests 与 PlanningChainTests 全部（含 T1/T2），加两项已明确的 W1 接口单测：test_unknown_template_before_connection、test_result_boundaries_and_nested_types。没有 W1／W2-A 全回归，不重新验收上游或运行生产查询。

batch-command 保存实际 sys.argv、项目解释器、cwd、B 及完整 shell 转录：`-B -m test_w2b1 --w2b1-t1t2-evidence`。该命令是历史证据，不是本文件授予的新运行许可。

环境报告记录项目 `.venv/Scripts/python.exe`、Python 3.12.9、项目根 cwd、实际 tempfile `.cache/tmp` 及相应 TEMP／TMP／TMPDIR、PYTHONDONTWRITEBYTECODE=1。

### 2.3 身份与保护

source-identity 记录测试快照 SHA-256 为 `f82bd89d6fd6a6742b866d768b43230bf4ce3d837714b096271d34bb6c6c1d54`。

本批 planning.py 摘要仍为 `fba945459dc0462b580484d398beeaae81191cddc1021cdd737b3c28cc602a23`；planning_methods.py 仍为 `c158f87f997a07404d9faddfa578a72f19f56c607b8d2316f86db80f2b9cbc30`，与原成功批次的已保存身份一致。标准与配置保护摘要也保持，支持本次仅补测试而未修功能的记录；不是全仓差异或供应链审计。

runner 对指定功能模块、标准、ADR-003/004/005、原契约与问题配置的 before／after 比较为成功必要条件。该证据证明本次指定观察窗口内一致，不是对所有历史文件完整前后审计，也不恢复原运行前摘要。

## 3. T1：当前依赖身份变化闭合

测试源码快照 `test_T1_dependency_changes`（第 503–559 行）按每项独立完整合法合成链执行：真实 load_s2_accept、候选生成／恢复、受控 cancel 与 verify_review 成功，保存基线；随后只改变一个当前依赖，不修改已发布候选／receipt／manifest。

| case | 实际依赖变化 | 旧上下文复用 | 旧候选恢复 | 旧审核恢复 | 判定 |
|---|---|---|---|---|---|
| data | 当前合成 profile.dataset_version 单文件字节读取 patch，使用工具生成新身份 | fixture_acceptance | fixture_acceptance | fixture_acceptance | 通过 |
| rules | 当前 feasibility.rules_module.registered_rules 返回新版本／摘要；真实 evaluate／diagnose／load_diagnosis 保持 | diagnosis_or_rules_changed | diagnosis_or_rules_changed | diagnosis_or_rules_changed | 通过 |
| registry | 当前 planning_methods.registered_methods 返回新 registry 版本／摘要；真实候选生成和恢复保持 | unregistered_planning_methods | candidate_plan_changed | candidate_plan_changed | 通过 |

每条 checks 的 actual 与 expected 匹配，case 的 unchanged=true；源码断言 before==after 和每条 matches。不是整验证函数预设拒绝，也不是只修改保存 candidate.registry_hash 或 receipt.dataset_version。

data case 在真实 adapter 的 fixture acceptance 不一致处拒绝；它验证单个当前数据身份改变不能沿用旧批准，不宣称已部署内部全部一致的新数据链。rules case 经过诊断重建比对；registry case 分别验证旧注册参数失效与旧计划重建不符。

当前身份变化采用限定 patch，明确模拟范围。不修改生产 CSV 或功能源码，不证明真实部署、并发替换或协同篡改抵抗。将来合法新版本配合新的审批流程仍可生成新候选；本测试不要求永久拒绝所有新版本。

**T1 关闭 B103／B108 的原缺口。**

## 4. T2：已有输出拒绝与内容保护闭合

测试源码快照 `test_T2_existing_output_protection`（第 561–608 行）先建立合法完整链与成功源候选／受控审核，另新建本轮 target，保存 marker。真实 planning.main 或 new_run 检查存在性，不由监控层制造 OSError。

| case | 入口 | 实际结果 | 保护观察 | 判定 |
|---|---|---|---|---|
| candidates | planning.main | 返回 2，reason_code=output_exists | target／source before==after，write_events=[]，terminal_exists=false | 通过 |
| review | planning.main，合法源候选及 cancel | 返回 2，reason_code=output_exists | target／source before==after，write_events=[]，terminal_exists=false | 通过 |
| newrun | planning.new_run | 实际异常 output_exists；测试助手记 2 | target／source before==after，write_events=[]，terminal_exists=false | 通过 |

newrun 的 2 是测试助手对受控异常的记录，不是另一个 CLI 进程的退出状态。main 两项则是实际函数返回值。报告含 argv／direct_call、stdout／stderr、文件集合、大小及实际工具摘要。

目标目录实物只保留 marker；拒绝没有新增终态或 .tmp。写入观察为被动记录并调用底层原方法，没有用强制失败代替真实入口拒绝。

只对本轮新受控目录做保护测试，没有向历史真实候选／审核发起覆盖尝试。

**T2 关闭 B109 的原缺口。**

## 5. B101–B112 综合判定

前次已通过项继承原证据及限定范围，并有本次全阶段正常／反向与发布故障回归。补证改变的是证据充分性，不是标准或接口。

| ID | 当前判定 | 依据与边界 |
|---|---|---|
| B101 | 通过 | 原固定真实 S2 独立进程重核验与非 accept 拒绝；本次合成完整链继续回归，不重新作真实 S2 决定。 |
| B102 | 通过 | 原独立 parser／路径／版本／类型／大小／重解析 mock，保持原受控边界范围，不宣称真实 junction 防御。 |
| B103 | 通过 | 原实际缺件／独立结构与问题变更，加本次 T1 当前数据／规则／registry 身份变化的复用与恢复拒绝。 |
| B104 | 通过 | 源码封闭单一方法、稳定内容、未知注册输入拒绝与受控空集合继续回归，不凑候选。 |
| B105 | 通过 | 原固定桶原始记录计数口径、契约／模板一致与错误定义拒绝；没有新增计算或日期／订单语义。 |
| B106 | 通过 | 原 candidate 无业务值、预期 schema 非结果及非法结果注入拒绝继续回归。 |
| B107 | 通过 | 原真实用户选择／口径确认与独立 S3 approve，API／CLI 审核反向继续回归；合成 cancel 不是新的用户决定。 |
| B108 | 通过 | 原候选／receipt 字段绑定与恢复反向，加 T1 当前依赖变化导致旧审核失效；不默认批准，不自动 S4。 |
| B109 | 通过 | 原独立 run／scope／源候选保护，加 T2 本阶段 main／new_run 同名输出拒绝及完整字节／集合保护。 |
| B110 | 通过 | 原两 CLI 真实 publish 及逐证据／底层故障矩阵在本次回归，missing_fault_cases=[]；非零无发布成功，tmp 原位保留。 |
| B111 | 通过 | 原合法元数据探针、输出／错误扫描与调用观察，及本批 findings=[]；限指定哨兵与包装范围，不当全系统隐私认证。 |
| B112 | 通过 | 原真实入口／审核、完整命令与证据，加本批 17 tests、T1/T2 完成、故障／扫描／清单／保护闭合；不是 W1/W2-A 全回归。 |

总判定通过，阻塞项无。不根据测试数量计算“准确率”或宣传业务效果。

## 6. 报告范围、时间与能力局限

### 扫描／清单

privacy-scan 明确 scanned_files、streams、fixture／test-source 排除，findings=[]，无单独 trace。artifact-inventory 明确实际路径／类别／大小／工具摘要，自引用报告排除 artifact-inventory、privacy-scan、batch-result、batch-status；runner 复查 covered／missing，并且未覆盖路径为非成功条件。

末尾 batch-result／status 不含自摘要，属于明确预声明报告范围，不是无限自认证；该排除不扩大为产品输出豁免。本次新 run／scratch 的范围与有限调用观察已审查，不宣称完整监控全部 Python／native 行为。

### ADR-005 时间与责任

authorization-record 保存 confirmed_at=not_provided，独立 recorded_at=`2026-10-10T06:30:00.756620+00:00`，来源为 Python datetime.now(timezone.utc) via feasibility.now。它是运行授权记录的工具操作时间，不是用户确认时刻，也不是本验收文档保存时间。

本文件不借该时间补填文档 recorded_at。受控合成 cancel 的既有功能 schema 时间参数明确是 synthetic_test_input／not_user_confirmation；没有迁移功能时间字段、回填旧 receipt 或增加时间测试要求。

### 证据类别分开

- 原成功合成测试：`outputs/W2-B1/w2b1-syn-60e61a5474ca4536bca9a5fff29487e4/`。
- 原真实候选：`outputs/W2-B1/w2b1-candidates-1f9fa1e612fa4c19b48181111a3a35d6/`，独立观察另目录。
- 原真实 S3 approve：`outputs/W2-B1/w2b1-review-219e79901d08444bab62c6e61f6e2211/`。
- 本次 T1–T2：新合成补测目录 B，不替代原真实入口／决定。
- 首次失败：`outputs/W2-B1/w2b1-syn-4c27236f9fcf4f88bf5ab0e4d969b80d/`，历史记录原位保留。

W1 修复前最后生产计算与修复后合成收尾继续分别引用，不能称修复后完整生产实测。本阶段只使用已验收历史画像，不重跑 CSV、不重验 W1/W2-A。

### 未测／不支持

- 原真实 review 的独立恢复运行、审核前后专项保护／敏感扫描及独立工具清单；原 v1 已明确保持未测，本次不擅自新增或假称补做。
- 当前生产 CSV 的新读取／哈希、新生产统计或查询。
- 所有真实敏感值审计、所有上游字节变更穷举、真实 Windows junction、并发路径替换、系统崩溃／native 网络隔离或协同篡改防护。
- 自由 SQL、任意方法／规则、用户级特征、清洗、S4–S6。
- DeepSeek 接入、provider/model 能力、外发 payload、usage／计费实测。

这些是能力边界，不是当前冻结范围的新增阻塞。通过的是确定性候选与本地 S3 口径审核，不是完整 W2 或 LLM Agent。

## 7. 本轮保护与下一步

本轮只新建本复验记录并更新 INDEX；不修改 v1、执行记录、标准、代码、配置、ADR 或运行证据，不运行命令。

`outputs/<阶段>/<run_id>/` 稳定引用保留，失败 run／同目录 .tmp 均不移动、删除、覆盖或清理。旧不通过判定是当时证据状态，保留其历史；新通过依据为本次新增补证，不追写到旧运行。

待用户业务决策：本轮无。新增 ADR：本轮无。新增执行／教学交接：本轮无。

下一步可只读规划 W2-B2 的一个最小闭环。DeepSeek 的已确认选择与 D 盘规则保留；首次真实请求仍需核对准确 provider/model、能力、费率／余额、累计请求/token/费用上限、脱敏 payload 及当轮调用许可，未知计费／限额缺失不调用。

**W2-B1 通过不授权 W2-B2、清洗、S4、联网或外部 API。** 后续仍先规划、明确责任与验收安排，再按具体动作取得许可。
