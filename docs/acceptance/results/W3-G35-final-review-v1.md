# W3 G3.5真实策略记录最终验收 v1

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

## 1. 当前权威判定

**G3.5真实策略记录：通过。本门阻塞项：无。**

用户明确选择的preserve_all已独立记录，固定真实S2／S3及唯一方法／口径通过现有入口核验后绑定保存；不需要补跑消费核验或离线矩阵。该记录形成S3.5策略资格，**不授权生产CSV读取或计算**。

W3限定离线技术验收通过保持；W3整体仍未验收，D303当前真实源身份与D312真实计算／S5／草稿未完成。S6随后独立，不由本记录或pending状态推定完成。

- confirmation_actor：用户。
- confirmation_basis：用户提交G3.5交回请求验收；规划／验收方只读判定通过并提出“新建权威验收记录、更新INDEX、准备E3-REAL交接”的文档批次，用户回复“批准下一步”。
- confirmed_at：not_provided。
- recorded_at：null；recorded_at_source：not_available；recorded_at_status：unavailable。
- recorded_at_reason：本次仅文件工具，未取得可信精确记录时刻；不执行取时、不估计、不以历史运行时间代填。
- authorization_scope：P-W3-G35-FINAL-AND-E3-DOC仅本记录、E3-REAL交接新建及INDEX更新；不修改标准／代码／配置／旧证据，不运行、不读取生产CSV，不授权E3-REAL／S6／外发。
- bound_versions：W3-v2 frozen、ADR-003／005／007／008／009、W3-offline-final-review-v1、W3-G35-sol61-low-v1及本次真实策略run。

## 2. 只读核对范围与证据

项目根：`D:\MyPythonProjects\datainsight`。本次核对：

- 执行结果：`docs/acceptance/results/w3-g35-real-v1-a.md`。
- 策略run：`outputs/W3/strategy-g35-real-v1-a/`中strategy.json、bindings.json全文分段、operation.json、final-status.json及目录匹配。
- 必要上游样例：固定S3审核receipt及终态、固定候选candidate-plans.json、固定S2 receipt。
- 当前analysis.py的load_w3_context、record_preservation_decision、load_strategy、operation及终态流程；未调用这些函数。
- 前序／反向证据继承W3限定离线最终验收与W3-v2，不重新审计全上游。

本次没有执行命令、计算新hash或读取CSV。hash一致性依据运行工具保存值和现有代码生成／核验路径，不冒称验收方独立重算了所有文件字节。没有全历史清单、扫描或重复进程恢复要求。

## 3. 最小验收清单

| 项目 | 判定 | 实际依据 |
|---|---|---|
| 许可／决定／动作分离 | 通过 | 执行文档分别记录用户明确批准A–F真实历史证据读取、选择preserve_all、确认actor=user及not_provided时间、批准准确单次命令／写入和零重跑；不从旧S3批准推定本次策略决定 |
| 真实固定批准链 | 通过 | 固定S2=accept、S3=approve且口径确认true；选定P-BEHAVIOUR-RECORDS／M-BEHAVIOUR-RECORDS，数据／问题／诊断规则／注册表／口径身份与新bindings相符；strategy保存前实际入口核验与check_context完成 |
| 策略及口径绑定 | 通过 | preserve-all-v1，scope=S3.5_preserve_all_only；全保留原始记录，不清洗／去重／过滤／填补／trim／改大小写；固定桶、NULL／other及全文件版本窗口保持 |
| 四文件与合法终态 | 通过 | strategy、bindings、operation及final-status齐全；run_id、command=strategy、status=success、exit_status=0相符；strategy.bindings_hash与final-status中bindings引用一致，必需引用名完整 |
| 时间／确认者语义 | 通过 | actor=user映射有明确用户依据；confirmed_at=not_provided；recorded_at独立为工具UTC时刻及来源，不代填确认时间。旧S2／S3时间原位保留，不重构历史字段 |
| 来源／权限限定 | 通过（本门限定范围） | 保存bindings的必要引用属于交接A–F固定链；strategy代码不调用fingerprint／calculate／worker，不打开CSV或连接DuckDB；不据此宣称全系统网络隔离或真实敏感值审计 |

反向底线由既有离线证据支持：缺终态／绑定变化／reject／cancel不得形成执行资格。此次真实门不重复制造反向输入，不为“无真实失败演示”追加运行。

## 4. 工具记录与身份引用

实际单次argv见执行文档与operation.json：`python -B -m datainsight.analysis strategy --decision preserve_all --actor user --confirmed-at not_provided --output-dir <固定strategy-g35-real-v1-a目录>`。cwd为项目根；保存环境Python3.12.9／DuckDB1.4.1，实际退出0，CLI phase=strategy／reason_code=ok。

运行工具保存身份：

| 对象 | 保存值 |
|---|---|
| strategy.bindings_hash／终态bindings引用 | `59401aec63c30e65b39351d4488b2e17e7a4f00449c10aec688b2dbbb929da4f` |
| 终态strategy引用 | `c081b59260443bded2c1695fdddf755b55df414478bd3b51f4505e1230f70160` |
| 终态operation引用 | `0eaecf4c6d3aee5d1a52dea27410a58079076913cd4b4aff4c60247f7a752094` |
| 已批历史dataset_version | `7095a57fbd6eb1292bec5ccde4713ac256678b8551eb478d3b5aaad89612cfb4` |
| 已批口径hash | `567762be0d1ea69a2b3095b8132fee269e15e2288a86dc3dc486eb3fac6d7951` |

strategy.recorded_at=`2026-10-14T08:08:08.316223+00:00`，operation.recorded_at=`2026-10-14T08:08:08.326689+00:00`，final-status.completed_at=`2026-10-14T08:08:08.329799+00:00`。均引用运行工具结果，不是用户确认时间或本验收文档落盘时刻。

当前dataset_version只是历史已批身份。本门没有计算当前CSV内容hash，不能宣称当前源未变化。模型token／usage／费用not_applicable；开发费用／耗时未取得依据，不估算。

## 5. 保持项与下一门

human_review_state=pending不撤销receipt中的明确G3.5决定，也不意味着S6批准。S2／S3各自scope、候选pending及原清洗授权文字保持历史语义；新的独立策略receipt没有回写候选或扩大旧批准。

原生产画像／模板重跑与修复后合成收尾继续分开；G3.5未新增生产计算。W2-B2整体未验收／真实调用暂停保持，不因为策略通过重启模型调用。

本批仅保存本结论、新建[E3-REAL交接](../../handoffs/W3-E3-REAL-sol61-low-v1.md)并同步INDEX。不改旧run／结果／frozen、源码或配置，不新增ADR、不生成教学交接或其他Agent／Session。

下一门为独立E3-REAL：用户准确批准固定生产CSV的只读hash／严格解析／受信聚合及现有单次execute命令／本地写入范围后，low才能执行。实际源身份／上游绑定变化则停止，不自动重新批准、重跑或修复。真实计算／三层S5／草稿交回high；S6再独立。
