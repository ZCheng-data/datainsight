# W3限定离线最终验收 v1：R3通过

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

## 1. 当前权威判定

**W3限定离线技术验收：通过。该离线范围阻塞项：无。无需新增离线补齐批次。**

依据[W3-v2 frozen](../W3-v2.md)及[ADR-009](../../decisions/ADR-009-W3-evidence-calibration-and-minimal-offline-closure.md)，继承已核对的前序／R2证据，R3闭合M1–M3及受影响最小回归。本判定不根据执行者自评、用例数量或runner退出码单独作出。

**W3整体仍未验收。** D301真实固定链核验、D302真实G3.5决定、D303当前真实源身份及D312真实计算／S5／本地草稿尚未运行，不能由合成证据替代。随后S6人工业务解释确认仍独立。

- confirmation_actor：用户。
- confirmation_basis：用户提交R3交回请求验收；规划／验收方只读核对后给出限定离线通过，随后用户回复“批准下一步”，批准新建本记录并更新INDEX。
- confirmed_at：not_provided。
- recorded_at：null；recorded_at_source：not_available；recorded_at_status：unavailable。
- recorded_at_reason：本次记录仅使用文件工具，未取得可信精确记录时刻；不执行取时，不估计、不以历史运行时间或会话日期代填。
- authorization_scope：P-W3-OFFLINE-FINAL-DOC仅新建本验收记录并更新结果INDEX；不改标准／源码／配置／旧结果／运行证据，不运行，不读取生产CSV或真实画像工具输入，不启动真实门／网络／凭据／API。
- bound_versions：W3-v2 frozen、ADR-003／005／007／008／009、R2-b继承证据及R3-a新证据；W3-v1和历史结果原位保留。

## 2. 本次只读核对与证据范围

项目根：`D:\MyPythonProjects\datainsight`。相对路径如下：

- 执行交回：`docs/acceptance/results/w3-e3o-r3-a.md`。
- 新证据根：`outputs/W3/offline-w3-e3o-r3-a/`，简称R3。
- 直接核对R3的case-results.json、batch-result.json、operation.json、reference-results.json、test.log。
- 核对analysis-normal的result.json、calculation-evidence.json、validation.json、report.md、final-status.json及strategy-normal/strategy.json。
- 核对expired-post-hash、expired-success-staging、required-write-failure的final-status；另读expired-success-staging/final-status-success.tmp。
- 目录匹配结果显示strategy-missing-terminal包有strategy／bindings／operation，无final-status；测试断言确认目标执行目录没有创建。
- 定向读取当前`src/datainsight/analysis.py`的deadline／成功发布／失败收尾／局部配置代码，以及`tests/test_w3.py`的run_r3、正常／M1／M2／M3／回归实际断言和结果生成逻辑。
- 前序／R2继承范围按[校准记录](W3-r2-evidence-calibration-v1.md)，不重做上游或97项矩阵。

本次未执行命令、未重跑、未独立计算文件hash；已有hash引用及一致性依据保存产物和测试中的实际工具核验。没有把当前源码阅读冒称独立运行时快照身份认证；没有全历史清单／扫描／系统隔离审计。

## 3. M1–M3与最小回归判定

| 范围 | 判定 | 已核对的实际行为与证据 |
|---|---|---|
| 正常worker／计算／S5／草稿／终态 | 通过 | run_r3通过受控fixture适配实际spawn worker，使用真实DuckDB；result与独立csv.reader/Counter工具结果一致；S5三层pass；报告字节与确定性渲染一致；终态消费核对引用hash，human_review_state=pending |
| M1／D302：策略缺成功终态 | 通过 | 新独立策略包省略final-status，实际execute_verified_plan返回evidence_missing_or_size；source_check／fingerprint／calculate／supervised／success调用均为0，目标目录未创建；不是预设整个load_strategy拒绝 |
| M2／D305：局部配置不符 | 通过 | 真实连接与实际配置SELECT，代理只把观测threads改为2；实际calculate比较返回resource_configuration_mismatch，仅配置SELECT发生、无业务查询，连接关闭；正常配置由正常基线支持 |
| M3／D305：后置核验过期 | 通过 | 实际check_context完成后受控单调时钟跨deadline，execute返回execution_deadline；success发布调用为0，failed终态存在 |
| M3／D305：成功暂存过期 | 通过 | 实际写完final-status-success.tmp后时钟过期，publish在rename前拒绝；必要结果／草稿已存在，但合法final-status为failed，没有发布success；原位保留tmp |
| 禁止覆盖 | 通过 | 对已有analysis-normal运行目录返回output_exists，已有终态发布返回terminal_exists；原终态字节保持 |
| 必需写入失败／安全收尾 | 通过 | result.json保存处受控失败确实生效，实际main返回1；无敏感错误raw回显，失败终态保存；新增deadline成功门未阻止失败收尾 |

代码依据：`analysis.py`的execute_verified_plan在后置核验、必要写入、S5／渲染／回读之间核对同一deadline；success传递end，publish在暂存前后及rename前检查。失败终态不携带已过期成功门，仍允许受控收尾。

M3的父进程边界反向复用合法真实计算结果／受控worker返回以隔离时钟路径，正常基线另有实际spawn；这不冒称两个反向都重新执行真实worker。测试不实际等待180秒。

### 暂存文件不是成功终态

`expired-success-staging/final-status-success.tmp`内部status=success只是未发布暂存；同目录合法`final-status.json`明确status=failed、exit_status=1。符合ADR-003原子发布规则，不是残留成功终态，不需要清理、回填或补测。

## 4. 运行工具记录与时间语义

R3保存值：total_cases=7、passed_cases=7、offline_test_status=passed、halted_reason=null、exit_status=0、technical_acceptance=pending、stage_acceptance=not_performed。测试源码根据实际断言／中断情况生成状态，没有照抄R2固定incomplete清单。

实际argv：`.venv/Scripts/python.exe -B -m test_w3 --w3-r3-evidence --batch-id w3-e3o-r3-a`；cwd为项目根，Python3.12.9／DuckDB1.4.1。operation记录进程运行信息；执行交回说明PYTHONPATH及TEMP／TMP／TMPDIR为批准项目D盘范围。

operation保存：

- authorization=P-W3-E3-OFFLINE-R3；confirmation_actor=用户；confirmed_at=not_provided。
- confirmation_basis为用户在执行对话批准精确R3候选的执行方记录；不把本轮验收或文档批准当作新增运行许可。
- started_at=`2026-10-14T07:29:57.168817+00:00`。
- recorded_at=`2026-10-14T07:30:17.988818+00:00`，来源python_datetime_utc，是本批运行工具记录时刻，不是用户确认时刻或本文件落盘时间。
- elapsed_seconds原值`20.820203799999945`，是工具记录的本批时长，不估算为未来耗时。
- model_usage=not_applicable；development_tokens／development_cost=unknown。不推算费用或效率提升。

合成strategy中的actor=synthetic_actor，不是用户真实G3.5决定；confirmed_at与recorded_at分开，旧S2／S3记录不改。

## 5. D301–D312当前层次

| 范围 | 当前判定 |
|---|---|
| D301–D311的限定离线证明义务 | 按W3-v2继承前序／R2证据并由R3闭合必要增量，离线技术门通过 |
| D301真实固定链／D302真实G3.5 | 未运行，独立真实核验链读取与人工决定门尚未授权 |
| D303真实源前后hash／D312真实E3 | 未运行，须当次准确读取许可；W3整体未验收 |
| S6业务解释确认 | W3真实结果之后独立，不由草稿、S5或本离线通过代替 |

限定离线范围无遗留阻塞，不新增离线矩阵或R4。若后续数据／问题／规则／方法／口径身份变化、实际功能缺陷或边界变化，则停止并明确影响；这不是现在预先增加审计补证的理由。

## 6. 能力边界、历史保持与下一门

通过能力仅包括已批准固定方法／口径的合成执行、三层校验／草稿、必要门控／失败／合作式deadline控制。不是OS硬实时、总内存或DuckDB原生／全系统网络隔离认证，不认证任意输入、开放方法、自由SQL、协同篡改或所有隐私值。

W3仍零模型。W2-B2停止续作、整体未验收／真实调用暂停与旧C205缺口保持；不因本离线通过重新调用DeepSeek。历史生产画像／模板重跑与修复后合成收尾分别引用，新R3不包含生产CSV计算，不回填旧状态。

本次只新建本记录及更新INDEX，不修改W3-v1／v2、ADR、源码、配置、R2／R3执行文档或产物，不清理tmp，不自动生成教学交接、创建Agent／Session或运行命令。

下一门：另行明确G3.5所需固定真实核验链读取范围与人工策略决定安排；无源CSV读取／计算权限。真实E3必须在有效策略与独立当次读取许可之后，仍一次合批计算／校验／草稿交回技术验收。本次“批准下一步”仅指上述文档动作，不授权该真实门。
