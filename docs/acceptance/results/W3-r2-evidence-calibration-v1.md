# W3 R2证据校准记录 v1

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

- 状态：校准结论已批准；离线技术门尚未通过，W3整体未验收。
- confirmation_actor：用户。
- confirmation_basis：用户要求按必要性基线复核R2交回和D301–D312，规划方提交继承／删除／最小剩余后，用户回复“批准”。
- confirmed_at：not_provided。
- recorded_at：null；recorded_at_source：not_available；recorded_at_status：unavailable。
- recorded_at_reason：本批文件工具无可信精确时刻，不取时、不估计或复用R2工具时间。
- authorization_scope：正式校准文档／新标准／R3交接及INDEX；无功能／测试／R3运行或真实读取许可。
- bound_versions：W3-v1原frozen、ADR-008／009、W3-v2；R2-b历史证据原位保留。

## 1. 判定与实际读取范围

**原v1不能因97项用例通过而算全部完成；校准后的离线剩余只保留必要新策略终态拒绝、配置拒绝和总体deadline后置保护。其余细粒度矩阵不继续补齐。**

本轮只读核对：

- `docs/acceptance/results/w3-e3o-r2-b.md`。
- `outputs/W3/offline-w3-e3o-r2-b/case-results.json`全文分段、batch-result、operation、test.log。
- R2-a的operation／test.log，未重审其全部用例，不估算两批总耗时。
- R2-b的analysis-complete calculation-evidence／validation／final-status／operation。
- 当前`src/datainsight/analysis.py`、`tests/test_w3.py`相关函数和实际断言。
- W3-v1与已批准定位／基线，W1／W2-A／W2-B1权威验收条款映射。

未运行、未独立重算hash、未逐个读取所有子run；当前源码是本次审阅版本，不冒称有独立R2运行快照认证。工具值直接引用，不把读取结果当新执行。

R2-b工具记录：total_cases=97、passed_cases=97、halted_reason=null、status=incomplete、exit_status=1。源码runner在test_w3.py:224–231固定赋值incomplete和unmet，因此不能将该列表当作自动完整检测结果。部分case实际记录ok表示测试函数成功捕获／断言拒绝，不代表非法业务输入被接受；拒绝目标需结合函数断言和case_reason_details。

合成analysis-complete的S5三层pass及合法终态支持新离线完整路径；不代表真实许可、生产计算或S6。

## 2. D301–D312逐项必要性校准

| ID | 分类 | 继承条款／R2证据及处理 |
|---|---|---|
| D301 | 必要＋前序重复 | W2-B1 B101/B103/B104/B108；R2_actual_synthetic_verifiers、字节／缺件、reject/cancel、method/metric拒绝。保留实际接入，不重做全上游矩阵 |
| D302 | 必要；全字段身份排列属审计级 | 新G3.5不能由S2/S3代替；R2正常消费、缺决定、reject/cancel、未知策略、stale_binding。只剩策略缺终态消费拒绝与后续真实决定 |
| D303 | 必要＋前序重复 | W1-B B02/B04/B08、W2-A A02/A03；未改路径helper仍被W3调用；R2 wrong_source、URI、坏解析及源版本停止。不要补链接完整矩阵；真实hash仍必需 |
| D304 | 必要＋前序重复 | W1-B B03/B05/B06；R2新DuckDB与csv/Counter、类型／覆盖反向已有。共享数值证据，不补语义组合 |
| D305 | 必要；精确边界排列属审计级 | R2实际spawn／timeout／回收、正常配置、文档超量和受控结果超量已有；只剩实际配置不符拒绝与后置deadline修复／证明 |
| D306 | 必要，与D303/D304共用证据 | R2合法S5基线、pending／错误环境／结果hash／缺件／source_before/source_after。无需重复恢复包 |
| D307 | 必要＋前序重复 | W2-B1 B105/B108；R2过滤／重复／NULL／文本／窗口／分母／粒度及SQL／模板hash／contract拒绝；不扩排列 |
| D308 | 必要 | R2任意text、orders/payments/conversion/date/effect/ratio、value/reference拒绝；不增加自然语言穷举 |
| D309 | 必要 | R2完整execute／消费／render、no_validation、changed_report、memory_disk_mismatch；真实草稿待D312 |
| D310 | 必要；文件×底层操作属审计级 | W1-B B09、W2-A A12、W2-B1 B109/B110；R2各必需文件save失败、终态底层五类故障及double失败已有；不要笛卡尔积 |
| D311 | 必要；逐provider不存在API断言属审计级 | R2安全错误、限定网络／凭据tripwire、worker门及源码无provider调用。不是全系统隔离，不增加扫描范围报告 |
| D312 | 必要、不可继承 | 未授权／未运行，属于后续真实门，不是离线runner固定失败项；真实S4/S5／草稿仍必需 |

继承不移除运行检查，不认证未测junction、竞争路径替换、native网络或协同篡改。若旧helper／模板／上游验证实际改变，相关继承失效，另行限定影响评估。

## 3. 最小剩余与功能定位

- M1／D302：load_strategy首先消费终态；新增合法策略副本省略final-status，由真实execute入口证明未读源／未查询／未成功。这不是穷举，是阻止部分人工receipt被执行。
- M2／D305：calculate实际设置后比较观测配置；新增单条件不符拒绝，不能用S5事后engine_configuration错误代替worker发送业务聚合前检查。
- M3／D305：analysis.py:551–580在最后remaining后仍做绑定核验／落盘并success；worker超时证明不能覆盖这个后段。只在原analysis.py内补合作式阶段／成功发布前时间保护；正常、后置核验和写入跨deadline反向一起验证，资源数值不变。

所需代码变化可限定在原analysis.py／test_w3.py；不增加方法、依赖或自由SQL。删v1证明义务不能直接在原frozen完成，故新W3-v2＋ADR-009明确变更；旧frozen不改。

本次不制定OS级硬实时证明，阻塞文件调用／原子rename不保证瞬时撤回；保留“已观测过期不得success”与worker监督。若执行方发现三项之外的实际防错／权限缺陷，停下交回，不静默扩成全项目审计。

## 4. 批次、费用与权限

| 候选批次／门 | 结果 | 当前状态 |
|---|---|---|
| 文档校准 | ADR-009、W3-v2、此记录、R3交接、INDEX | 本批获批，仅文档 |
| 限定R3离线 | M1–M3及受影响最小回归，一个交回 | 精确命令／次数另批；未运行 |
| G3.5 | 真实核验链读取＋人工明确策略决定 | 独立许可，未授权 |
| E3-REAL | 一次真实计算／S5／草稿、技术验收 | 独立真实读取授权，未运行 |
| S6 | 人工业务解释确认 | W3之后独立，不自动外发 |

W3产品模型费用not_applicable。开发辅助token／金额及补齐总耗时unknown；现有operation只有工具记录时刻，没有足以估算成本／总耗时的证据；180秒是设计限额而非预测。不给没有依据的金额、时长或效率提升比例。

限定R3交接：[W3-E3-OFFLINE-R3-sol61-low-v1](../../handoffs/W3-E3-OFFLINE-R3-sol61-low-v1.md)。用户手动转交，low先申请精确本地合批许可。不存在默认真实读取或人工批准；不启动Agent／Session。
