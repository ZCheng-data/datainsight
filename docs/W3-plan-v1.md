# W3方案 v1：唯一方法的真实计算、三层校验与本地报告草稿

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

- 状态：accepted；详细接口、资源设计及D301–D312验收安排已获用户确认，内容未变；闭环方向按ADR-008批准。
- 当前实现／运行／验收：未实现、未运行、未验收。
- confirmation_actor：用户。
- confirmation_basis：用户先确认八项方向边界并批准合批文档落盘，随后对“一次确认W3方案／标准／交接的详细安排并冻结”的建议回复“确认”；据此执行P-W3-DOC-F，仅保存确认／冻结状态和同步INDEX。
- confirmed_at：not_provided。
- recorded_at：null；recorded_at_source：not_available；recorded_at_status：unavailable。
- recorded_at_reason：本次确认状态保存仅使用文件工具，未取得可信精确时刻，无取时命令许可，不估计或借用历史时间。
- authorization_scope：P-W3-DOC-F仅本方案、W3标准、low交接确认／冻结状态与INDEX导航更新；无代码、测试、CSV／真实画像摘要工具读取、策略决定、网络／API许可。
- 对应：[ADR-008](decisions/ADR-008-closed-intent-evidence-baseline-and-W3-boundary.md)、[证据基线](project-position-and-evidence-baseline-v1.md)、[冻结标准](acceptance/W3-v1.md)、[low交接](handoffs/W3-sol61-low-v1.md)。

## 1. 最小结果闭环

固定S3审核及依赖有效 → G3.5人明确选择原始记录全保留 → 另获本次真实读取许可 → E3：确认源身份、计算固定桶原始记录数、S5执行／口径／边界校验、发布本地报告草稿 → 一次W3技术验收。

已有部分使用阶段证据：历史生产画像与模板重跑、源前后身份一致、真实S2 accept及S3方案／口径approve；**尚无完整S4→S5→S6真实业务结论闭环**。W3必须新增真实计算及校验报告，不以旧数字复制、合成用例或文档替代。

W3到S5，报告草稿human_review_state=pending。随后独立S6人工业务解释确认才补齐完整案例闭环。S6记录不在本轮功能实现范围；其选择／引用／记录契约在看到W3结果后冻结，不自动确认，不自动外发。

## 2. 固定输入与保护范围

项目根：`D:\MyPythonProjects\datainsight`。

| 输入 | 固定路径／约束 |
|---|---|
| 真实S3 receipt | `outputs/W2-B1/w2b1-review-219e79901d08444bab62c6e61f6e2211/s3-review.json` |
| 真实候选 | `outputs/W2-B1/w2b1-candidates-1f9fa1e612fa4c19b48181111a3a35d6/candidate-plans.json` |
| 真实S2 receipt | `outputs/W2-A/s2-accept-3178ad8b677e49edb91de623be0c3905/decision.json` |
| 问题 | `configs/w2a-question-v1.json`，只接受现有behaviour_record_counts／raw_record |
| 读取契约 | `configs/w1b-read-contract-v1.json`，现有严格五列VARCHAR读取 |
| CSV | `D:\大数据项目\电商用户行为分析\第9章\UserBehavior.csv`，仅独立许可后本地只读 |
| 上游依赖 | 只读现有`planning.verify_review`／`load_plan_set`实际需要的固定证据／manifest集合；不扫描全部outputs |

真实工具读取画像／摘要和源CSV均须明确许可，文档阅读／旧S2／S3批准不替代。策略记录可绑定已审数据版本，不打开CSV；执行必须重新计算实际源字节身份并与该版本比较。

源身份不符、规则／方法／口径／问题变化、上游缺件或批准失效：停止，不重跑W1／W2、不重新受理或自动更新批准。核对原始源前后身份不等于新画像，也不为旧run补终态。

保护：W1／W2所有源码、配置、标准、结果、receipt与旧run原位保留；不改`planning_methods.py`、`profile_templates.py`、`__main__.py`或预算模块。

## 3. 唯一方法与结论边界

method_id=`M-BEHAVIOUR-RECORDS`，plan_id=`P-BEHAVIOUR-RECORDS`。规则／注册表及完整metric_definition由现有核验链取得，不另造口径。

- 一条读取后的原始记录，按behaviour精确文本pv／fav／cart／buy；NULL→missing，其他非NULL→other。
- 全文件数据版本窗口；不作日期覆盖、时间过滤或排序。
- 保留全部记录、重复和其他字段NULL；不trim、改大小写、删重、填补或筛选。
- 只输出固定桶记录数；不生成订单、支付、用户数、比例／转化、GMV、日期分组、效果或因果声明。
- S5核对用全文件row_count只作覆盖完整性证据，不变成新增分析方法、分母或比例。

报告的数值、显示和比较只由宿主工具产生。本轮最小报告列出桶及计数与限定描述，不增加排序、比率、双口径或自由业务建议。

## 4. 功能文件与拟议接口

仅新增：

- `src/datainsight/analysis.py`：W3固定输入核验、策略记录、计算／校验／草稿及独立CLI，必要计算worker也放本模块，不建通用执行框架。
- `tests/test_w3.py`：独立合成参考、正常／反向／发布故障测试及一个证据runner。
- 合成原始CSV：`tests/fixtures/w3/<batch_id>/`内新文件；合成上游／审核包：`outputs/_scratch/<batch_id>/`。不改旧fixture。

不新增依赖、用户自定义SQL、模型接口、入口翻译或问题文件路径扩展。

以下是待实现契约，不是当前函数或可运行命令：

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

ExecutionContext：有效approve、选定method／plan、数据／问题／诊断规则／注册表／口径身份、S2／S3和必要输入引用／实际字节hash、读取契约及完整口径。它不赋予源读取或动作授权。

StrategySpec：decision=`preserve_all`／`reject`／`cancel`、actor、confirmed_at。`preserve_all`是本轮唯一可执行策略；其他清洗策略拒绝，不默认替用户选择。新确认时间支持用户字面值或not_provided；独立recorded_at由获批运行工具取得，来源与精度明确。

StrategyReceipt：独立run、决定、actor／confirmation_basis、confirmed_at、recorded_at及来源、S3／选定方案／数据／问题／规则／方法／口径／策略版本身份及必要引用；scope=`S3.5_preserve_all_only`，不表示本次真实读取获批。reject／cancel不产生执行资格。

CalculationEvidence：固定SQL／模板版本／实际hash、源路径本地参数、读取契约、数据前后工具hash、六桶聚合结果、辅助row_count、实际结果字节hash、执行环境／资源配置、工具状态。无原始行、标识值、低频原文或密钥。

ValidationResult：execution／metric／boundary三项明确pass／fail与reason_code；引用相应证据。ValidatedClaims只允许固定claim_type=`behaviour_bucket_raw_record_count`、固定bucket及value_ref／evidence_ref，不开放任意文字或直接数值输入。

W3Run：阶段状态／退出码、必需结果引用、数据及版本身份、validation_state、human_review_state=pending。计算完成先pending，最终成功由唯一合法final-status.json表示。

## 5. 复用与计算边界

只读已存在接口：`planning.verify_review`、`planning.load_plan_set`、`planning_methods.definition`／`registered_methods`；源与契约用`inspection.validate_source`／`fingerprint_file`、`profile.load_read_contract`／`validate_profile_source`，固定SQL用`profile_templates.build_template`及现有结果校验。

现有核验函数内部重复重建和manifest读取保留，不为精简审计报告修改旧实现。W3不另要求反复新进程恢复或全历史枚举。

当前`profile.execute_profile_template`没有W3所需的计算超时／资源监督接口；不能只调用它就宣称资源受控。W3可以在新模块的受控worker内复用固定SQL生成、源／契约和结果验证，创建局部DuckDB连接并设置宿主config。不得改旧函数或执行SET／INSTALL／LOAD等SQL。

允许SQL仅固定SELECT／WITH：behaviours、summary及完整严格解析所需的五列非NULL聚合／零行schema核验。后者只作读契约／覆盖验证，不报告新的业务指标，不运行全部画像模板。实际SQL及参数保留为本地可重跑证据。

### 已确认资源设计值（未实测）

- DuckDB内存配置`memory_limit=256MiB`、`threads=1`；临时／扩展目录沿用项目`.cache/duckdb/tmp`／`extensions`，自动安装／加载关闭；经固定SELECT核对实际配置。
- E3从执行入口起总体deadline为180秒；源hash按块检查剩余时间，计算worker等待只使用剩余预算，超时终止／回收本模块的固定子进程，不重试。结束清理可有有限额外等待，不把它包装为全系统硬实时保证。
- 原始源前后哈希包含在该时间预算；超时停止，不自动提高限额。
- 聚合结果仅一行固定六桶计数，辅助row_count独立；单结果64KiB上限，超限拒绝不截断。草稿／每个JSON产物1MiB上限，写前检查；无逐用户或自由文本结果。
- 只允许本项目venv的固定本模块worker；无用户可控命令／shell，worker直接入口同样核验来源和策略，不能绕过父入口门。所有模型／网络调用禁止，不宣称DuckDB原生或系统级隔离。

这是本查询的有限资源设计，不是通用SQL沙箱、所有内存总量或OS故障隔离认证。设计值若导致真实失败，保留失败并停止，调整需另版／批准。

## 6. S5三层与草稿发布

1. 执行层：源hash与已批版本匹配且前后相同；固定SQL／schema／完整读取与结果hash有效；六桶均非负整数；工具核对桶和等于辅助row_count；工具退出成功、必需引用有效。
2. 口径层：完整metric_definition与已批定义／hash一致，SQL与固定模板一致；原始粒度、全保留、精确文本、NULL／other、全文件窗口一致。
3. 边界层：claims来自封闭schema和工具value_ref，不接受新增claim类型／字段／任意文本；显示为代码记录数，不推订单／支付／比例／时间／效果；至少一个无依据声明负向被拒绝。

三个层级全部通过后渲染本地草稿；每个数值和限定结论有结果／SQL证据引用。报告包含问题、口径、结果、三层校验、限制、pending人工状态及下一S6门，不生成行动效果。

校验失败不生成可用成功草稿，不静默修正口径、结果或声明，不请求模型修复。结论／报告数值错配、引用缺失或被改均必须拒绝成功。

## 7. 最小必要产物与终态

策略run：`outputs/W3/strategy-<run_id>/`，至少strategy.json、bindings.json、operation.json、final-status.json。

E3 run：`outputs/W3/analysis-<run_id>/`，至少bindings.json、calculation-evidence.json、result.json、validation.json、report.md、operation.json、final-status.json。只有成功路径要求report.md；失败保留已有产物与安全失败状态，不能创建“成功交付”。

- bindings只列本次消费／结论所需身份，不要求跨run全产物清单；既有上游manifest引用保持。
- operation集中实际argv、环境／依赖、源读取目的／批准依据、资源配置、阶段起止工具时间和安全状态，不记录完整环境、原始值、异常raw或密钥。
- result先独占写入，报告／validation写完并hash绑定后才发布final-status；run与已有文件拒覆盖。
- final-status唯一；同目录tmp→flush／fsync→无覆盖发布；故障不留合法success，tmp非终态原位保留。若失败状态也不可写，非零退出明确failure_evidence_persisted=false。
- 必需引用与字节hash可集中到calculation-evidence／final-status，不新增全量artifact-inventory或哨兵扫描范围报告。

## 8. 批次及权限

| 批次／门 | 允许结果 | 当前权限 |
|---|---|---|
| F3冻结 | 用户已确认本方案／标准／交接的详细安排，规划方保存确认／冻结状态 | 已完成文档确认；不授权实施或运行 |
| E3-OFFLINE | 新模块＋测试＋合成正反向／故障＋证据／结果文档，一个批次交回技术验收 | 未授权；精确文件／命令／次数另批 |
| G3.5 | 读取固定真实核验链、呈现口径，用户明确preserve_all／reject／cancel后记录 | 真实摘要读取及人工门独立，均未授权 |
| E3-REAL | 当前固定源一次执行，S4＋S5＋草稿及结果文档合批 | 待离线通过、有效策略和当次真实读取许可 |
| S6 | 在真实草稿上独立业务解释确认 | 后续独立，不预批／不外发 |

有限重跑：离线实现批可预授权首次＋一次合成重跑，仅修正新模块／测试中本契约范围问题；新依赖、旧功能修改、方法／标准／上限变化或次数用尽立即停止。真实执行一次，失败不自动重跑；重跑读取须新许可。

实际许可须绑定文档版本、准确命令／cwd、D盘环境、输入输出、次数、有限修复范围和停止条件；本方案不授予上述动作。执行每批一句话通知，无中间人工门的步骤合批，既定人工门不合并成默认批准。
