# W2-B2 首批离线审查 v1：部分实现与最小续作 L1

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

- 阶段状态：**W2-B2 整体未验收；离线部分尚未闭合。**
- 审查性质：首批 mock 的实现／覆盖缺口审查，不是对已完成真实模型闭环作最终验收，也不将尚未实现的真实请求直接判为测试失败。
- 冻结标准：[W2-B2-v1](../W2-B2-v1.md)，C201–C212 保持，不放宽。
- 原执行记录：[w2b2-mock-0f19f9f22e2e4c98834f7c9f6b3bd586](w2b2-mock-0f19f9f22e2e4c98834f7c9f6b3bd586.md)，保留原文。
- 当前前置：W2-B1 通过，基线不重新验收。
- confirmation_actor：用户。
- confirmation_basis：用户批准本次离线审查、ADR-007、L1 交接新建及 INDEX 导航更新。
- confirmed_at：not_provided。
- recorded_at：null；recorded_at_source：not_available；recorded_at_status：unavailable。
- recorded_at_reason：本轮文件工具未提供可信精确记录时间，不执行取时命令或借用旧运行时刻。
- authorization_scope：仅以上文档动作；没有 L1 执行、真实数据读取、联网、凭据或 API 许可。

## 1. 直接读取范围与观察

项目根 `D:\MyPythonProjects\datainsight`。

证据根：`outputs/W2-B2/w2b2-mock-0f19f9f22e2e4c98834f7c9f6b3bd586/`。

直接读取或定向核对执行记录／INDEX、batch-result、test.log、source-identity、authorization-record、batch-environment、privacy-scan、fault-results，以及运行时 source-snapshots/test_w2b2.py 的相应测试与 runner。

还读取当前 explanation.py、deepseek_call.py、call_budget.py，核对真实入口是否实现，及正常 mock 子 run 的 final-status／explanation-draft。没有运行项目、独立重算摘要、审阅原始数据、读取密钥或联网；没有独立打开清单中全部文件。

工具记录：35 tests、13.351s、OK；batch-result tests_run=35、failures=0、errors=0、exit_status=0、real_provider_calls=0、missing_fault_cases=[]、uncovered_paths=[]、protection_unchanged=true、live_provider_protocol=not_verified。

上述是已保存值，不是本次重新运行。real_provider_calls=0 对应测试编排与受控网络观察；不作为全系统网络隔离证明。missing_fault_cases 仅覆盖该 runner 明确列举的 mock 矩阵，不证明未实现产品 CLI 的完整故障协议。

环境证据记录项目 venv Python 3.12.9、项目根 cwd、实际 D 盘 .cache/tmp 及对应 TEMP/TMP/TMPDIR、字节码禁用变量。

正常 mock 草稿为 structurally_valid_draft、human_review_state=pending，row_count 渲染为合成工具值，不是生产统计或新业务结论。

## 2. 可以保留、不从零重做的离线成果

- 严格响应顶层／字段／alias 校验、常见直接数值及显式越界拦截，宿主引用工具值渲染；不承诺全部自然语言语义正确。
- 合成完整 body 的 system/user/schema/envelope/aggregate 层独立白名单反向；body 不是 DeepSeek 已确认 wire schema。
- 假连接的剩余整体 deadline、读取后超时、响应体设计限额、重定向／HTTP 错误拒绝；没有真实 HTTPS 构造或发送阶段实测。
- 有理数保守向上预留、Decimal 费用求和，mock usage／费率明确为 synthetic。
- reservation／attempt_started 持久化先于 mock transport、结算／未知计费占额、消费／未结算恢复阻止重复。
- Windows 字节锁正常竞争与 scope 路径绑定；故障残留／释放阶段仍有覆盖缺口。
- 持久 synthetic 授权绑定／恢复、伪字段拒绝；不是实际人工批准的可信生产边界。
- 授权、账本、mock call 的底层发布及证据写入故障矩阵；违规 raw 响应不落盘，消费不因解释失败撤销。
- 合成全上游 approve／reject／cancel 经真实核验函数运行；不是固定真实输入的新进程 prepare。
- 新证据清单、指定源码保护、stdout/stderr/log 哨兵扫描、时间责任记录；局限明确。

## 3. C201–C212 当前状态映射

本表不把某项 mock 成功标为完整 C 项通过；离线与真实证据分开。

| 条款 | 本批已有证据 | 仍未闭合／续作位置 |
|---|---|---|
| C201 | 合成完整上游 approve/停止门 | L1补缺终态／引用、单依赖变化独立拒绝；固定真实 prepare 留后续独立读取许可 |
| C202 | synthetic完整body与层级反向 | 实际provider协议／完整body尚未核对，不可据此外发；不在L1扩建假协议 |
| C203 | synthetic持久授权、绑定变化／消费恢复 | 实际人工外发记录形成生产边界对象未实现；保留mock-only，不让构造对象直通真实入口 |
| C204 | request_explanation始终拒绝未配置／未验证 | 实际endpoint/model/HTTPS/凭据/能力待独立CHECK，非测试失败 |
| C205 | exact预留算术、mock usage类型／上界 | 真实计数依据、全部计费输出上界、费率／余额／限额待核对 |
| C206 | 持久事件／未知占额／请求次数／正常锁竞争 | L1补input/output token、金额独立边界及序号／前序／policy绑定、锁生命周期故障 |
| C207 | 假响应deadline与体积／状态控制 | 真实发送→响应整体transport未实现；mock接收助手不当完整HTTP边界 |
| C208 | 严格结构、引用、宿主渲染 | 保留明确语义局限；实际provider响应shape待适配，不称模型表现已验证 |
| C209 | mockusage结算、unknown保持、故障不成功 | 真实model/usage分类／费率与结算尚无证据 |
| C210 | 指定探针及有限读取网络观察、非法raw不落盘 | 真实服务错误／密钥／headers处理待协议实现；不宣称全敏感值认证 |
| C211 | 当前mock许可／账本／call故障矩阵 | 产品prepare/call CLI、实际manifest／引用／完整终态协议未实现，L1不填假生产证据 |
| C212 | 本次实际真实请求数为0 | 真实单请求闭环未验收；mock通过不替代，整体仍未验收 |

当前 live boundary 的固定拒绝是正确停止状态，不是授权扩大模型能力。不能删掉停止桩或先填假 policy 后请求。

## 4. 最小续作 L1：单一离线结果批次

详见 [L1 low 交接](../../handoffs/W2-B2-L1-sol61-low-v1.md)。L1只关闭两类已有可独立核验的离线缺口：

### L1-A 上游门独立反向

在新的合法完整合成 approve 链上，经真实 load_approved_plan／verify_review／恢复路径，独立构造：缺终态、缺引用文件、当前数据／规则／registry 变化。保存合法基线、实际变更对象、具体拒绝原因及调用未发送观察。

缺件创建新包时省略或精确模拟某个必需读取失败，不能整验证函数mock为失败、删除／修改已发布证据或用前一错误掩盖后一项。依赖变化是当前身份变化，不只改旧receipt绑定字段。

### L1-B 预算边界与恢复

- request_limit 保持非绑定约束，分别测试 input_limit、output_limit、amount_limit 正好允许与独立不足，真实预留/累计路径有受控工具oracle。
- 单 scope 新构造或单文件字节模拟序号缺口、previous_hash、policy_hash不符；独立失败且无新增消费／发送。
- scope锁打开／获取／正常释放／释放或关闭失败的受控生命周期测试：发送前失败为0次；发送后释放失败不得称成功或丢失原消费，不能错误要求已经发生的发送变回0。
- 故障锁不能自动删除／绕过；正常OS解锁／关闭不是删除锁证据。不新增多用户平台或复杂事务。

已有35项测试及明确故障矩阵继续回归，不重复规划或重验上游。若真实新增用例失败，先分清测试构造与功能缺陷；功能修改不在L1测试预授权内，另提最小修复，不能为减少询问默默改功能。

## 5. 为什么先 L1，再真实资料核对

L1与实际DeepSeek wire协议无关，先关可复用的入口与预算风险；不继续写大量假真实CLI／政策字段。完成后只独立申请官方协议、模型、计数／价格资料核对（不读key、不做paid probe），再制定真实适配的明确闭环。

真实余额与累计数值由人确认，准确provider/model、协议与上界不能猜。POLICY、实际准备读取、OUTBOUND与CALL依旧独立。资料门未满足则停在离线基线，不宣布整个W2-B2通过。

## 6. 合批与预授权安排

本轮已采纳 [ADR-007](../../decisions/ADR-007-batch-consolidation-and-scoped-preauthorization.md)：受控离线实现／测试／证据／结果文档可合成一个交付批次，里程碑明确范围／命令／次数可一次预授权，每批一句话通知，用户可停止。

该规范不批准L1执行。L1交接列出一项具体“测试修改＋离线运行＋结果文档”的预授权请求，执行对话须先得到批准；范围外功能修复、新依赖、真实数据、外发与人工决定仍单独申请。

W3重排采用 G3.5 独立策略决定门，E3为S4计算＋S5校验＋本地结果文档，一次交回技术验收；真实数据读取每次许可明确后才启动E3，不借合批取消校验／清洗策略门。当前没有W3实现或运行授权。

## 7. 本轮交付与下一步

本轮仅新增本审查、ADR-007、L1交接并更新INDEX；没有执行、修复功能、联网、凭据或API动作。冻结标准与旧记录／证据保持。

本轮不作W2-B2整体最终判定，阶段仍未验收。待用户业务决定：无；只需后续明确L1范围执行预授权。没有教学／面试交接或token成本改善实测。

下一步由用户手动转交L1，执行方一次完整返回离线证据及未测项，规划／验收方一次审查其闭合性；不自动进入真实调用或W3。
