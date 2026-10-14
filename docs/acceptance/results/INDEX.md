# 验收结果入口

本索引仅导航已有结果与证据，不是新运行、独立复验或执行授权。目录保存规则见 [ADR-003](../../decisions/ADR-003-directory-and-evidence-layout.md)。

## W4-B回归后续范围：保留待办，按相关变更触发

用户已确认[W4-B回归范围决定v1](W4-B-regression-scope-decision-v1.md)：独立冻结回归集／可复用入口**保留待办，首次相关功能变更时合批建设**；当前不新增独立回归批次、不重跑当前案例，不称原W4-B评测集已完成。仅文档变更不触发计算回归。

后续只建设受控新batch入口、必要正常基线和实际变更影响路径的反向，交回真实结果及未测范围；既有阶段证据在未改范围内继承，不要求全历史／穷举审计。准确文件／命令／次数另批，当前没有功能、运行或产品v2许可。

本次记录依据用户“确认采纳建议”，仅新建范围决定并同步本导航；confirmed_at=not_provided，recorded_at=null／unavailable（文件工具无可信精确时刻，不取时或估计）。README、frozen、旧结果／run、源码／测试不改；未运行、读CSV或启动模型／网络。原W3、限定S6及README通过保持。

## 当前W4-B交付文档权威判定：通过

[W4-B文档最终验收v1](W4-B-doc-final-review-v1.md)：**J401–J408全部通过，文档范围内阻塞项无，无需补运行／回归**。[根README](../../../README.md)的定位／状态、固定案例阅读链、职责、环境／实际CLI、权限／限制及v2方向准确，核心链接可定位；验收基于实际静态核对，不是执行方自评。

通过仅为交付文档子闭环，不代表新增全量回归、新机器复现、全部W4／产品v2或LLM Agent完成。已有指定案例S4→S5→S6闭环完成状态保持；原W4-B评测／回归方向、F-PATH及产品v2仍待后续范围决定，不自动实施或发布。

本次P-W4B-DOC-FINAL依据用户对新建最终记录／更新INDEX建议回复“继续下一步”，仅正式文档与导航；confirmed_at=not_provided，recorded_at=null／unavailable（文件工具无可信精确时刻，不取时或估计）。README、旧交回、标准／源码／run不改，无命令、CSV读取、模型／外发、Git或新Agent／Session动作。

## W4-B交付文档执行记录（历史待high状态）

[根README](../../../README.md)及[执行交回w4-b-doc-v1-a](w4-b-doc-v1-a.md)已在P-W4B-README-DOC-V1准确许可下新建，J401–J408执行侧静态核对完成；未验收，待high文档验收。本批零命令运行、无真实数据工具核验／功能修改；不代表全量回归、全部W4、新环境验证或产品v2完成。旧判定及run保持。

## 当前无模型S6权威判定：通过，指定案例闭环完成

[W4-S6最终验收v1](W4-S6-final-review-v1.md)：**H601–H606全部通过，范围内阻塞项无，无需补核验或重跑**。用户已实际审阅固定analysis-e3-real-v1-a/report.md并明确接受限定解释，必要字节核验相符、独立记录绑定与ADR-005时间口径完整。

与[W3最终验收](W3-final-review-v1.md)共同确认**该指定真实案例S4→S5→S6闭环完成**。仅接受已批版本／口径下的行为代码原始记录数与限制；不是全部W4／产品v2完成、产品S6自动化或业务效果证明，外发未授权。

原run/report的pending保持生成时语义，后续独立审核文档及本权威结论表示当前人审状态，不回填旧产物。下方“待high／S6尚未完成／实际决定未给出”均保留此前记录语境，当前限定状态以本最终验收为准。

本次P-S6-FINAL-DOC依据用户对新建最终验收和更新INDEX建议回复“继续下一步”，仅正式文档与导航；confirmed_at=not_provided，recorded_at=null／unavailable（文件工具无可信精确时刻，不取时或估计）。无旧记录／run／标准／源码变化，无运行、CSV读取、模型／网络或外发，未启动产品v2。

## 无模型S6人工审核执行记录（历史待high状态）

[W4-S6-human-review-v1](W4-S6-human-review-v1.md)：用户明确本地审阅固定report后选择approve_limited_interpretation，接受限定解释及全部限制；P-S6-LOCAL-RECORD-V1获批单次字节核验退出0，必要锚相符。决定已独立记录，待high按H601–H606核对，不是执行者自封S6／案例闭环通过。scope=S6_local_limited_interpretation_only，external_release=not_authorized；旧run及报告pending不改。下方“实际决定尚未给出”保留原安排语境，当前真实决定见本新记录。

## 当前W3权威判定：通过；S6独立待确认

[W3最终验收v1](W3-final-review-v1.md)：**按W3-v2总判定通过，阻塞项无，无需补测／重跑**。已通过限定离线、G3.5真实策略及新增真实E3，D301–D312在各自范围闭合；本次真实源前后身份匹配已批版本、固定方法计算／S5／本地草稿及合法终态齐全。不是执行者自评、退出0或pass字段单独认证。

**S6尚未完成**，report仍pending，完整案例S4→S5→S6须独立人工业务解释确认；W3通过不是报告发布或业务效果认证。用户随后回复“采纳建议确认批准下一步”，无模型[S6方案](../../W4-S6-no-model-plan-v1.md)已accepted、[H601–H606最小标准](../W4-S6-no-model-v1.md)已frozen，条款未变；实际业务approve尚未给出。

[无模型S6限定low记录交接](../../handoffs/W4-S6-no-model-sol61-low-v1.md)已新建：一次固定已验收包hash消费核验和独立人工决定文档，不新增产品S6代码／CLI，不重算、不改run。准确一次命令／读取／新记录写入许可及用户实际接受／拒绝／取消仍须明确，不能从安排冻结推定。

本次P-S6-DOC-F仅保存方案／标准确认冻结、新建交接并同步本导航；confirmed_at=not_provided，recorded_at=null／unavailable（仅文件工具，无可信精确时刻，不取时或估计）。未运行、读取CSV、调用模型或生成真实审核记录，旧报告pending保持，不自动完成S6。

## 产品v2正式方向（登记，不实施）

[ADR-010](../../decisions/ADR-010-product-v2-draft-channels-and-current-no-model-S6.md) · [产品v2方向登记](../../project-v2-directions-v1.md)：执行后解释草稿归v2的W4／S6可选部件；入库前方法候选归v2 W5-B方法发布；入口翻译归v2 W5-A／S2前意图草稿。新增执行后模型角色例外仅限未来方向，专项契约／模型标准未冻结、未实现／验收，无调用许可；三项不阻塞当前无模型S6。

产品v2与W3-v2标准修订号不同。W2-B2仍停止续作、整体未验收／真实调用暂停，旧C205未满足；未来付费／协议／外发另版及独立授权，不用新方向放行旧条款。固定问题路径缺陷F-PATH保持登记，不默默删除。

本批依据用户明确批准W3最终记录／INDEX／无模型S6安排与v2方向登记，仅正式文档；confirmed_at=not_provided，recorded_at=null／unavailable（文件工具无可信精确时刻，不取时或估计）。未修改run、代码、配置、旧标准或旧结果，未运行、CSV读取、外发或模型调用；未自动确认S6。下方“W3整体未验收／真实未运行／待high”的段落均保留历史语境，当前W3状态以新权威记录为准。

## W3 E3-REAL执行记录（历史待high状态）

[w3-e3-real-v1-a](w3-e3-real-v1-a.md)：用户明确P-W3-E3-REAL-V1-A当次核验链／固定CSV读取及单次命令／写入许可后，execute退出0；新实测前后源hash匹配已批版本，S5三层pass，本地pending草稿及唯一success终态已生成。待high按W3-v2判定，不是执行者自封W3通过。无S6／外发，旧证据保持。下方“真实运行尚待完成”的旧段落保留其当时语境，本次新执行见该结果记录。

## W3 G3.5当前权威判定：通过

[W3-G35-final-review-v1](W3-G35-final-review-v1.md)：**真实策略记录通过，本门阻塞项无**。用户明确preserve_all、actor=user映射及准确许可分别记录；固定S2／S3／唯一方法／口径及版本绑定相符，四文件齐全、合法唯一终态。此策略仅scope=S3.5_preserve_all_only，不授权当前生产CSV读取／计算；未测当前源身份。

**W3整体仍未验收**：当前真实源hash及D312真实计算／三层S5／草稿尚待完成，S6随后独立。历史“G3.5尚未完成／待high核对”保留其记录语境，当前本门状态以该权威验收为准，不改旧产物／结果。

[E3-REAL自包含low交接](../../handoffs/W3-E3-REAL-sol61-low-v1.md)已准备：仅现有单次execute、固定CSV／策略／上游白名单、真实计算／校验／本地草稿。准确本次真实读取、命令及写入许可仍待取得；不因本门通过自动运行或再次选择策略。

本批P-W3-G35-FINAL-AND-E3-DOC依据用户对权威记录／INDEX／交接文档请求回复“批准下一步”，仅正式文档新建与导航；confirmed_at=not_provided，recorded_at=null／unavailable（文件工具无可信精确时刻，不取时或估计）。无标准／源码／配置／旧证据修改，无运行、CSV读取、网络／密钥／API，不授权E3-REAL或S6。

## W3 G3.5真实策略执行记录（历史待high状态）

[w3-g35-real-v1-a](w3-g35-real-v1-a.md)：在用户明确A–F真实历史证据读取、preserve_all策略决定及单次命令／写入许可下，strategy入口退出0，独立策略run记录完成；待high核对，不是执行者验收通过。scope=S3.5_preserve_all_only，actor=user，confirmed_at=not_provided；工具recorded_at见run。未读取生产CSV／计算当前源hash，无E3-REAL／S6／外发许可。旧结果保持。

## 当前方向与W2状态收尾

最新方向依据：[ADR-008](../../decisions/ADR-008-closed-intent-evidence-baseline-and-W3-boundary.md) · [项目定位／必要证据基线／后续方向](../../project-position-and-evidence-baseline-v1.md)。定位为面向封闭分析意图、提供可复核结论与证据的受控分析系统；W3零模型，解除对真实模型解释的依赖，独立S6人工门保持。

[W2最终状态记录v1](W2-final-state-v1.md)：**离线基线通过、阶段停止续作、W2-B2整体未验收／真实调用暂停**。这是方向收尾，不是全部W2验收通过；旧frozen、C205缺口、C212未完成及历史证据保持，不再自动继续计数查证、tokenizer或真实解释接入。

W3详细安排已获用户随后回复“确认”：[方案v1（accepted）](../../W3-plan-v1.md) · [验收标准v1（frozen）](../W3-v1.md) · [自包含low交接v1（accepted，待执行授权）](../../handoffs/W3-sol61-low-v1.md)。D301–D312、接口、资源设计和命令契约形式内容未变。唯一方法`M-BEHAVIOUR-RECORDS`的S4计算＋S5三层校验＋本地报告草稿是必需证明场；未实现／未运行／未验收，不授权执行或真实读取。完整案例闭环还需随后独立S6。

P-W3-DOC-F仅保存上述确认／冻结状态及本导航；confirmed_at=not_provided，recorded_at=null／unavailable（本次文件工具无可信精确时刻）。低档离线实现／测试的精确预授权仍待取得；真实读取、G3.5及S6人工决定、网络／外发／付费均未授权。旧标准、结果和运行证据保持。

本次维护依据：用户一次确认八项边界并批准合批文档落盘。confirmed_at=not_provided；recorded_at=null／unavailable（文件工具未提供可信精确时刻，不取时或估计）。技术判定由规划／验收方负责，用户不为未验证条款认证。仅正式文档与导航；无功能、配置、旧标准／证据变化，无项目命令、真实数据／摘要工具读取、联网／密钥／API。

## W3当前证据校准（后续以v2为准）

用户在R2只读复核后批准必要性校准：[ADR-009](../../decisions/ADR-009-W3-evidence-calibration-and-minimal-offline-closure.md) · [W3-v2（frozen）](../W3-v2.md) · [R2校准结果](W3-r2-evidence-calibration-v1.md)。v1及旧结果原位保留；W3实际离线实现／证据已经产生，不能继续把原冻结时的“未实现／未运行”读作当前状态。

R2-b记录97项通过、incomplete／退出码1，原值不改；runner固定unmet不单独决定验收。继承前序和R2有效证据，停止重复上游／链接／精确字节边界／逐文件底层故障／逐provider不存在调用矩阵。当前离线仍剩新策略缺终态拒绝、配置不符拒绝和总体deadline后置保护；**离线技术门尚未通过，W3整体未验收**。

[限定R3自包含交接](../../handoffs/W3-E3-OFFLINE-R3-sol61-low-v1.md)：仅上述最小缺口与受影响回归。精确命令／batch／一次运行候选尚未预授权，不能复用R2次数或自动补齐；G3.5真实读取／人工决定、E3-REAL、S6、网络／付费均独立且未授权。

本次P-W3-CAL-DOC仅新增校准正式文档及本导航；confirmed_at=not_provided，recorded_at=null／unavailable（文件工具无可信精确时刻，不取时或估计）。无源码／测试／配置／旧frozen／R2产物变更，无命令、数据工具读取、网络／密钥／API。

## W3限定离线当前权威判定：通过

[W3限定离线最终验收v1](W3-offline-final-review-v1.md)：**通过，限定离线范围阻塞项无，无需新增离线补齐批次**。依据W3-v2／ADR-009继承前序与R2证据，R3的策略缺终态、配置不符、后置deadline和受影响最小回归已闭合；不根据用例数量或runner状态单独认证。

**W3整体仍未验收**：真实固定核验链、G3.5策略决定、当前真实源hash、D312真实E3及随后独立S6尚未完成。本通过不授权这些门。上方校准时“离线尚未通过／R3未预授权”与下方执行者“待high判定”均为此前记录语境，当前限定判定以本最终验收为准；不追改旧标准、执行文档或run。

本次P-W3-OFFLINE-FINAL-DOC依据用户对新建验收记录及更新INDEX回复“批准下一步”，仅新增正式结论与导航；confirmed_at=not_provided，recorded_at=null／unavailable（文件工具无可信精确时刻，不取时或估计）。无功能／标准／配置／旧证据变化，无运行、真实数据工具读取、网络／密钥／API；不自动启动G3.5、E3-REAL或S6。

## 当前权威判定

| 阶段 | 当前状态 | 权威来源 |
|---|---|---|
| W1（S0＋S1） | 通过 | [W1 最终验收与交接](W1-final-acceptance-and-handoff.md) |
| W2-A | 通过；R1–R4 已关闭前次阻塞项，标准保持 frozen；仅本地固定输入的离线诊断与 S2 记录，不授权启动 S3/W2-B | [最终验收记录 v2](W2-A-final-review-v2.md) · [历史判定 v1](W2-A-final-review-v1.md) · [原执行结果](s2-accept-3178ad8b677e49edb91de623be0c3905.md) · [补测结果](r1r4-ee1dc6e19ab84b21b23fc03a0e7f5886.md) · [冻结标准](../W2-A-v1.md) |
| W2-B1 | 通过；T1–T2 已关闭前次阻塞，标准保持 frozen；仅确定性候选与本地 S3 口径审核，不授权 W2-B2/S4 | [最终验收记录 v2](W2-B1-final-review-v2.md) · [历史判定 v1](W2-B1-final-review-v1.md) · [原执行结果](w2b1-review-219e79901d08444bab62c6e61f6e2211.md) · [补测结果](w2b1-t1t2-8811bf4a7b404d3cac7222b32ff6a021.md) · [冻结标准](../W2-B1-v1.md) |

W1 历史执行文件中的“未验收，待验收者判定”是当时执行记录，保留原文；后续综合判定以 W1 最终验收文件为准。本索引不追改历史状态，不重新启动 B01–B09。

## W2-B2 离线进展（L1 通过，整体未验收）

当前离线审查：[v2：L1 通过](W2-B2-offline-review-v2.md)。L1 指定的上游门独立反向、预算边界／事件链／锁生命周期缺口已闭合；完整实际 provider 协议、配置、产品 prepare/call 与 C212 仍未完成，**W2-B2 整体未验收**，不授权联网、凭据、真实数据读取、外发或付费。

历史入口：[离线审查 v1](W2-B2-offline-review-v1.md) · [首批执行记录](w2b2-mock-0f19f9f22e2e4c98834f7c9f6b3bd586.md) · [首批 mock 证据](../../../outputs/W2-B2/w2b2-mock-0f19f9f22e2e4c98834f7c9f6b3bd586/) · [冻结标准](../W2-B2-v1.md)。保留当时离线未闭合的记录，不回写旧结论，不把 mock 返回 0 当整体通过。

L1 交接与实际执行：[low 交接](../../handoffs/W2-B2-L1-sol61-low-v1.md) · [执行结果](w2b2-l1-b892af4b267a4586bf1c25f4df86cdf5.md) · [新证据](../../../outputs/W2-B2/w2b2-l1-b892af4b267a4586bf1c25f4df86cdf5/) · [一次技术审查 v2](W2-B2-offline-review-v2.md)。执行记录保留其“待验收”状态；当前 L1 通过以直接证据及断言审查为准，而非 batch-status 单独证明。授权记录通用编号瑕疵见 v2，不追改或重跑旧证据。

官方公共资料核对：[W2-B2-provider-check-v1](W2-B2-provider-check-v1.md)。已在 P-B2-CHECK-PUBLIC 下读取同站公开协议／model／JSON／token及计费文档；没有账户／余额／密钥／生成请求。实际 body 与 mock 不同，完整输入计数、费用适用及真实配置仍待核验，不能据文档直接付费。

tokenizer 当前限定判定：[静态审查 v2：补证通过](W2-B2-tokenizer-static-review-v2.md)。完整小型配置／模板／demo及有限结构已补齐，**C205仍未满足**：当前模型适用、服务端包装与可靠完整输入上界未建立。static通过不等于计数运行或付费门通过，整体仍未验收。

历史下载与审查：[原执行结果](tokenizer-check-9d62e031a4b84ef59cb776e043c13821.md) · [原包及证据](../../../outputs/W2-B2/tokenizer-check-9d62e031a4b84ef59cb776e043c13821/) · [v1不通过记录](W2-B2-tokenizer-static-review-v1.md)。保留当时未充分提取的状态，不回填旧run或旧结论。

已完成的原包离线补证：[low交接](../../handoffs/W2-B2-tokenizer-static-supplement-sol61-low-v1.md) · [执行结果](tokenizer-static-supplement-7f9c82d4a6034b71b18d0d12e609c5ae.md) · [新证据](../../../outputs/W2-B2/tokenizer-static-supplement-7f9c82d4a6034b71b18d0d12e609c5ae/) · [一次静态技术审查v2](W2-B2-tokenizer-static-review-v2.md)。原记录的“待审”文字保持；当前判定来自直接原文及矩阵审查，未运行tokenizer、安装或重新下载。

官方计数依据核对已收尾：[W2-B2-token-count-evidence-check-v1](W2-B2-token-count-evidence-check-v1.md)。在授权并实际读取的页面中未找到足以闭合当前模型／完整服务输入计数的保证，C205保持阻塞；不是宣称“官方不存在”。不继续反复查证、安装tokenizer或付费probe。

下一步只讨论可证明的保守预算候选（如明确context ceiling预留），或需明示新版本／ADR的风险口径安排；当前没有上界证明、成本计算、接口变更或policy批准。Responses输出上限的正面文档事实与输入缺口分开记录，不自动换接口。

工作流规范：[ADR-007 合批与范围预授权／W3重排](../../decisions/ADR-007-batch-consolidation-and-scoped-preauthorization.md)。受控本地写入可在明确许可内合批，真实读取／外发／人工门仍独立；不改任何冻结标准、旧权限或证据，不授予W3执行许可。

## 生产计算与修复后收尾：分开引用

| 证据性质 | 结果文档 | 稳定证据位置 | 能证明／不能证明 |
|---|---|---|---|
| 最后生产画像与模板重跑（修复前协议） | [W1-B 生产批次索引](final-20261009T061339601505Z.md) | [生产批次](../../../outputs/W1-B/final-20261009T061339601505Z/) | 历史生产计算与重跑；没有新协议 final-status，不能声称修复后完整生产 CLI 实测 |
| 修复后合成 CLI 收尾与回归 | [B09 收尾修复记录](b09-finalization-20261009T063948192695Z.md) | [合成收尾批次](../../../outputs/W1-B/b09-finalization-20261009T063948192695Z/) | 当前收尾协议的正常／故障验证；没有再次运行生产画像或生产重跑 |
| 综合最终验收 | [W1 最终验收与交接](W1-final-acceptance-and-handoff.md) | 引用上述两类证据及其他 W1 证据 | W1 总判定通过；不把两类证据拼成不存在的一次生产运行 |

## W2-A 验收结论与执行证据

当前最终判定：[W2-A 最终验收记录 v2](W2-A-final-review-v2.md)，**通过**；R1–R4 已关闭 A02、A03、A12 与 A13–A15 的前次证据缺口，结合原已通过项完成冻结范围验收。能力与未测边界见 v2，不授权自动进入 S3/W2-B。

历史判定：[W2-A 最终验收记录 v1](W2-A-final-review-v1.md)，保留当时“不通过”及补证依据；不改原文、不抹掉历史，不把后续通过追写到旧运行。

统一执行记录：[S2 accept 批次结果](s2-accept-3178ad8b677e49edb91de623be0c3905.md)，保留原“未验收，待规划／验收者判定”文字。测试成功、诊断成功与人工 accept 不等于 A01–A15 最终通过；执行记录与最终验收分别保存。

| 性质 | 证据位置 | 边界 |
|---|---|---|
| 合成测试及两项 W1 接口回归 | [syn 批次](../../../outputs/W2-A/syn-3178ad8b677e49edb91de623be0c3905/) | 不称 W1 全回归；不是生产画像计算 |
| 固定历史生产画像输入诊断 | [历史画像诊断](../../../outputs/W2-A/local-syn-3178ad8b677e49edb91de623be0c3905/) | source_kind=historical_production；目录含 syn 不代表合成输入；未读当前 CSV |
| 真实用户 accept 独立记录 | [S2 决定](../../../outputs/W2-A/s2-accept-3178ad8b677e49edb91de623be0c3905/) | acceptance_scope=S2_only，不授权 S3/W2-B |

### R1–R4 补测（已复验通过）

[补测执行记录 r1r4-ee1dc6e19ab84b21b23fc03a0e7f5886](r1r4-ee1dc6e19ab84b21b23fc03a0e7f5886.md) · [新证据目录](../../../outputs/W2-A/r1r4-ee1dc6e19ab84b21b23fc03a0e7f5886/) · [复验判定 v2](W2-A-final-review-v2.md)。执行记录保留其当时“待复验”状态；当前阶段通过依据是 v2 的直接证据及断言审查，而非 runner 返回 0 单独证明。该批只有合成补测，不替代历史画像诊断或真实 accept，不授权后续阶段动作。

## W2-B1 最终判定与执行证据

当前最终判定：[W2-B1-final-review-v2](W2-B1-final-review-v2.md)，**通过，阻塞项无**；T1–T2 关闭 B103/B108/B109 的前次缺口，结合原已通过项及完整回归使 B112 闭合。能力与未测边界见 v2，不授权自动进入 W2-B2、清洗或 S4。

历史判定：[W2-B1-final-review-v1](W2-B1-final-review-v1.md)，保留当时“不通过”与 T1–T2 补测依据，不追改原文，不把后续通过回填旧运行。

[候选与独立 S3 approve 执行记录](w2b1-review-219e79901d08444bab62c6e61f6e2211.md) 保留原“待验收”状态；[冻结标准](../W2-B1-v1.md) 不改。业务 approve 不等于技术验收通过，不授权清洗、S4 或 W2-B2。

技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。新增记录／模板责任与时间口径见 [ADR-005](../../decisions/ADR-005-approval-responsibility-and-confirmation-time.md)，不回写旧记录或改变补测范围。

| 性质 | 证据目录 |
|---|---|
| 首次合成失败（保留） | [失败批次](../../../outputs/W2-B1/w2b1-syn-4c27236f9fcf4f88bf5ab0e4d969b80d/) |
| 测试命名修正后合成成功 | [成功测试批次](../../../outputs/W2-B1/w2b1-syn-60e61a5474ca4536bca9a5fff29487e4/) |
| 固定真实 S2 核验与候选 | [候选](../../../outputs/W2-B1/w2b1-candidates-1f9fa1e612fa4c19b48181111a3a35d6/) · [独立观察](../../../outputs/W2-B1/w2b1-local-observation-1f9fa1e612fa4c19b48181111a3a35d6/) |
| 用户真实选择／口径确认的独立 S3 approve | [审核](../../../outputs/W2-B1/w2b1-review-219e79901d08444bab62c6e61f6e2211/) |

### T1–T2 补测（已复验通过）

[补测执行结果](w2b1-t1t2-8811bf4a7b404d3cac7222b32ff6a021.md) · [新证据目录](../../../outputs/W2-B1/w2b1-t1t2-8811bf4a7b404d3cac7222b32ff6a021/) · [复验判定 v2](W2-B1-final-review-v2.md)。执行记录保留当时“待复验”状态；当前通过来自 v2 对直接报告及测试断言的技术判定，不由退出 0 单独证明。补测只含合成依赖变化／已有输出保护，不替代原真实候选与 S3 approve，旧不通过与所有历史证据保持，不授予下一阶段动作权限。

## 历史结果导航（保留原文与引用位置）

| 阶段／性质 | 结果文档 | 证据目录 |
|---|---|---|
| W1-A 初始执行记录 | [20261008T123312951300Z](20261008T123312951300Z.md) | [原 run](../../../outputs/W1-A/20261008T123312951300Z/) |
| W1-A 修复运行记录 | [20261008T125437808302Z](20261008T125437808302Z.md) | [修复 run](../../../outputs/W1-A/20261008T125437808302Z/) |
| W1-A 修复证据补充（非新生产演示） | [证据补充](20261008T125437808302Z-evidence-supplement.md) | [同一历史 run](../../../outputs/W1-A/20261008T125437808302Z/) |
| W1-B RECORD 合成测试失败；真实校验未运行 | [record-20261008T140118794797Z](record-20261008T140118794797Z.md) | [失败 run](../../../outputs/W1-B/record-20261008T140118794797Z/) |
| W1-B RECORD 修复与离线校验记录 | [record-20261009T043521036513Z](record-20261009T043521036513Z.md) | [后续校验 run](../../../outputs/W1-B/record-20261009T043521036513Z/) |

安装、严格读取、独立对照、入口／结果边界、语义、证据修复等未单独列出结果文档的批次，从 [W1 最终验收表](W1-final-acceptance-and-handoff.md) 进入；不为补齐索引虚构结果文件。

## 维护规则

- 新阶段运行结果新增 `docs/acceptance/results/<run_id>.md`，并在获批的文档动作中更新本 INDEX。
- 记录阶段、证据性质、当前判定来源与未测能力，不把执行者记录当最终验收结论。
- 冻结标准只在 `docs/acceptance/` 保存；运行结果不得写回标准。
- `outputs/<阶段>/<run_id>/` 及已发布证据不得移动、删除或覆盖；失效链接报告原因，不通过搬移旧证据修补。
- run 内用于同目录原子发布的 `.tmp` 是必要例外，不是遗漏或待清理项；残留临时文件不代表已发布成功终态。
- 新一般临时产物只放 `outputs/_scratch/` 或 `.cache/tmp/`；对话推理、讨论与临时文字草稿不落盘。

本次依据用户批准P-B2-COUNT-CHECK，只读取指定官方公开页面及直接相关同站链接，新建计数依据报告与本导航；C205仍阻塞、W2-B2整体未验收。confirmation_actor=用户，confirmed_at=not_provided；recorded_at=2026-10-13T05:20:50.539Z（浏览器工具本地Date.toISOString，资料观察时钟，不是用户／provider或精确文件落盘时间）。没有搜索引擎、外域／账户访问、支持联系、包下载／安装、项目命令、密钥或API请求；不授予预算／接口变更、policy或真实调用，不改标准与旧证据。

## W3离线执行 w3-e3o-v1-a

[w3-e3o-v1-a](w3-e3o-v1-a.md)：不完整；未验收，待规划／验收方判定。真实门未启动。

## W3离线执行 w3-e3o-v1-b

[w3-e3o-v1-b](w3-e3o-v1-b.md)：不完整；未验收，待规划／验收方判定。真实门未启动。

## W3离线执行 w3-e3o-r1-a

[w3-e3o-r1-a](w3-e3o-r1-a.md)：不完整；未验收，待规划／验收方判定。真实门未启动。

## W3离线执行 w3-e3o-r2-a

[w3-e3o-r2-a](w3-e3o-r2-a.md)：不完整；未验收，待规划／验收方判定。真实门未启动。

## W3离线执行 w3-e3o-r2-b

[w3-e3o-r2-b](w3-e3o-r2-b.md)：不完整；未验收，待规划／验收方判定。真实门未启动。

## W3 R3离线执行

[w3-e3o-r3-a](w3-e3o-r3-a.md)：passed（仅本批合成测试）；未验收，待high判定；真实门未启动。
