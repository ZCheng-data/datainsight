# W3最终验收 v1：真实计算、三层校验与本地草稿通过

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

## 1. 当前权威判定

**W3总判定：通过。W3范围内阻塞项：无，无需补测或重跑。**

按[W3-v2 frozen](../W3-v2.md)及ADR-009，结合已通过的[限定离线验收](W3-offline-final-review-v1.md)、[G3.5真实策略验收](W3-G35-final-review-v1.md)和本次新增真实E3证据，D301–D312已在各自范围闭合。

已验收：指定真实数据版本及已批唯一方法／口径下的S4确定性计算→S5执行／口径／边界校验→证据绑定的本地报告草稿。**S6尚未完成，报告仍pending；不能称完整S4→S5→S6案例闭环或已批准发布。**

- confirmation_actor：用户。
- confirmation_basis：用户提交真实E3交回请求验收；规划／验收方只读判定W3通过；用户随后明确批准新建本记录、更新INDEX并准备独立无模型S6安排，同时登记产品v2方向。
- confirmed_at：not_provided。
- recorded_at：null；recorded_at_source：not_available；recorded_at_status：unavailable。
- recorded_at_reason：本次仅文件工具，无可信精确记录时刻；不取时、不估计或借用历史运行时间。
- authorization_scope：仅本最终验收、产品v2方向／ADR及无模型S6规划文档新建和INDEX更新；不改run／frozen／源码，不运行、不重读CSV、不自动确认S6或调用模型。
- bound_versions：W3-v2、ADR-003／005／007／008／009；离线／G3.5权威结果及真实analysis-e3-real-v1-a。

## 2. 只读核对方法与范围

项目根：`D:\MyPythonProjects\datainsight`。

- 执行结果：`docs/acceptance/results/w3-e3-real-v1-a.md`。
- 新run：`outputs/W3/analysis-e3-real-v1-a/`。
- 直接读取新run的result.json、calculation-evidence.json、validation.json、report.md、operation.json、final-status.json，定向核对bindings.json的数据版本／已批口径／身份段及目录文件集合。
- 核对已通过的真实strategy-g35-real-v1-a/strategy.json、读取契约、当前analysis.py计算／S5／报告／终态流程和固定profile_templates.py。
- 继承已验收的离线反向／故障及真实G3.5证据；不重做矩阵、不独立恢复或审计全历史。

未运行项目或测试，未读取生产CSV，未独立重算文件hash。运行保存值及绑定核验结合实际代码路径审查，不冒称独立字节计算或运行时源码快照认证。执行方自评、退出0、S5的pass字段均不单独作为通过依据。

## 3. D301–D312综合判定

| ID | 判定 | 依据与边界 |
|---|---|---|
| D301 | 通过 | G3.5实际固定真实链核验已通过；本次父／worker入口重新消费策略及上游，后置核验完成；新bindings的唯一method／plan／口径及问题／规则／注册表身份相符 |
| D302 | 通过 | 独立真实preserve_all策略及scope有效；本次strategy_ref／strategy_hash与已通过receipt相符；不把S3批准或文档许可替代策略决定 |
| D303 | 通过 | 新工具before／after源hash均匹配已批dataset_version，bytes_read相同；严格契约和固定源参数有效，不复制旧指纹 |
| D304 | 通过 | 实际固定SQL／模板hash／参数／schema、六桶计数与辅助row_count齐全；实际工具执行和S5核对覆盖；独立参考／反向继承限定离线证据 |
| D305 | 通过 | 实际局部config符合冻结值；正常worker退出0并回收；合作式deadline代码和失败／超时／配置拒绝继承R2／R3，不宣称OS硬实时或总内存隔离 |
| D306 | 通过 | S5执行层检查源及绑定、工具状态、结果类型／覆盖、实际结果字节hash与必要引用；新validation和evidence对应，故障拒绝继承离线 |
| D307 | 通过 | 固定口径与已批hash、preserve_all、实际SQL／参数／读取契约一致；无新过滤、去重、分母、日期口径；变化反向继承离线 |
| D308 | 通过 | 六桶claims为固定类型和工具value_ref／SQL引用，无业务语义扩张；无依据claim拒绝继承离线 |
| D309 | 通过 | report.md各值与result／evidence一致，固定宿主渲染且发布前回读；逐桶引用、边界说明和human_review_state=pending完整 |
| D310 | 通过 | 七项必需产物齐全，唯一final-status=success、command=execute、run_id匹配、exit_status=0及必需hash引用完整；原子发布／失败／不覆盖反向已通过 |
| D311 | 通过（既定限定范围） | 本次仅固定本地计算，源码无provider／凭据／外发路径；安全错误与受控worker证据继承；不是native／全系统网络隔离或所有敏感值审计 |
| D312 | 通过 | 用户单独许可后新增真实E3，当前源身份、计算／S5／草稿、准确命令／环境／绑定与成功终态齐全；不是旧画像复制或合成批准 |

数值与hash均引用保存工具产物。辅助row_count和桶和一致由calculate及S5确定性流程核对，验收者不心算或产生新指标。

## 4. 本次真实计算与结论证据

父进程前后源工具SHA-256均为`7095a57fbd6eb1292bec5ccde4713ac256678b8551eb478d3b5aaad89612cfb4`，bytes_read均为39876537，匹配新bindings中的已批数据版本。

worker按现有代码计算前再次hash核对；该第三份指纹未独立保存，不冒称具有第三份指纹产物，不为审计便利追加保存／重跑。

本次结果限定为：

| 固定桶 | 原始记录数 | 新工具引用 |
|---|---:|---|
| pv | 940045 | result.json#/buckets/pv |
| fav | 29353 | result.json#/buckets/fav |
| cart | 57861 | result.json#/buckets/cart |
| buy | 21315 | result.json#/buckets/buy |
| missing | 0 | result.json#/buckets/missing |
| other | 0 | result.json#/buckets/other |

所有桶绑定同run的`calculation-evidence.json#/sql/behaviours`，实际SQL／源参数／模板hash可以由工具重跑，本次不再执行。row_count／strict_row_count均为1048574，只作覆盖证据，不转为占比或转化分母。

必要产物工具身份：report.md=`a843329fb63a5ce8638a348667cef31e082673a2252022691a98e1c2c5b380bd`；result.json=`020942cc3f09d73b28d8aa4daf2ced9d92c754cafa9491c44b410b493d299861`；calculation-evidence.json=`4fc1d869fb4411db9c28ed09fdef24224d3668ce6b3cb45b3b1a2690ee89417e`；bindings.json=`59401aec63c30e65b39351d4488b2e17e7a4f00449c10aec688b2dbbb929da4f`。完整本run必要hash引用见final-status.json，不建设跨run清单。

## 5. 运行与时间语义

P-W3-E3-REAL-V1-A的执行记录分别明示本次固定策略／上游读取、CSV多次内部hash与固定计算、准确单次命令及本地写入；零重跑。不从G3.5或先前许可推定。

实际命令为现有`python -B -m datainsight.analysis execute`，strategy指向真实strategy-g35-real-v1-a，输出analysis-e3-real-v1-a；完整Git Bash命令／cwd／环境见执行结果及operation.json。Python3.12.9／DuckDB1.4.1；实际worker退出0、reaped=true、terminated=false，query_count=5不是源读取次数。

operation.recorded_at=`2026-10-14T08:18:47.481022+00:00`，final-status.completed_at=`2026-10-14T08:18:47.497719+00:00`，均运行工具时刻，不是用户确认或本记录保存时间。用户字面确认时间未给，confirmed_at=not_provided。产品usage／费用not_applicable；开发token／费用／总耗时unknown，不据时间段估算。

## 6. 通过能力与未证明事项

已证明指定真实数据版本、读取契约、唯一已批方法及口径下的行为代码原始记录数可复核，并有实际计算、三层S5、必要绑定和本地草稿。

不证明订单／支付语义、独立用户数、转化／比例、日期覆盖、总体代表性、因果／业务效果、源数据来源真实性、所有任意输入安全或协同篡改防御。技术通过也不能替代业务解释确认。

当前草稿仍pending；S6无模型路径的安排另见[W4-S6-no-model-plan-v1](../../W4-S6-no-model-plan-v1.md)。只有独立实际人工决定被有效记录后，才可称该指定案例S4→S5→S6闭环完成；不能因此宣称全部W4回归／README或产品v2完成。

历史W1生产画像／模板重跑与修复后合成收尾原位分开。本次是新增独立W3真实run，不包装为W1修复后生产重跑，不改旧失败、run或frozen。W2-B2停止续作／整体未验收／真实调用暂停及旧C205缺口保持。

本次仅正式结论落盘与导航、新方向及S6准备，不自动S6、不模型接入、不额外调用、不新建Agent／Session。
