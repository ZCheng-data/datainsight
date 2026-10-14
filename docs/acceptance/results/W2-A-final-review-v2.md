# W2-A 最终验收记录 v2：R1–R4 复验通过

## 1. 当前最终判定

**总判定：通过。阻塞项：无。**

R1–R4 已关闭 v1 所指出的必需反向测试与扫描／产物证据缺口；结合此前已通过项，W2-A 在冻结的本地固定输入范围内通过。不是根据“补测结束”、执行方自评或测试数量直接判定。

- 冻结标准：[W2-A-v1](../W2-A-v1.md)，保持 frozen，A01–A15 未修改。
- 契约：[W2-A-plan-v1](../../W2-A-plan-v1.md)，接口与范围未变。
- 目录规约：[ADR-003](../../decisions/ADR-003-directory-and-evidence-layout.md)，保持 accepted。
- 前次验收：[W2-A-final-review-v1](W2-A-final-review-v1.md)，原“不通过”判定与依据原位保留。本文件是基于新增补证的后续判定，不追改 v1。
- 原执行记录：[s2-accept 批次](s2-accept-3178ad8b677e49edb91de623be0c3905.md)，保留执行者当时“未验收”的记录。
- 补测交接：[R1–R4 low 交接](../../handoffs/W2-A-R1-R4-sol61-low-v1.md)。
- 新执行记录：[r1r4-ee1dc6e19ab84b21b23fc03a0e7f5886](r1r4-ee1dc6e19ab84b21b23fc03a0e7f5886.md)，不回写其“待复验”状态。
- 规划／验收职责：用户指定 sol6.1 high；没有探测或切换实际模型。
- 本轮文档权限：用户对“新建 v2 并更新 INDEX”的请求回复“批准”；精确确认时间未提供，不以保存日期、运行时间代替。

通过能力：结构化问题＋已验收画像 → 离线确定性前提诊断 → 独立、版本绑定的 S2 人工决定记录。结束于 S2，不包含 S3 方案生成、清洗、分析执行或 DeepSeek 接入。

本轮最小闭环：把已完成的只读复验结论与证据映射落盘并同步入口。没有新运行，不授权下一阶段。

## 2. 复验方法与证据版本

项目根：`D:\MyPythonProjects\datainsight`。下述路径均相对项目根。

本次先使用文件工具读取用户指定的补测执行记录与 INDEX，再直接核对相关 JSON、日志、源码快照和受控输入／产物。只读复验没有执行测试、命令或独立哈希计算。

### 2.1 新补测批次

证据根：`outputs/W2-A/r1r4-ee1dc6e19ab84b21b23fc03a0e7f5886/`。简称 B=`r1r4-ee1dc6e19ab84b21b23fc03a0e7f5886`。

直接读取或按需定位：

- `batch-command.json`、`batch-environment.json`、`batch-source-identity.json`。
- `test.log`、`batch-result.json`、`batch-status.json`。
- `case-results.json`：合法基线、输入身份、预期／实际 reason_code、变更键、缺件及 patch 范围。
- `r3-publication-results.json`：两条 CLI 的正常与底层发布故障矩阵。
- `r4-read-observation.json`、`r4-privacy-scan.json`。
- `artifact-inventory.json`、`protected-files-before.json`、`protected-files-after.json`。
- `source-snapshots/test_w2a.py`：实际运行时保存的测试与 runner 源码。

报告体积较大时使用定向读取／内容搜索，不将被截断的页面当完整文件。case-results 已通过定向检查覆盖所有 case 的实际／预期／匹配结果；源码审查确认各项生成与断言路径。没有逐个独立打开清单中的所有文件，也没有独立重算所有摘要。

### 2.2 直接核对的实物样例

- 新 R3 diagnose-normal 的 `final-status.json`。
- 新 R3 decide-normal 的 `decision.json` 与 `final-status.json`；它是受控 `cancel`，actor=controlled_test_actor，不是重新发起真实用户 accept。
- 新 R3 decide-tmp-rename 的目录文件与 `final-status-success.tmp`：只有未发布临时状态，未见 `final-status.json`；不能把临时内容中的 success 当运行成功。
- R2 missing-result 包中仅有 summary-evidence；missing-evidence 包中仅有 summary-result，对应缺件确实在新包中省略。
- R1 unknown-profile-version 的 profile、R2 contract-version-mismatch 的契约副本，核对独立错误值。
- 本次保护报告中历史诊断／决定、功能源码、标准、ADR、原契约与问题配置的记录，并核对 runner 将整个 before／after 比较作为成功条件。

### 2.3 工具运行观察

`test.log` 原值：25 tests、10.237s、OK。

`batch-result.json` 原值：tests_run=25、failures=0、errors=0、exit_status=0、reports_complete=true、observations_complete=true、uncovered_paths=[]、final_acceptance=not_performed。

`batch-status.json` 原值：started_at=`2026-10-09T10:38:12.424320+00:00`，completed_at=`2026-10-09T10:38:28.299079+00:00`，status=success、exit_status=0。这是补证批次记录，不是阶段最终验收结论，也不等于每个故障子 run 成功。

环境文件记录：Python 3.12.9；项目 `.venv/Scripts/python.exe`；cwd 为项目根；实际 tempfile 在项目 `.cache/tmp`；TEMP／TMP／TMPDIR 对应项目临时目录，PYTHONDONTWRITEBYTECODE=1。

批次测试源码摘要由工具记录为 `181278cb882975990f5ff57ddc749839d2c91057b7cf6157566bc8acee615f78`；旧测试源码快照身份为 unknown。本文不把未知旧源码身份补成当前身份。

以上数字与摘要均引用已保存工具结果，不是本次文档动作重新计算。

## 3. R1–R4 闭合判定

| 补测 | 复验判定 | 直接证据及断言依据 | 关闭缺口 |
|---|---|---|---|
| R1 | 通过 | case-results；源码快照第 169–191 行；新独立输入 | extra-key、unknown-profile-version、bad-reading-schema 分别合法基线→单一错误；实际原因分别 invalid_object_keys、profile_identity、reading_schema，matches=true。没有遗留 extra 键掩盖后两项。 |
| R2 | 通过 | case-results；源码快照第 410–458 行；缺件实物与契约副本 | 独立契约摘要／版本错配、实际缺结果／缺 evidence、run／dataset_version／引用错配均返回对应原因；缺件创建时省略，不用整 read_bytes mock 或删除旧文件。 |
| R3 | 通过 | r3-publication-results；源码快照第 460–508、547–591 行；正常终态与失败 tmp 实物 | diagnose／decide 经真实 main／publish；open、write、flush、fsync、rename 的受控故障针对当前 run 的底层操作生效；正常返回 0、有 success；故障返回 2，无发布成功终态；双发布失败明确 failure_evidence_persisted=false。 |
| R4 | 通过（限定观察与扫描范围） | privacy-scan、read-observation、artifact-inventory、保护报告；源码快照第 520–543、594–718 行 | 合法元数据哨兵进入合成诊断／决定链，产品文件与正常／故障 stdout／stderr扫描 findings=[]；fixture／测试源码单列排除；清单、覆盖检查及本次旧文件保护比较闭合。 |

### R3 状态特别说明

- diagnose 正常／故障计算产物保持 computed_pending_finalization；最终运行成功只由合法发布终态判断。
- decide 故障时 decision.json 可能存在，报告 receipt_available=true；没有合法成功终态仍不可当作有效完成决定。文件存在不是成功。
- tmp-open 可以没有残留；其余故障按实际报告保存同目录临时残留。
- run 内 `.tmp` 是 ADR-003 的原子发布必要例外，不是遗漏或待清理项。即使文件内 status=success，也不等于已发布 final-status。
- 测试中的 fixed legacy 入口适配替换为经真实 adapter 校验的合成 snapshot；decide 恢复读取受控源诊断。保留这种同进程、合成范围，不宣称新的真实生产进程实测。

### R4 扫描与清单充分性

哨兵为 SOURCE／ROW／IDENTIFIER／SECRET／INSTRUCTION 的合成标记，不是真实业务行、标识或密钥。合法元数据中的 source_path／sql／parameters 被作为数据处理，不转换为执行权限。

动态观察聚焦 R2／R3 的 Path.open、socket connect／getaddrinfo、provider／engine imports 以及已加载 DuckDB 的指定调用入口。现有其他测试不在这些包装范围内，报告明确 unobserved；不据此宣称全部 Python／native 行为均受独立监控。

产物枚举范围是旧指定 W2-A run、新 B／B- 子 run 与本次 scratch。runner 在报告写入前枚举，随后复查覆盖；artifact-inventory、privacy-scan、batch-result、batch-status 的自引用排除明确列出。最终结果／状态文件在末尾生成，没有自摘要认证；该已声明且有限的报告排除不等于豁免产品输出，不要求自引用无限重写。

扫描报告明确文件与 stream 范围、fixture／test-source 排除、findings=[]，产品输出及错误没有普遍豁免。通过的是固定探针与范围内的隐私反向测试，不是证明任何历史真实敏感值都不存在。

before／after 一致是本次 runner 成功的必要条件；重点保存字段和代码路径已审查。它只支持本次补测窗口内指定文件未变化，不是原运行前摘要恢复、完整 W1 旧证据审计或独立供应链认证。

## 4. A01–A15 综合判定

前次已通过项保留其原限定范围；本次不重复从零运行或扩大其能力。补证改变的是验收证据充分性，不是标准。

| ID | 当前判定 | 证据依据与能力范围 |
|---|---|---|
| A01 | 通过 | v1 审查的精确历史特例、新协议合成门与来源边界；不泛化旧 success，不新增生产画像实测。 |
| A02 | 通过 | 原路径／JSON／大小／类型反向＋本次 R1 独立错误与对应拒绝原因。 |
| A03 | 通过 | 原 manifest／字节结果绑定／指纹反向＋本次 R2 契约、缺件、版本／引用错配。 |
| A04 | 通过 | 原结构化问题／未知 intent／额外输入反向，本次全 W2-A 回归保留；不支持自由文本理解。 |
| A05 | 通过 | 原历史画像正向诊断有字段／工具与规则证据，本次合成回归；不新增业务统计或订单／支付定义。 |
| A06 | 通过 | 规则层 GMV 缺字段／口径的负向回归；不要求额外真实 GMV CLI 运行。 |
| A07 | 通过 | 受控 snapshot 条件不足／方法范围反向继续回归；时间单位／时区未确认保持未知。 |
| A08 | 通过 | 固定质量观察与限制，不清洗、不推断业务真值；零值合成包等原局限保留。 |
| A09 | 通过 | 稳定规则／候选／规则源码身份回归；规则摘要不冒充整个实现认证。 |
| A10 | 通过 | 原真实 accept 与独立 receipt，条件不足／缺确认 API 反向及 cancel CLI 回归；不把合成 cancel 当用户业务决定。 |
| A11 | 通过 | 原合成恢复／版本绑定反向继续回归；本次源诊断保护与旧决定只读观察补充，不宣称真实 receipt 独立重启核验。 |
| A12 | 通过 | 原收尾文件故障回归＋本次两条 CLI 真实 publish 底层故障矩阵，无已发布 success；tmp 非终态。 |
| A13 | 通过 | 原适配层读取观察＋本次哨兵文件／streams 扫描和 R2／R3 调用观察；零模型声明保持限定范围。 |
| A14 | 通过 | 已存在输出拒绝、D 盘实际环境、同目录 tmp＋本次产物枚举与指定保护前后比较。 |
| A15 | 通过 | 原历史画像诊断／真实决定证据＋新完整 W2-A 测试与两项指定 W1 接口回归＋补证报告及结果导航；不是 W1 全回归。 |

总判定通过，无阻塞项。尚未测试的范围下列明示，不以“有条件通过”暗中解锁；本轮不计算“准确率”或宣称业务效果。

## 5. 能力、历史证据与未测项

### 已验收能力

- 固定已验收历史画像的结构化、离线确定性可行性诊断。
- 规则身份、字段／工具证据绑定、质量观察与方法前提分离。
- 封闭的原始记录分类计数候选，以及缺金额／严格漏斗需求的明确拒绝或范围缺口。
- 本地人工受理门与独立、版本绑定的 S2 决定记录。
- 本阶段正常与关键反向／故障收尾、限定哨兵扫描、产物导航与新旧证据保护。

### 三类证据不混称

1. W1 最后生产计算与模板重跑：`outputs/W1-B/final-20261009T061339601505Z/`，修复前协议，没有新协议终态。
2. W1 修复后合成收尾：`outputs/W1-B/b09-finalization-20261009T063948192695Z/`，不含再次生产计算。
3. W2-A 原历史画像诊断／真实 accept 与本次合成 R1–R4 补测：前两者保留原批次；新批次只关闭本阶段测试／证据缺口，不替代它们。

没有重跑生产 CSV，不重新验收 W1，不把目录中的 syn 字样当数据用途判断。

### 未测／不支持

- 当前原始 CSV 的再次读取、哈希验证或新生产画像／生产重跑。
- 真实决定的独立新进程重启 verify_decision；已有的是合成恢复与真实决定版本绑定记录。
- 所有真实敏感值的隐私审计、任意恶意输入穷举、所有 Python／native 调用的动态监控。
- 真实 Windows junction 攻击、同机并发路径替换、全系统网络隔离、全系统崩溃恢复、协同篡改防御。
- 通用自由 SQL、安全沙箱、任意数据来源／字段映射或新方法执行。
- DeepSeek 接入、provider/model 实测、外发 payload 审核、usage／计费／业务效果实测。
- S3／W2-B、清洗、S4–S6 或完整 Agent。

这些是能力边界，不是本文额外提出的阻塞；通过不证明以上能力。

## 6. 本轮文档修改与权限

仅：

- 新建本文件。
- 更新 `docs/acceptance/results/INDEX.md` 的当前 W2-A 判定及 v2／补测导航。

未修改功能代码、测试、配置、冻结标准、ADR、v1 验收、执行记录或运行证据。没有运行命令、安装、联网、模型/API 调用或独立重算摘要。

所有 `outputs/<阶段>/<run_id>/` 保留稳定引用位置；失败 run 和 `.tmp` 残留不移动、不删除、不覆盖、不清理。执行方记录当时状态保持原文；本文件更新的是当前验收权威，不抹去历史。

## 7. 下一步

待用户产品决策：本轮无。新增 ADR：本轮无。新增执行／教学交接：本轮无。

下一步可在新一轮只读规划 W2-B 的一个最小闭环。W2 使用 DeepSeek、项目路径与 D 盘规则保持已确认，不重问；实际 provider/model、结构化能力、费率／余额、累计请求/token/费用限额和审核后 payload 在首次调用前必须核对并获得当轮明确授权。

**W2-A 通过不是启动 S3／W2-B、写代码、运行、联网或外部 API 的授权。** 后续仍先规划、冻结标准，再按动作门请求许可。
