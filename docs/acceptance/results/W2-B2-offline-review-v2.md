# W2-B2 离线审查 v2：L1 通过，整体仍未验收

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

## 1. 判定与权限

**L1 判定：通过。L1 范围内阻塞项：无。**

**W2-B2 整体状态：未验收。** L1 只关闭首批离线审查指定的上游门独立反向、预算边界、事件绑定与锁生命周期缺口；不表示 C201–C212 全部通过，也不解锁真实调用。

- 冻结标准：[W2-B2-v1](../W2-B2-v1.md)，条款不改。
- 前次审查：[W2-B2-offline-review-v1](W2-B2-offline-review-v1.md)，保留当时离线未闭合的状态与依据。
- 首批执行：[w2b2-mock-0f19f9f22e2e4c98834f7c9f6b3bd586](w2b2-mock-0f19f9f22e2e4c98834f7c9f6b3bd586.md)。
- L1 交接：[W2-B2-L1-sol61-low-v1](../../handoffs/W2-B2-L1-sol61-low-v1.md)。
- L1 执行：[w2b2-l1-b892af4b267a4586bf1c25f4df86cdf5](w2b2-l1-b892af4b267a4586bf1c25f4df86cdf5.md)，其“待验收”原文不回写。
- confirmation_actor：用户。
- confirmation_basis：用户对“新建本审查 v2 并更新 INDEX”的请求回复“批准”。
- confirmed_at：not_provided。
- recorded_at：null；recorded_at_source：not_available；recorded_at_status：unavailable。
- recorded_at_reason：文件工具未返回可信精确记录时间，没有执行取时命令，不用 L1 运行时间或估计时刻代填。
- authorization_scope：仅新建本文件与更新 INDEX；不批准联网核对、实现、真实数据读取、凭据访问、外发或 API 请求。

本轮最小闭环为完成 L1 的一次只读技术审查并将结论落盘。没有运行项目、独立重算摘要、修改实现或新增测试。职责与时间记录遵循 ADR-005；合批方式遵循 ADR-007，不据此宣称成本或效率提升比例。

## 2. 直接证据与工具观察

项目根：`D:\MyPythonProjects\datainsight`；下述路径均相对项目根。

L1 证据根：`outputs/W2-B2/w2b2-l1-b892af4b267a4586bf1c25f4df86cdf5/`。

直接读取或定向核对：

- 执行结果文档、INDEX、batch-result.json、batch-status.json、test.log。
- upstream-gate-results.json、budget-boundary-results.json、ledger-binding-results.json、lock-lifecycle-results.json。
- source-snapshots/test_w2b2.py 中新增用例、runner 及完整性检查。
- batch-command.json、batch-environment.json、source-identity.json、authorization-record.json。
- protected-files-after.json、privacy-scan.json、artifact-inventory.json、fault-results.json 的必要字段及范围。

报告完整性与实现路径结合审查，不只依据 runner 的 l1_complete=true。没有独立打开清单中所有文件，也没有将文件读取比对冒称独立哈希审计。

### 实际运行记录

- test.log：**39 tests，45.962s，OK**。
- batch-result：tests_run=39、failures=0、errors=0、exit_status=0、l1_complete=true、missing_fault_cases=[]、uncovered_paths=[]、protection_unchanged=true。
- real_provider_calls=0、live_provider_protocol=not_verified、final_acceptance=not_performed。
- batch-status：started_at=`2026-10-10T08:20:14.257327+00:00`，completed_at=`2026-10-10T08:21:05.640083+00:00`，status=success、exit_status=0。

这些数值与时间直接引用已保存工具结果，不是本次重新运行或估计。测试耗时与批次时间是不同范围，不据它们倒推用户确认时间。

实际命令记录为项目解释器 `-B -m test_w2b2 --w2b2-l1-evidence`，同时保存完整 shell 转录、sys.argv、项目根 cwd。环境记录 Python 3.12.9、项目 venv、实际 `.cache/tmp` 与对应 TEMP／TMP／TMPDIR、PYTHONDONTWRITEBYTECODE=1。

source-identity 中测试快照摘要为 `d890e046b2d29951140422227732ce8cef53dbab004796c1bd4cc2772ce1bff0`。explanation.py、deepseek_call.py、call_budget.py 的已保存摘要与首批一致，且本次保护报告保持一致；支持本批只改测试的证据，不是全仓差异审计。

## 3. L1-A：上游方案门独立反向通过

运行时测试快照 `test_l1_upstream_independent_changes`（第 752–824 行）为每项创建独立完整合成 approve 链，先实际加载合法 ApprovedPlan，再以限定字节读取或注册身份 patch 改变一个条件。

| case | 实际变化／路径 | 预期与实际结果 | 判定 |
|---|---|---|---|
| approve-baseline | 合法合成 S3 approve，经真实核验 | accepted | 通过 |
| missing-terminal | 指定 S3 final-status 单文件读取缺失 | file_missing_or_size_boundary | 通过 |
| missing-reference | 指定 S3 reference-check 单文件读取缺失 | file_missing_or_size_boundary | 通过 |
| data-change | 当前合成 profile.dataset_version 变化 | fixture_acceptance | 通过 |
| rules-change | 当前诊断 registered_rules 身份变化 | diagnosis_or_rules_changed | 通过 |
| registry-change | 当前方案 registered_methods 身份变化 | candidate_plan_changed | 通过 |

六项均有合法基线身份、实际目标及 actual／expected 匹配。真实 verify_review、上游恢复、诊断／计划重建路径保留，没有整函数预设失败。缺件通过指定读取失败模拟，不宣称已创建缺件包实物，不删除已发布文件。

transport_calls=0 是本测试未调用其 mock 哨兵的记录。该哨兵未连接到方案核验流程，**不作为独立发送拦截证明**；此项通过依据是实际方案门拒绝与受控测试范围。真实发送门仍关闭且留后续验收。

固定历史 profile 路由到经 adapter 校验的新合成包，只模拟当前依赖变化，不声称重新核验真实生产来源、部署新源码或抵御协同篡改。

结论：L1-A 指定的 C201 离线缺口闭合；固定真实方案的新进程 prepare 仍未实施，不把整个 C201 标为完整通过。

## 4. L1-B：预算边界、事件绑定与锁生命周期通过

### 4.1 独立累计边界

测试快照第 829–863 行分别以 input、output、amount 为唯一限制，其他限额与 request_limit 不先触发。先完成一次合法结算，下一请求使用不同 request_id，经真实预留与累计检查。

| 维度 | exact | over | 关键证据 |
|---|---|---|---|
| 输入 token | 正好覆盖累计与下一预留，允许 | budget_limit_exceeded | 第二次调用分别为 1／0；over 账本前后不变 |
| 输出 token | 正好覆盖累计与下一预留，允许 | budget_limit_exceeded | 第二次调用分别为 1／0；其他限额非绑定 |
| 金额 | 工具计算累计费用＋下一最高预留，允许 | budget_limit_exceeded | 精确算术 oracle；over 无新事件／发送 |

全部独立 case 的实际结果与预期一致，金额来自 reserve_amount／exact_amount_sum 工具算术；mock 费率及 usage 不是实际 provider 价格、余额或费用证据。

### 4.2 事件链恢复

测试快照第 872–908 行先真实追加／结算与恢复成功，再独立模拟：

- sequence-gap：限定目录列表不显示一个事件，真实恢复与 attempt 都拒绝 budget_sequence_gap。
- previous-hash：仅单事件读取字节的前序摘要变化，两入口拒绝 budget_event_binding。
- policy-hash：仅单事件读取字节的 policy 身份变化，两入口拒绝 budget_event_binding。

各项 transport_calls=0，退出 patch 后原账本与基线相等。序号缺口是可见集合模拟，不是真实删除；不据此宣称已测试所有损坏方式或协同篡改防御。

### 4.3 锁生命周期

测试快照第 910–957 行使用实际 mock_scope_lock 与账本流程，并在限定锁文件／OS 操作上注入故障。

| case | 实际结果 | mock 调用／消费 | 判定 |
|---|---|---|---|
| open-fail | OSError | 调用 0，事件为空 | 通过 |
| acquire-fail | budget_lock_conflict | 调用 0，事件为空 | 通过 |
| release-normal | success | 同 scope 两次顺序请求完成，锁文件仍保留 | 通过 |
| release-fail | OSError | 已调用一次，settlement 保留；入口未返回成功 | 通过 |
| close-fail | OSError | 实际关闭后注入失败，已调用一次且 settlement 保留 | 通过 |

发送后释放故障不能把已发生调用改记为 0。settlement 已知且完整时保留它，不把释放异常伪装为未知费用或撤销消费。

正常 OS 解锁／关闭不是删除锁文件。释放故障仍通过真实 stream.close 回收 OS 资源；close-fail 明确为真实关闭后抛错，不能宣传为真实 handle 永久残留测试。没有删除锁文件或换 scope 绕过该失败。

结论：L1-B 指定的 C206 离线覆盖缺口闭合。真实 policy、唯一生产 scope 及真实累计预算门仍待独立核对和实现，不把合成 scope 当生产许可。

## 5. 回归、扫描及证据保护

原 mock 测试与故障矩阵保留回归，新增四个测试方法承载上述独立 case；总数 39 不代表工程得分或“准确率”。

fault-results 中 settlement-rename 保留 reservation／attempt_started 与未发布 settlement.tmp，mock_send_count=1；call 终态改名故障保留 success／failed 两个 tmp，没有发布终态。缺失故障集合为空只说明本 runner 列举矩阵齐全，不证明尚未实现的产品 CLI。

privacy-scan 指定文件及 stdout／stderr／test.log，findings=[]；fixture 与测试源码排除明确。扫描仅证明指定探针范围，不认证全部真实敏感值。读取／网络观察限 Path.open、socket connect／getaddrinfo，不宣称 native 或全系统隔离。

artifact-inventory 覆盖本次 B 前缀上游子 run、同 UUID 的 w2b2-mock 授权／调用子 run、budget-synthetic scope、scratch 及锁文件。没有按 B 前缀漏掉受 helper 限制使用 mock 别名的产物。自引用报告排除明确，uncovered_paths=[]；末尾结果／状态文件没有自摘要认证，不无限回写。

保护摘要是本次指定源码／标准／配置／ADR 观察窗口的前后工具比较，不能冒称历史运行前摘要或全历史审计。旧首批 mock、上游阶段及所有失败／临时残留原位保留。

## 6. 非阻塞记录瑕疵

本次 authorization-record.json 的 confirmation_basis 仍为通用 `P-B2-MOCK single offline batch approval`，未准确标识本批 `P-B2-L1` 范围预授权；运行时测试快照沿用了该文本。

执行结果文档与实际 batch-command 明确关联 L1，但本验收者没有读取另一执行会话的原始批准消息，不将自动生成的通用字段当成独立授权认证。

处理：原文件不回填、不为此重跑；后续新授权记录使用实际批准编号、命令／次数与范围。如需补充历史授权来源，只能另行新记录引用，不改旧 run。该记录准确性瑕疵不改变本次离线技术断言与 L1 判定，也不扩大任何未来权限。

该记录的 confirmed_at=not_provided 与 recorded_at=`2026-10-10T08:20:14.286469+00:00` 分开；后者是工具记录操作时刻，不是用户确认或本文件保存时刻。本文件不借用它填写 recorded_at。

## 7. W2-B2 剩余门与最小下一步

L1 所列离线缺口已关闭，不继续重复扩建假 provider 协议。首批已测试的 payload／响应结构、算术、持久化及故障机制可作为后续基础；不据此宣称所有离线产品能力已完成。

仍未实现或未实核：

- C204/C205：实际 endpoint／model／结构化协议、可靠输入 token 上界、全部输出计费上界、费率／余额／累计限额。
- C207：真实发送到响应的非流式 transport、整体 deadline、凭据／证书／重定向等实际控制。
- C209：真实 model／usage 分类及费用结算。
- C201/C202/C203/C211：固定真实 prepare、实际 body/envelope、生产外发记录边界、完整产品 CLI／manifest／终态协议。
- C212：获批的一次真实请求闭环，没有任何证据可由 mock 替代。

**下一最小闭环：只核对官方公共协议资料。** 先列精确官方文档目标与检索范围，单独取得联网许可，再核对 model、结构化模式、计数／输出上界、usage 分类及计费依据；不读密钥、不查认证账户或余额、不发生成请求、不做付费探测，不修改功能。

公共资料核对后再制定有依据的真实适配范围。资料无法支持可靠计数或全部计费上界时明确阻塞，不猜参数、不改冻结标准；余额与累计数值再由用户确认，实际准备读取、OUTBOUND 与 CALL 保持独立许可。

## 8. 本轮落盘与后续责任

本轮仅新建本审查 v2 并更新 INDEX 的 L1 判定导航；保留 v1 与原执行记录，不修改代码、配置、标准、ADR 或旧证据，没有命令、联网或真实数据读取动作。

`outputs/<阶段>/<run_id>/` 及追加预算事件稳定保留；同目录原子发布 .tmp 是必要例外，不迁移或清理。L1 通过只对本次限定续作有效，不自动授予后续网络、真实输入、凭据、预算或人工决定权限。

新增 ADR：本轮无。新增执行／教学交接：本轮无。用户业务决定：本轮无。后续公共资料核对仍需精确权限请求；技术证据判定继续由规划／验收方承担。
