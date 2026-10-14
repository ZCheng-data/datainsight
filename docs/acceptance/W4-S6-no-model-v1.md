# W4／S6无模型人工业务解释确认：最小验收标准 v1（已冻结）

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

- 状态：frozen；H601–H606及具体记录安排已获用户确认，条款未变；实际业务决定尚未给出。
- confirmation_actor：用户。
- confirmation_basis：用户先批准无模型S6准备，随后对“一次确认S6方案／最小标准的具体安排，再审阅固定报告并明确选择；安排确认不等于报告批准”的建议回复“采纳建议确认批准下一步”。
- confirmed_at：not_provided。
- recorded_at：null；recorded_at_source：not_available；recorded_at_status：unavailable。
- recorded_at_reason：本次冻结状态保存仅文件工具，无可信精确时刻，不执行取时或估计。
- authorization_scope：P-S6-DOC-F仅方案／本标准确认冻结状态、限定记录交接新建及INDEX同步；无S6真实决定、核验命令／数据工具读取或发布权限。
- 对应：[无模型方案](../W4-S6-no-model-plan-v1.md)、[ADR-010](../decisions/ADR-010-product-v2-draft-channels-and-current-no-model-S6.md)、ADR-003／005／007／008／009。
- 前置：[W3最终验收通过](results/W3-final-review-v1.md)，固定真实analysis-e3-real-v1-a报告；不重算、不模型接入。

## 1. 一个最小人工闭环

固定已验收报告／证据身份核对 → 用户明确接受限定解释或reject/cancel → 独立正式文档绑定决定和时间／scope → 规划方核对记录 → 只有有效approve才宣称指定案例S4→S5→S6完成。

这是文档化人工业务审核，不是已实现产品S6引擎／自动发布。范围只本案例，不包含W4回归／README、受控问题入口、新方法、模型部件或业务效果。

## 2. 必需项（不加审计矩阵）

| ID | 客观要求 | 主要反向判定 | 最小证据 |
|---|---|---|---|
| H601 技术前置与固定对象 | 指向W3已验收analysis-e3-real-v1-a/report.md，合法终态与S5通过，当前必要字节hash与已验收锚相符 | 错run、缺success／S5、报告／必要结果被改，不登记有效确认，不重跑 | W3权威结果、固定run必要终态／报告／结果／evidence身份；一次获批必要核验，非全历史审计 |
| H602 真实人工决定 | 用户在审阅固定对象及限制后明确approve_limited_interpretation、reject或cancel；actor／确认依据可核对 | 只有准备／冻结／读取许可、W3通过或“继续”不得代签approve；reject/cancel不闭合 | 必要用户决定内容／确认来源，不保存全部聊天或推理；不伪造身份认证 |
| H603 解释边界 | 只接受指定版本下行为代码原始记录数和限制；无模型计算、新指标、订单／支付／比例／转化／日期／因果／效果推断 | 人审请求扩大结论不能沿用现报告批准；先停下另作范围变更 | 固定report及被接受限制，数值引用工具，不在审核文档心算或估计业务效果 |
| H604 独立记录与绑定 | 新审核文档保存decision、报告／数据／问题／规则／方法／口径／策略及结果必要身份引用和scope；不修改旧run pending | 无绑定、错版本、已有目标、记录写失败不成功；不回填或覆盖 | 独立W4-S6-human-review-v1.md完整记录及INDEX导航；身份可引用既有包，无全产物清单 |
| H605 责任／时间与权限 | ADR-005责任清楚，confirmed_at用户字面值或not_provided，工具recorded_at独立；scope=S6_local_limited_interpretation_only，external_release=not_authorized | 不以工具时间冒充用户时间；批准解释不自动授权网络、模型、行动或CSV读取 | 决定／授权字段与真实工具来源，缺时刻如实unavailable；零模型／无外发安排 |
| H606 完成状态准确 | high核对后有效approve才S6通过、案例闭环完成；reject/cancel或必要证据不足停止；W3技术通过保持 | 草稿存在、技术pass、文档准备、v2方向登记不能称S6完成；不宣传完整W4或产品v2完成 | S6决定记录和后续high判定；无真实确认则未完成 |

反向是明确拒绝规则，不强迫为每项制造运行fixture／故障／恢复矩阵；沿用W3已验收数值、终态和安全反向，不再跑生产CSV或测试suite。

## 3. 记录与权限纪律

本版H601–H606及记录安排已获确认并冻结，内容未变；安排确认不等于真实业务approve，不自动生成审核记录。

记录前准确授权固定真实聚合包的必要读取／一次字节核验、新文档和导航；不得调用execute、上游全链重建、SQL、模型或网络。记录交接已列现有函数的一次准确命令候选，仍须另获许可；本标准冻结未授命令。

用户可以同一明确回复分别给读取／核验许可、业务决定及文档写入许可，但三项作用分开；缺一等待。拒绝／取消如需保存，亦仅记录真实选择，不填批准状态。

审核记录后由high只读判定，不按记录方自评或文件存在直接通过。旧W3 report／终态／receipt保持pending和原语义，独立后续记录表达S6决定，不改frozen或run。当前没有S6功能JSON或原子发布CLI，不编造运行证据。

结果放`docs/acceptance/results/W4-S6-human-review-v1.md`，对话40行以内。后续模型解释草稿采用专门模型W4／S6标准另版／新契约；本无模型标准不能放行provider、外发或旧C205。
