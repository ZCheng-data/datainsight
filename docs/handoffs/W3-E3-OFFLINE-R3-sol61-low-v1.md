# W3限定离线收尾R3：sol6.1 low自包含交接 v1

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

- 状态：accepted（校准范围与交接）；本文件精确命令／batch／运行次数是新列出的许可候选，未获执行预授权。
- confirmation_actor：用户。
- confirmation_basis：用户批准按必要证据基线另版W3标准及最小剩余方向；本次落盘不推定尚未提供的R3命令／次数已获批准。
- confirmed_at：not_provided。
- recorded_at：null；recorded_at_source：not_available；recorded_at_status：unavailable。
- recorded_at_reason：本批仅文件工具，未取得可信精确时刻，不估计或执行取时。
- authorization_scope：仅ADR-009、W3-v2、R2校准记录与本交接新建及INDEX；不授权功能／测试／真实读取／人工决定／网络。
- bound_versions：ADR-003／005／007／008／009；W3-v2 frozen；W3-v1和R2证据保持。

## 【目标】

只做一个有限离线结果闭环：补新策略缺终态拒绝、配置不符拒绝及总体deadline后半程保护，做受影响最小回归，生成新合成证据与结果文档，一次交回high。

不重建97项矩阵，不补路径链接／字节精确边界／逐文件底层故障／provider不存在API证明，不加方法或功能，不进入G3.5／真实数据／S6。

## 【前置状态与职责】

你是用户指定sol6.1 low执行角色；不声称切换实际模型，不创建Agent／Session，不自行验收通过。

W1、W2-A、W2-B1通过保持。W2-B2真实接入停止续作，整体未验收、C205未满足，真实调用暂停。W3零模型，不读取密钥、账户、预算账本、不联网、不调用本地／远端模型。

R2-b已记录97项用例通过，但batch-result固定incomplete／unmet；原结果原位保留。高档校准允许继承已有证据，离线仍有M1–M3必要缺口；D312及真实G3.5是后续独立门，不能计成离线补齐失败，也不能省掉总验收。

现有Python3.12.9／DuckDB1.4.1项目venv，不安装／重建环境；实际不符停止。当前analysis.py、test_w3.py已存在，先只读核对实际函数，若与交接前提不符停止报告，不整仓扫描或重跑历史runner。

## 【先申请的精确许可候选】

许可候选名称：P-W3-E3-OFFLINE-R3。

取得许可前仅读本交接、ADR-009、W3-v2、R2校准结果及需要的当前源码；不运行、不生成fixture、不写功能。启动前用一句话列本批目的、下面两文件修改、固定命令／batch和一次运行上限，请用户明确批准该候选范围。此前“批准校准”或R2授权不作为此精确预授权。

拟批准后在范围内合批连续完成，不按每个文件重复申请；每批开始通知，用户可叫停。

### 可改文件（仅两份）

- `src/datainsight/analysis.py`：仅execute后半程／成功发布边界所需deadline检查及其最小传递。保持原函数入口、方法、口径、180秒、worker监督、输出及失败收尾；不为补M1/M2无故改功能。
- `tests/test_w3.py`：新增隔离R3证据入口、M1/M2/M3和受影响最小回归，校准新runner状态生成。原R2入口和历史batch仍拒覆盖，不移除旧用例；R3不调用全97项矩阵。

不得改其他源码、上游helper、配置、标准、旧handoff／ADR／run。发现三项之外实际功能缺陷需停止交回，不能顺手修复或新增完整框架。

### 运行／写入范围（准确新命名）

- batch_id=`w3-e3o-r3-a`。
- `tests/fixtures/w3/w3-e3o-r3-a/`：有限合成CSV，仅同方法原始记录测试。
- `outputs/_scratch/w3-e3o-r3-a/`：合成上游核验链、独立策略包；标明synthetic，不能读取真实S2／S3或生产画像摘要。
- `outputs/W3/offline-w3-e3o-r3-a/`：本批test.log、case-results.json、reference-results.json、batch-result.json、operation.json及有限正常／反向子run，包含合法策略与E3合成结果。
- `.cache/tmp/`及现有`.cache/duckdb/tmp`／`extensions`：仅批准进程临时路径，不清理旧缓存。
- `docs/acceptance/results/w3-e3o-r3-a.md`新建；`docs/acceptance/results/INDEX.md`仅追加新结果导航，不把旧R2改成功。

所有新目标先检查不存在，存在即停，不覆盖／删除／移动旧数据／证据。outputs普通同目录发布tmp仍必要例外，失败残留原位保存。

### 准确命令候选（新增入口，尚未实现／授权）

cwd为`D:\MyPythonProjects\datainsight`，已有项目venv。固定Git Bash命令：

```bash
cd /d/MyPythonProjects/datainsight && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH='D:\MyPythonProjects\datainsight\src;D:\MyPythonProjects\datainsight\tests' TEMP='D:\MyPythonProjects\datainsight\.cache\tmp' TMP='D:\MyPythonProjects\datainsight\.cache\tmp' TMPDIR='D:\MyPythonProjects\datainsight\.cache\tmp' .venv/Scripts/python.exe -B -m test_w3 --w3-r3-evidence --batch-id w3-e3o-r3-a
```

只此一次合成runner运行，自动重跑0。不增加试跑、discover、编译检查或另跑旧suite；静态源码核对不执行命令。失败保留部分结果，一次交回，不占用新batch再试。若用户希望预授权重跑，需准确新batch／命令／次数另批，不能推定R2仍有余额。

代码修改与一次运行均须该精确许可先获批准；本规划对话不实施。

## 【复用接口与必要修复】

函数仍为现有：load_w3_context、record_preservation_decision、load_strategy、calculate、supervised、validate_s5、render_report、execute_verified_plan、success／publish。完整定义和先前接口不重构。

当前execute_verified_plan在after fingerprint后的remaining检查之后，继续check_context／load_strategy、S5、报告和必要文件写入，最后直接success。这一后段缺时间保护，worker超时回收测试不能证明整个E3受控。

最小修复要求：

- 用入口已建立的同一个end，在后置耗时阶段之间及成功发布前检查剩余时间。
- 如时间预算需要传到成功终态准备／发布前路径，只增加局部可选参数或私有helper；不得对外开放deadline提高或用户可控worker。
- 已知过期必须拒绝，不能继续发布success；不得仅在后半程开始检查一次然后永久假定未过期。
- 不给失败终态同样加一个已过期即拒绝的成功门，失败收尾／回收仍可以执行；不改未覆盖允许的硬实时承诺。
- 180秒、256MiB、threads=1、结果64KiB、文档1MiB都不改；这是合作式检查／固定worker监督，不保证OS阻塞或最终rename瞬时撤销，不新增系统监控。

M1／M2目前看是证据缺口，不要求重写策略或配置功能。没有足够依据就写未完成，不为了出green改测试期待值或伪造终态。

## 【验收：最小新增集合】

### M1：新策略缺成功终态

- 基线：合成合法S2／S3→实际W3策略记录→load_strategy正常消费。
- 反向：独立创建本轮新策略包，省略final-status；其他条件合法。不要删除／patch旧已发布文件来冒充新包。
- 走实际execute_verified_plan或main入口，拒绝发生在源读取／计算前。记录真实异常／安全reason及source read／fingerprint／calculate／成功发布未调用的直接断言，不把query_count=0字段当唯一证据。
- 不展开scope／version／schema／actor所有身份字段排列。

### M2：局部配置不符

- 基线：实际DuckDB连接、同固定config与固定聚合成功，记录实际observed配置。
- 反向：只改变config观测中一个目标字段，复用实际calculate配置比较路径（受控cursor代理或有限patch允许，真实连接其余操作照常）。
- 断言resource_configuration_mismatch，未执行strict／behaviours／summary等业务查询、未生成成功草稿，connection关闭。配置读取SELECT可以发生，不能伪造query_count=0。
- 不模拟更早非法来源／策略错误掩盖配置路径，不要求所有config字段逐个故障。

### M3：总体deadline后半程

- 基线：合法合成包、实际spawn worker、三层S5、草稿、唯一终态正常；不mock DuckDB为固定结果。
- 反向一：在最后源后hash之后的后置核验阶段，用受控单调时钟／延迟使剩余时间耗尽；走实际execute入口，拒绝过期且无success。
- 反向二：本地必需文件写入已发生、时间在成功发布前耗尽；真实成功发布路径拒绝，无合法success，部分结果与失败状态如实保留。
- 测试可以复用本轮合法计算结果／受控worker返回来定位父进程时钟路径，但基线必须有实际worker；不实际等待180秒，不新增sleep长跑。
- 记录phase、actual reason、CLI／函数结果、成功发布调用或终态状态；若失败记录无法写，明确非零与failure_evidence_persisted=false，不追改成成功。

### 受影响最小回归

与基线／上述负向共用，不增加重复矩阵：

- actual DuckDB聚合与独立csv／Counter参考一致；六桶／row_count、S5三层pass、报告数值／引用及pending状态正确。
- 正常成功终态及字节引用消费有效；已有输出／终态拒覆盖，目标marker／字节不变。
- 至少一条沿用现有必需写入失败的实际execute拒绝，说明新增deadline门不破坏失败收尾；不是每文件×每底层操作。
- 受控本地失败不回显异常raw；模型／网络／凭据仍不调用，不补逐provider断言或扫描范围报告。

前序和R2其他证据以稳定引用继承；若本次修改真的影响旧功能路径，先说明影响，不自动expand全suite或撤销前序继承。

## 【新runner与结果语义】

R3必须从实际执行／断言生成passed／failed／halted；新增用例未执行或失败不能返回合成成功。不要照抄R2固定status=incomplete、unmet。

- offline_test_status：只描述本批新增用例和最小回归。
- inherited_evidence：列R2根及被引用case类别、前序条款，不复制所有产物或重算历史全部hash。
- remaining_offline：只列实际必要新缺口；为空不等于W3总体通过。
- deferred_real：D301真实固定核验、D302真实决定、D303真实hash及D312实际计算未授权／not_run，明确后续门；不使离线runner固定失败。
- technical_acceptance：pending；stage_acceptance：not_performed。high一次核对真实结果，执行方不能自封通过。

按ADR-005记录本批许可依据、confirmed_at用户字面值或not_provided、独立工具recorded_at及来源；不能借日期／run_id／旧R2时间代填，不贴密钥或原始行。

产品模型费用not_applicable；开发token／金额／总耗时没有工具证据则unknown。可以工具记录本批实际时长，不估算为实测，不为记录时间另跑未授权命令。

## 【保护／停止条件】

- 不读取生产CSV、真实画像摘要或真实S2／S3作为运行输入；合成patch必须严格限新fixture／scratch，不能从文件名syn推定真实可读。
- SQL仅原受信SELECT／WITH；禁DDL／DML／ATTACH／COPY／INSTALL／LOAD／SET，自由SQL不支持。
- 不改方法／口径／资源数值、旧helper／模板／终态、预算／provider、准备包或全局配置；不装新依赖、不联网、不创建会话、不Git提交／推送。
- 本次一次执行耗尽、失败、目标已存在、需要范围外文件／修复或发现新的必要功能缺口，停止交回，不自动R4。
- 成功也只交回离线结果，不进入真实G3.5／E3-REAL或S6。用户叫停停止新动作，已产生失败／部分证据原位保留。

## 【完成后一次交回】

新结果文档与R3证据路径、准确argv／cwd／环境／实际退出、M1–M3与最小回归actual／expected／断言摘要、必要产物和成功／失败终态、继承引用、遗留必要缺口、真实门deferred状态。

对话40行以内，只给结果／状态／下一门。详细证据放正式结果文档；不保存讨论／推理／临时文字、不自动教学交接或生成其他Agent／Session。
