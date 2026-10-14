# W3 G3.5真实策略决定门：sol6.1 low自包含交接 v1

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

- 状态：accepted（交接文档）；真实核验链工具读取、命令运行及策略决定均待独立授权／确认。
- confirmation_actor：用户。
- confirmation_basis：限定离线通过落盘后，用户要求继续；规划方提出仅新建本G3.5交接文档的请求，用户回复“批准”。
- confirmed_at：not_provided。
- recorded_at：null；recorded_at_source：not_available；recorded_at_status：unavailable。
- recorded_at_reason：本批仅文件工具，未取得可信精确记录时刻；不执行取时、不估计或借用历史时间。
- authorization_scope：仅新建本交接；不改INDEX／标准／代码／配置／旧证据，不运行，不读取真实receipt／画像作为工具输入、不读取生产CSV，不作人工策略决定，不联网／凭据／API。
- bound_versions：W3-v2 frozen、ADR-003／005／007／008／009、W3-offline-final-review-v1；原W3-v1及历史证据保持。

## 【目标与本门边界】

本轮只完成G3.5：用户明确选择策略 → 在准确许可下执行现有strategy命令，实际核验固定S2／S3及必要历史证据 → 绑定相符才保存独立真实策略记录 → 一次交回high核对。

此策略记录只表示S3.5决定，不授权读取生产CSV／计算，不自动进入E3-REAL、S6或外发。读取历史画像聚合证据不是重新计算画像，也不证明当前CSV未变。

现有CLI已足够，不新增代码、prepare／verify CLI、runner或新依赖。内置核验链可能重复读取同一证据，这是既有接口行为；本门只执行一次命令，不另跑独立恢复或审计矩阵。

## 【职责、前置状态与启动】

你是用户指定sol6.1 low执行角色；不声称切换实际模型，不创建Agent／Session，不自行验收通过。

- W1、W2-A、W2-B1通过保持；W3限定离线技术验收通过，范围内无补测阻塞，不再补R4或重跑R2/R3。
- W3整体未验收，真实核验／决定／CSV计算尚未完成。W2-B2停止续作、整体未验收／真实调用暂停；旧C205不放行。
- W3只用M-BEHAVIOUR-RECORDS／P-BEHAVIOUR-RECORDS，无模型、网络、密钥、预算或余额动作；token／usage／费用not_applicable。
- 使用项目已有Python3.12.9／DuckDB1.4.1环境，不安装或重建。strategy会导入现有DuckDB包，但不连接引擎、不执行SQL或启动计算worker。

先仅读本交接、W3-v2、W3-offline-final-review-v1及所需当前源码，核对现有入口。未获第【权限】节准确许可前，不打开真实receipt／画像包执行核验，不运行命令或新建结果文件。若实际源码／入口与契约不符，停止，不自动补实现。

## 【真实业务决定：不能默认】

决定对象是已批准唯一方法的原始记录保留策略，不是重新选择方法／指标：

| 选择 | 含义与后果 |
|---|---|
| preserve_all | 本轮不清洗；全保留原始记录，不去重、过滤、填补、trim或改大小写。保留固定文本pv／fav／cart／buy，NULL→missing，其余非NULL→other；全文件数据版本窗口。不推出订单／支付／转化／日期覆盖／效果。形成策略资格，但仍无生产读取许可 |
| reject | 不接受本轮策略，记录决定后停止；不寻找替代清洗策略或分析方法 |
| cancel | 取消本门，记录决定后停止；不默认恢复／继续 |

执行前用上述有限选项呈现并取得明确决定。用户只说“批准交接”“批准读取”“继续”不当作preserve_all；不从旧S3口径批准推定G3.5已决定。

可以在同一用户回复中获得多个明确许可／决定，但必须分别列明：①真实核验链工具读取；②所选策略；③一次命令及本地记录写入。任一缺失就不运行，不替用户补齐。条件确认绑定现有固定已批对象；若实际核验不符则停止，不转成对新版本的批准。

## 【准确输入读取白名单】

项目根：`D:\MyPythonProjects\datainsight`。下列相对路径均基于项目根。文件名集合是许可边界，不是通配扫描授权。

### A. 固定S3审核run

目录：`outputs/W2-B1/w2b1-review-219e79901d08444bab62c6e61f6e2211/`。

只读：s3-review.json、final-status.json、input-manifest.json、reference-check.json、environment.json、network-observation.json、cli-command.json。

### B. 固定候选run

目录：`outputs/W2-B1/w2b1-candidates-1f9fa1e612fa4c19b48181111a3a35d6/`。

只读：candidate-plans.json、accepted-context.json、final-status.json、input-manifest.json、reference-check.json、environment.json、network-observation.json、cli-command.json。

### C. 固定S2决定run

目录：`outputs/W2-A/s2-accept-3178ad8b677e49edb91de623be0c3905/`。

只读：decision.json、final-status.json、input-manifest.json、reference-check.json、environment.json、network-observation.json、cli-command.json。

### D. 固定诊断run

目录：`outputs/W2-A/local-syn-3178ad8b677e49edb91de623be0c3905/`。

只读：diagnosis.json、final-status.json、input-manifest.json、reference-check.json、environment.json、network-observation.json、cli-command.json。

该目录名称含syn，但本输入是历史生产画像诊断，不能把它当合成fixture许可。

### E. 必要历史生产画像包

目录：`outputs/W1-B/final-20261009T061339601505Z/production/`。

只读：

- profile.json、fingerprints.json。
- summary-evidence.json、summary-result.json。
- columns-evidence.json、columns-result.json。
- behaviours-evidence.json、behaviours-result.json。
- duplicates-evidence.json、duplicates-result.json。
- timestamp-evidence.json、timestamp-result.json。

另只读同一历史run根的`outputs/W1-B/final-20261009T061339601505Z/production-commands.json`。

这是现有固定上游adapter完整核验所需集合；不执行保存SQL、不重新统计，不增加读取其他历史生产run、replay目录或修复后合成包。历史生产特例没有当前协议final-status，不补造。

### F. 配置、权威记录与固定源码

- `configs/w1b-read-contract-v1.json`、`configs/w2a-question-v1.json`。
- `docs/acceptance/results/W1-final-acceptance-and-handoff.md`、`W2-A-final-review-v2.md`，分别作为现有adapter／S2核验依据。
- 规划／范围核对：`docs/acceptance/W3-v2.md`、`docs/acceptance/results/W3-offline-final-review-v1.md`、本交接及ADR-003／005／007／008／009。
- 固定源码：`src/datainsight/__init__.py`、analysis.py、planning.py、planning_methods.py、feasibility.py、feasibility_rules.py、profile.py、profile_templates.py、inspection.py。

必要模块导入可读取现有解释器／标准库／DuckDB安装文件，不枚举全环境、账户或缓存；进程禁止写入bytecode。上游规则／方法／模板摘要及JSON必要实际字节hash由现有工具计算，不让模型猜值。

保存manifest／receipt中出现的路径不扩大白名单。若它们引用白名单外文件、fixture／新run／外部URI或不同审核对象，停止并报告安全原因；不要顺着引用读完再申请，也不要改manifest。原源码路径校验保持，不关闭安全检查。

### 明确禁止读取／动作

生产CSV：`D:\大数据项目\电商用户行为分析\第9章\UserBehavior.csv`不在本门读取范围，连新的内容hash、画像、采样或数据查询也不做。bindings可保存已有source_path字面值，不跟随它打开源或核验当前源文件。

不读取旧淘宝项目、其他数据、任意outputs、原始行／标识值、密钥／.env／账户余额；不联网、不调用provider、不执行旧脚本或安装工具。不把本地路径／schema／摘要外发。

## 【现有接口与执行命令】

现有`analysis.main`的strategy分支先调用load_w3_context，进而通过planning.verify_review／load_plan_set与feasibility核对固定上游；record_preservation_decision再次核对同一context，匹配才写新run。

- verify有效不等于业务已选preserve_all；准确decision由用户提供。
- record保存scope=S3.5_preserve_all_only和bindings_hash；reject/cancel也可以有合法“记录完成”的success终态，但不能构成执行资格。
- human_review_state=pending不抹去receipt中的明确策略决定，也不表示S6完成。

候选许可编号：P-W3-G35-REAL-RECORD。

固定新run：`outputs/W3/strategy-g35-real-v1-a/`。

固定本地结果文档：`docs/acceptance/results/w3-g35-real-v1-a.md`，及INDEX仅新增导航。

下面为既有入口的命令模板。执行方必须先把decision和actor替换为明确确认的值，向用户展示完整argv并获一次运行许可；不可直接执行尖括号占位符，不默认preserve_all。actor为本地确认者标记，不是身份认证；现有校验只接受ASCII标识形式，可提议`user`表示当前用户，须在准确许可中确认这一映射，不将汉字“用户”直接填CLI导致失败，也不使用synthetic_actor。

用户未给字面确认时间，参数固定not_provided。用户给出的字面值只有能按现有带时区格式无损接受时直接传入；不擅自补时区／秒、不填当前工具时间。格式不相容先报告，不改代码、不把未知时间包装为已确认。

```bash
cd /d/MyPythonProjects/datainsight && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH='D:\MyPythonProjects\datainsight\src' TEMP='D:\MyPythonProjects\datainsight\.cache\tmp' TMP='D:\MyPythonProjects\datainsight\.cache\tmp' TMPDIR='D:\MyPythonProjects\datainsight\.cache\tmp' .venv/Scripts/python.exe -B -m datainsight.analysis strategy --decision <explicit_decision> --actor <confirmed_local_actor> --confirmed-at not_provided --output-dir 'D:\MyPythonProjects\datainsight\outputs\W3\strategy-g35-real-v1-a'
```

如用户提供可直接接受的字面时间，先展示替换后的准确命令另获确认，不在批准后随意更换参数。source／S3不是CLI可变参数，不开放输入路径或换对象。

运行上限：一次strategy入口；自动重跑0、无独立恢复命令、无engine连接／SQL／worker。不跑tests、不再验证离线矩阵。收到叫停停止启动新动作，已经发布的记录不撤改。

## 【输出与本地记录写入】

准确许可覆盖以下新文件：

- `outputs/W3/strategy-g35-real-v1-a/strategy.json`。
- 同run的bindings.json、operation.json、final-status.json。
- 同run必要final-status-success.tmp等原子发布暂存；残留原位保留，不当终态、不自动清理。
- `docs/acceptance/results/w3-g35-real-v1-a.md`：真实批准依据、准确命令／cwd／环境、实际退出／终态、决定与scope、版本／hash引用、遗留项。
- `docs/acceptance/results/INDEX.md`：仅新结果链接，执行者标“待high核对”，不改旧验收或记录。

目标run／结果文档如已存在，停止，不覆盖、不删除，不换名字绕过次数。失败包同样保留；必要写入／发布失败不能因receipt存在而称记录完成。strategy分支有些失败会只有非零输出而无合法终态，如实说明，不补造终态或改成执行成功。

不要增加全产物清单、哨兵范围扫描、hash审计报告、来源copy、原始数据副本、独立authorization功能文件或新runner。准确授权依据可集中到结果文档，现有operation中通用scope不扩权；不为了美化字段改已验收功能JSON。

## 【最小验收：不加矩阵】

- 实际固定核验链成功，S2=accept、S3=approve、唯一方法／计划／完整口径及绑定相符；未打开CSV、未查询、未调用模型。
- 真正用户所选策略被原样记录，actor映射及confirmation_basis有明确依据；document／读取许可不冒充策略选择。
- 新策略scope及bindings_hash匹配实际绑定，必要文件齐全、合法唯一终态，实际命令退出对应；hash用工具结果，不在聊天生成。
- confirmed_at=用户字面值或not_provided；运行工具recorded_at独立及来源明确；历史receipt时间语义保持，不迁移或回填。
- preserve_all只形成策略资格，尚无源读取授权；reject/cancel记录成功后仍停止。任何数据／问题／规则／方法／口径变化、缺终态／绑定失败均不能放行。

反向门控已有R2／R3离线证据，本门不重复跑反向用例。实际运行若触发拒绝，保留真实失败；不是“缺少真实负向演示”就另跑危险输入。

本轮不重新认证W1/W2或重算当前源hash；仅核验既有批准对象的当前保存证据身份。不能宣称源CSV未变、已完成S4/S5或真实业务报告。

## 【权限、停止与一次交回】

本文件的“批准”仅批准交接制作，**不是**P-W3-G35-REAL-RECORD、真实摘要读取、preserve_all或生产计算许可。

low应在只读启动后一次性列明A–F读取范围、用户策略选项、准确actor／时间／完整命令、四文件run与结果文档／INDEX写入、一次次数和停止条件，等待用户明确许可。分别记录三个效力：真实历史证据工具读取、人工策略决定、准确运行／本地写入。它们可以同回复明确批准，但不能互相推定。

若用户仅批准某一项，其余保持等待。不新增核验命令或预先生成approve记录，不自动执行execute子命令。

立即停止条件：范围外引用、现有入口不符、工具版本不符、缺件／核验失败、已有目标、时间口径不兼容、需新文件／功能修复、许可撤回或一次运行已消耗。最小功能修复另批，不在本门修改analysis.py或重新跑命令。

交回一次：结果文档路径、策略run、实际决定／scope、准确argv／退出／终态、必要绑定引用及权限未包含项。详细证据在docs与现有run，对话40行以内，仅给结论／状态／下一门，不复述摘要业务值、不保存讨论／推理，不生成教学交接。

high随后核对G3.5真实记录；即使通过，E3-REAL仍须独立当次生产读取与准确执行许可，S6仍在真实草稿之后独立。本门无新增ADR，W3-v2与旧标准保持。
