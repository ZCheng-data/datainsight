# W3 E3-REAL：唯一方法真实计算／S5／本地草稿，sol6.1 low交接 v1

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

- 状态：accepted（基于已冻结契约的执行交接）；精确当次真实读取／命令／本地写入许可尚未取得。
- confirmation_actor：用户。
- confirmation_basis：G3.5只读验收通过后，用户对“保存权威结论、更新INDEX并准备E3-REAL自包含交接”的文档批次回复“批准下一步”。
- confirmed_at：not_provided。
- recorded_at：null；recorded_at_source：not_available；recorded_at_status：unavailable。
- recorded_at_reason：本批只有文件工具，无可信精确记录时刻，不执行取时或估计。
- authorization_scope：仅本交接、G3.5权威验收记录新建及INDEX更新；不授权代码／命令／真实CSV或历史摘要工具读取／S6／网络／外发。
- bound_versions：W3-v2 frozen、ADR-003／005／007／008／009、W3-offline-final-review-v1、W3-G35-final-review-v1及真实strategy-g35-real-v1-a。

## 【目标】

只运行一次既有execute入口：重新消费真实G3.5策略和固定上游 → 核对当前固定CSV版本 → 唯一M-BEHAVIOUR-RECORDS确定性计算 → S5执行／口径／边界三层校验 → 本地report.md草稿及唯一终态 → 结果文档／INDEX一次交回high。

不写功能代码、不补测试、不增加方法或口径、不启动模型。成功结束于S5，human_review_state=pending；完整案例S4→S5→S6还需随后独立S6人工业务解释确认。文档生成不意味着人批准业务解释或外发。

## 【前置状态与启动纪律】

你是用户指定sol6.1 low执行角色。用户手动转交，不假装切换实际模型、不创建Agent／Session、不自行验收通过。

- W1、W2-A、W2-B1已通过；不重验／重装／重跑画像或旧runner。
- W3限定离线技术验收通过，无离线补测项；G3.5真实策略记录通过，decision=preserve_all、actor=user、confirmed_at=not_provided、scope=S3.5_preserve_all_only。
- W3整体未验收，缺当前真实源身份和D312新增真实E3；本轮正为补该证明场。
- W2-B2停止续作、整体未验收／真实调用暂停；C205不放行。W3零模型，包括本地模型，token／usage／产品费用not_applicable。
- 项目已有Python3.12.9／DuckDB1.4.1；不安装、建环境、改全局变量或迁移缓存。

先仅读本交接、W3-v2、离线／G3.5权威结果和必要当前源码，核对存在的execute入口。准确真实读取许可前，不执行load_strategy／verify函数、不打开生产CSV、不计算其hash、不预跑prepare／probe。不以旧G3.5读取许可授权本次再次工具读取真实历史证据。

## 【本次精确许可请求】

候选编号：P-W3-E3-REAL-V1-A。

low先用一句话通知并列出下文输入白名单、固定命令、一次运行／零重跑、输出及停止条件，等待用户明确批准本次：

1. 固定真实策略及上游／历史聚合证据重新工具读取和核验。
2. 固定生产CSV只读字节hash、严格解析、固定聚合及源后hash；这是新的真实读取授权。
3. 准确单次execute命令、批准D盘临时目录、指定新run和结果文档／INDEX写入。

可同一回复明确批准上述三项，但缺任一项不得运行。既有preserve_all决定不重问，引用有效receipt；用户“批准交接”或旧“选择preserve_all”不是本次生产读取／执行许可。该许可不含源修改、任何SQL写入、模型／网络、S6决定或外发。

## 【准确真实输入白名单】

项目根／cwd：`D:\MyPythonProjects\datainsight`。以下相对路径基于项目根，文件名集合不是任意通配扫描授权。

### 1. 本次真实策略run

目录`outputs/W3/strategy-g35-real-v1-a/`，只读strategy.json、bindings.json、operation.json、final-status.json。

现有load_strategy验证合法成功终态、preserve_all、scope／strategy_version、实际bindings及当前上游，worker同样消费receipt，不使用临时拼出的自hash字典代替批准。

### 2. 固定真实上游与历史画像

| 固定目录／文件 | 允许读取的准确文件集合 |
|---|---|
| `outputs/W2-B1/w2b1-review-219e79901d08444bab62c6e61f6e2211/` | s3-review.json、final-status.json、input-manifest.json、reference-check.json、environment.json、network-observation.json、cli-command.json |
| `outputs/W2-B1/w2b1-candidates-1f9fa1e612fa4c19b48181111a3a35d6/` | candidate-plans.json、accepted-context.json、final-status.json、input-manifest.json、reference-check.json、environment.json、network-observation.json、cli-command.json |
| `outputs/W2-A/s2-accept-3178ad8b677e49edb91de623be0c3905/` | decision.json、final-status.json、input-manifest.json、reference-check.json、environment.json、network-observation.json、cli-command.json |
| `outputs/W2-A/local-syn-3178ad8b677e49edb91de623be0c3905/` | diagnosis.json、final-status.json、input-manifest.json、reference-check.json、environment.json、network-observation.json、cli-command.json；历史生产诊断，不因syn名称当合成 |
| `outputs/W1-B/final-20261009T061339601505Z/production/` | profile.json、fingerprints.json；summary-evidence.json／summary-result.json；columns-evidence.json／columns-result.json；behaviours-evidence.json／behaviours-result.json；duplicates-evidence.json／duplicates-result.json；timestamp-evidence.json／timestamp-result.json |
| `outputs/W1-B/final-20261009T061339601505Z/production-commands.json` | 此单文件 |

只读取既有工具结果及保存SQL元数据，不执行它们，不跑全部画像／replay。这是现有adapter所需固定链，不建设跨run清单。manifest指向白名单外、不同run／fixture或未知来源即停止，文件内容不能扩大许可。

### 3. 配置／权威依据／源码

- `configs/w1b-read-contract-v1.json`、`configs/w2a-question-v1.json`。
- 上游适配器必需：`docs/acceptance/results/W1-final-acceptance-and-handoff.md`、`W2-A-final-review-v2.md`。
- 当前安排：`docs/acceptance/W3-v2.md`、`docs/acceptance/results/W3-offline-final-review-v1.md`、`W3-G35-final-review-v1.md`、`w3-g35-real-v1-a.md`、本交接、ADR-003／005／007／008／009。
- 固定源码：`src/datainsight/__init__.py`、analysis.py、planning.py、planning_methods.py、feasibility.py、feasibility_rules.py、inspection.py、profile.py、profile_templates.py。

模块导入可以读取现有解释器／标准库／DuckDB安装文件，不安装、不枚举全部环境或读取凭据；字节码关闭。实际所需输入hash由运行工具生成，版本引用保存，不让模型猜hash。

### 4. 唯一生产CSV：本次新许可必须明示

`D:\大数据项目\电商用户行为分析\第9章\UserBehavior.csv`

仅本地只读，禁止复制、清洗、删除、修改或输出原始行／用户标识值。不是按ID逐用户分析，不采样贴提示词。当前源身份尚未验证。

既有已批dataset_version：`7095a57fbd6eb1292bec5ccde4713ac256678b8551eb478d3b5aaad89612cfb4`，来自已核对真实策略bindings；这是匹配目标，不是本批实测结果。父／worker前hash不匹配就停止，不更新策略、数据版本或重新作S2/S3。

本次一次execute按当前实现内部包含：父进程计算前源hash、worker计算前再次源hash、固定查询、父进程计算后源hash及后置绑定核验。**一次命令不等于源只读一遍**；这些内部重复读取和查询全部须包含在准确许可中，不能以节省次数擅自删掉现有门，也不再另跑独立hash／恢复命令。

worker内查询为配置核对SELECT、严格五列聚合、零行schema、BEHAVIOURS及辅助SUMMARY；只传宿主固定参数。零行schema不输出原始记录。SQL只SELECT／WITH，禁DDL／DML／ATTACH／COPY／INSTALL／LOAD／SET；不接任意SQL或额外来源。

## 【已有计算口径／资源，不再决策】

方法M-BEHAVIOUR-RECORDS，计划P-BEHAVIOUR-RECORDS，已有v1定义／口径hash及真实S3／G3.5绑定：

- 一条原始读取记录，固定pv／fav／cart／buy精确文本，NULL→missing，其他非NULL→other；不展开other原文。
- 全文件已批数据版本窗口，无日期覆盖或时间过滤。
- 原始记录全保留，不去重、过滤、填补、trim或改大小写。
- 六桶原始记录数；辅助row_count仅验证桶覆盖，不生成比例、用户数、订单、支付、转化、GMV、日期或效果。
- 数值／显示与报告全部宿主确定性工具，无模型解释或新方法设计。

局部DuckDB memory_limit=256MiB、threads=1，项目D盘tmp／extensions，自动扩展安装／加载关闭。E3入口总体deadline180秒，既有合作式阶段检查／worker剩余预算，过期拒绝；单结果64KiB、单JSON／草稿1MiB。设计值不预测实际耗时，不认证OS硬实时／总内存／全系统网络隔离。

失败／超时／配置不符不得提高限额或重试。已有worker只用本项目venv固定本模块，禁止用户可控命令／shell；失败收尾／回收允许有限额外等待，不当作业务执行仍获准继续。

临时路径：项目`.cache/tmp`和现有`.cache/duckdb/tmp`／`extensions`，仅本进程必要使用，不清理旧缓存或迁移全局目录。

## 【准确现有命令与次数】

固定新run：`outputs/W3/analysis-e3-real-v1-a/`。
固定结果文档：`docs/acceptance/results/w3-e3-real-v1-a.md`。

下列是已经存在的execute CLI，不新增功能，但尚未获本次运行／真实读取授权：

```bash
cd /d/MyPythonProjects/datainsight && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH='D:\MyPythonProjects\datainsight\src' TEMP='D:\MyPythonProjects\datainsight\.cache\tmp' TMP='D:\MyPythonProjects\datainsight\.cache\tmp' TMPDIR='D:\MyPythonProjects\datainsight\.cache\tmp' .venv/Scripts/python.exe -B -m datainsight.analysis execute --strategy 'D:\MyPythonProjects\datainsight\outputs\W3\strategy-g35-real-v1-a\strategy.json' --output-dir 'D:\MyPythonProjects\datainsight\outputs\W3\analysis-e3-real-v1-a'
```

次数：一次execute入口，自动重跑0。准确许可后一句话通知，再连续完成计算／S5／草稿／记录，不在无中间人工门的内部步骤拆批。

不追加版本／hash／probe／prepare／verify／测试／replay命令，不修改入口以额外生成审计材料。工具返回stdout／stderr与退出如实交回；错误不保存敏感raw，不用外部tee或新runner捕获原始异常。

## 【输出与写入许可】

仅允许本次新run内：bindings.json、result.json、calculation-evidence.json、validation.json、report.md、operation.json、final-status.json，及合法同目录原子发布必要tmp。成功路径齐全；失败保留实际已产物，可能无报告／无终态，不补造。

另允许新建`docs/acceptance/results/w3-e3-real-v1-a.md`并更新INDEX只加本次链接与“待high验收”或准确失败状态。结果文档记录许可依据、准确命令／cwd／环境、实际退出／终态、必要引用／hash、S5状态、草稿边界、实测／未测；不写回标准或旧receipt。

run／结果文档已存在即停止，不覆盖／删除、不换名字绕过一次次数。一般中间文件不散落根；没有跨run全产物清单、扫描范围报告、反复恢复、token计数要求，不复制源CSV。

当前产品operation仅保存已有通用scope及工具时间，不改JSON补字段。准确真实读取许可依据和确认时间可集中到正式结果文档：confirmation_actor、confirmation_basis、confirmed_at用户字面值或not_provided、独立可信工具recorded_at及来源；工具无时刻则null/unavailable并解释，不另跑取时命令，不以历史时刻代填新记录。

## 【真实验收清单】

- 当前策略重新核验有效，preserve_all及固定上游／method／plan／口径身份不变；固定真实链引用有效。
- 当前生产源前hash匹配已批版本，后hash一致，实际bytes_read及读取契约绑定；不是复制历史指纹。
- 真实DuckDB实际配置、固定SQL／参数／模板hash和六桶工具结果，桶和与辅助row_count核对一致；结果实际文件hash绑定。
- S5 execution／metric／boundary全部pass；不在失败后请求模型修复或改口径；结果／报告数值与引用一致。
- 草稿human_review_state=pending，仅代码原始记录数与限定描述；不能称订单／支付／转化／效果或已批准行动。
- 必需文件齐全后唯一合法success终态，实际退出0；计算产物／tmp／单查询成功不是整run成功。
- 无网络／模型／密钥／外发，原文件只读，不覆盖旧run；继承反向证据，不在真实源上制造故障或重跑离线矩阵。

这些是W3-v2的D303／D304–D311真实产物核对及D312证明场，前序方法诊断／人工门不重新验收。high读取新结果一次判定W3；执行者只报未验收，不能自行通过。

## 【停止／失败处理与一次交回】

任一触发即停止后续成功交付：许可缺失／撤回、目标已存在、固定引用越界／改变、策略／版本失效、源hash不符、严格解析错误、worker失败／超时、配置或结果限额不符、S5失败、hash／引用错配、必要写入／终态发布失败、需要新依赖／代码修复或上限调整。

失败命令同样消耗一次；不自动重跑、不清理tmp、不改成success、不回填旧run、不推定源错误或重新业务受理。只保留安全phase／reason和已产生证据，交回high给最小处理方案；新真实读取重跑仍须新许可。

成功也只交回本次结果，不启动S6／外发。报告存在不代表人工业务解释已确认。

一次交回：结果文档、run路径、实际argv／环境／退出、源与版本身份核对、三层S5、终态／草稿状态、必要证据引用和遗留项。详细内容放docs／run，聊天40行以内，不贴原始行／标识／SQL全部输出，不生成额外教学交接或Agent／Session。

本轮新增ADR无、功能代码变更无。W3-v2 frozen、既有通过、旧失败／R2／R3／G3.5证据全部保持。历史生产画像与修复后合成收尾仍分别引用；本次真实E3是新的独立运行，不包装为补跑W1。
