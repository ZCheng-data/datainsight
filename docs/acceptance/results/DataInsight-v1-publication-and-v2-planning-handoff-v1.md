# DataInsight新对话交接 v1：v1发布前只读检查与v2解释草稿规划

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

## 1. 交接性质与本轮权限

本文件保存已审定状态、准确导航、用户新的下一步意图及权限边界，不是聊天转录、推理草稿或新的运行验收。它含本地路径，仅本地交接使用，**不得直接作为GitHub公开文件或外部模型payload**。

- confirmation_actor：用户。
- confirmation_basis：用户因上下文增大要求制作新对话交接；明确下个产品部件先选解释草稿，计划先发布v1至GitHub；发布前检查必须在新对话做，本对话不检查、不上传。
- confirmed_at：not_provided。
- recorded_at：null；recorded_at_source：not_available；recorded_at_status：unavailable。
- recorded_at_reason：本轮仅文件工具，没有可信精确记录时刻；不执行取时、不估计或借用历史时间。
- authorization_scope：仅本交接新建及必要既有正式状态文档只读；未更新INDEX、README、ADR／标准或旧证据，未做发布前扫描、Git命令、运行、联网、修改.gitignore、提交或上传。

## 2. 最新接续结论（不从零重验）

**当前指定真实案例已完成S4→S5→S6，W3／限定无模型S6通过；README交付文档通过。没有产品模型真实接入。** 这不是全部W4、通用异构分析、产品S6自动化或LLM Agent完成。

用户新增顺序：

1. 新对话先做v1的**发布前只读检查**，仅交清单与建议，不执行修复或上传。
2. 若仍要发布，由用户后续另批必要本地整改、发布范围与准确GitHub动作；意图不是动作许可。
3. 下一产品功能优先选择**V2-EXPLAIN执行后解释草稿**进行有限规划。专项契约、模型标准及付费／外发安排尚未制定冻结，不能直接沿旧W2-B2调用。
4. V2-METHOD／V2-INTENT仍只方向登记，不同时实施；F-PATH缺陷保持。

下表相对路径均基于项目根`D:\MyPythonProjects\datainsight`。

| 范围 | 当前权威状态 | 入口 |
|---|---|---|
| W1：体检／画像 | 通过，不重装、不重验 | docs/acceptance/results/W1-final-acceptance-and-handoff.md |
| W2-A：固定intent／确定性诊断／S2 | 通过 | docs/acceptance/results/W2-A-final-review-v2.md |
| W2-B1：唯一候选／口径／S3 | 通过 | docs/acceptance/results/W2-B1-final-review-v2.md |
| W2-B2 | 离线限定证据保持；真实解释接入停止续作，整体未验收／真实调用暂停，旧C205未满足 | docs/acceptance/results/W2-final-state-v1.md；ADR-008 |
| W3限定离线 | 通过，R3闭合必要增量，不再补审计矩阵 | docs/acceptance/results/W3-offline-final-review-v1.md |
| G3.5真实策略 | preserve_all独立记录通过 | docs/acceptance/results/W3-G35-final-review-v1.md |
| W3整体：真实S4／S5／草稿 | 按W3-v2通过，范围内无补测／重跑 | docs/acceptance/results/W3-final-review-v1.md |
| 无模型S6限定人工确认 | H601–H606通过，指定案例闭环完成 | docs/acceptance/results/W4-S6-final-review-v1.md |
| README文档子闭环 | J401–J408通过，不等于新机器／回归验证 | docs/acceptance/results/W4-B-doc-final-review-v1.md |
| W4-B独立冻结回归集／可复用入口 | 保留待办，首次相关功能变更时合批建设，当前不另开回归批 | docs/acceptance/results/W4-B-regression-scope-decision-v1.md |

`docs/acceptance/results/INDEX.md`是本地历史／结果入口。旧“待high／未完成”是当时语境，当前以随后权威判定为准，不回写旧结果。README及INDEX现已链接多个本地run；以后仅挑部分outputs公开可能产生缺链接或不可运行固定核验链，发布前检查要明确列出这一后果，不移动／删除原证据来修链接。

## 3. 固定约定与最小能力（不重问）

- 定位：**面向封闭分析意图、提供可复核结论与证据的受控分析系统**；个人／小团队本地原型。
- 项目根：`D:\MyPythonProjects\datainsight`。不是新会话默认工作区。
- 准备包：`D:\DataInsight-Prep\insight-agent-planner`，仅参考新稿，不是发布仓库或可自动改动的目录。
- 生产CSV：`D:\大数据项目\电商用户行为分析\第9章\UserBehavior.csv`；原始只读，新对话没有读取／计算许可。
- 旧淘宝项目：`D:\MyPythonProjects\taobao-behavior-analytics`，不扫、不运行，不沿用清洗结论。
- 规划／验收：用户指定sol6.1 high，制定契约、核对证据，不写功能代码、不跑项目、不假装切模型。
- 执行：用户手动转交sol6.1 low，获准确批次许可后实施；不自动创建其他Agent／Session。
- DeepSeek产品选择保持；准确provider／model／mode、真实费率／余额／预算尚未冻结，不猜或默默换服务。历史20–30元计划不是余额／消费授权。
- 环境已有项目.venv、Python3.12.9／DuckDB1.4.1；不重装或建环境。所有新增可控文件／缓存按批准D盘范围，不迁移全局缓存。
- 当前唯一注册方法：M-BEHAVIOUR-RECORDS；计划P-BEHAVIOUR-RECORDS，固定JSON intent为behaviour_record_counts／raw_record。
- 指标为一条原始读取记录，按pv／fav／cart／buy精确文本分类，NULL→missing，其余非NULL→other；全文件绑定版本，无分母／比例／日期。全保留、不去重、过滤、填补、trim或改大小写。
- 当前CLI仍固定问题文件和真实上游链／本地来源；不是任意JSON路径、任意数据或开放问题空间。F-PATH为已知可用性待办。
- S6是独立文档化人工确认，不是新增产品CLI／JSON终态。原report及run里的pending保留生成时历史语义，后续独立决定表达当前已确认状态。
- 根README已存在且静态验收通过。最近交付核对未见根pyproject.toml／requirements.txt，未验证新机器／打包安装；新对话若相关再定向核对，不推定永远不存在。

## 4. 必要证据与权限基线

执行规则与新稿：`D:\DataInsight-Prep\insight-agent-planner\SKILL.md`及references、已批准ADR／后续变更。安装旧同名skill的自动教学／多角色会话／模型切换要求不覆盖用户的新稿和明确边界；平台／Agent系统约束仍优先。

- 一次只推进一个有限闭环；原始行、标识值（包括hash／伪匿名ID）、逐用户特征、密钥不得进提示词或交回聊天。只能用schema、聚合摘要、安全工具证据。
- 数值、字节大小、hash、费用与耗时由工具取得／计算；没有依据unknown，不能估算成实测。
- SELECT／WITH仅受信模板；禁DDL／DML／ATTACH／COPY／INSTALL／LOAD／SET等，不接自由SQL，不宣称通用沙箱。
- 缺少它会导致错误结论、越权／泄露、不可逆损坏或未授权费用才必要；仅改善审计便利则不要求。保留实际字节／版本绑定、人工门、路径边界、不覆盖、唯一终态／原子发布和必要正常／反向。
- 不再为验收堆跨run完整产物清单、哨兵扫描范围报告、多次独立恢复或精确token／chat_template补证；发布检查的目录／敏感候选清单是本次明确交付，不借此重开全系统审计。
- ADR-003：outputs原位、失败同样保留，禁止覆盖／移动／删除／回填；run同目录.tmp是必要原子发布例外，不能当success或自动清理。
- ADR-005：技术判定方承担技术条款认证；用户批准范围／目的／安排。confirmed_at未提供则not_provided；recorded_at独立工具值，无可信时刻null/unavailable，不复用历史时间或会话日期。
- ADR-007：受控离线动作合批、范围／命令／次数／修复限额明确预授权；真实数据／摘要工具读取、网络／付费／凭据和人工门仍独立。
- 旧frozen不默默放宽，变更另版／必要ADR；当前旧C205仍不满足，不因产品v2方向或风险口径登记说旧标准通过。
- 对话40行以内，仅结论／判定／决策点；正式细节获批放docs，不保存讨论／推理／临时文字草稿。不自动教学交接、建Session／Agent、commit／push或发布。

## 5. 关键真实案例与历史层次

发布时用户倾向只提交一个真实案例run，这是**偏好而非已批准提交白名单**。

- v1真实结果run：`outputs/W3/analysis-e3-real-v1-a/`，七项必需产物bindings／result／calculation-evidence／validation／report／operation／final-status。
- 报告：该run的report.md；S6记录：`docs/acceptance/results/W4-S6-human-review-v1.md`，权威通过另见W4-S6-final-review-v1。
- 真实策略run：`outputs/W3/strategy-g35-real-v1-a/`。
- 固定S3候选／审核、S2、历史诊断及画像的必要引用已在bindings／对应交接白名单中。只选真实E3一个run不必然足够让现有固定CLI重新核验或让README所有链接有效。
- 最后W1生产画像／模板重跑：`outputs/W1-B/final-20261009T061339601505Z/`，修复前协议。
- W1修复后合成收尾：`outputs/W1-B/b09-finalization-20261009T063948192695Z/`，没有再次生产计算。
- W3 R2：`outputs/W3/offline-w3-e3o-r2-b/`，历史incomplete保持；R3：`outputs/W3/offline-w3-e3o-r3-a/`，补必要策略／配置／deadline和最小回归后限定验收通过。

当前数据版本和已验收报告身份详见W3／S6权威记录；发布检查不需要重读生产CSV或计算新数据hash。文件中有本机路径、SQL参数、真实聚合与业务审核依据，不因为已脱离原始行就自动可公开。

## 6. 新对话第一闭环：GitHub发布前只读检查

**本对话尚未执行以下检查，没有路径／大文件／敏感候选扫描结果或发布通过结论。** 新对话按用户要求只给清单和建议，不自动整改或上传。

### 6.1 用户明确要求的四项输出

| 检查项 | 必须交回的内容 | 不可偷换为 |
|---|---|---|
| 所有硬编码绝对路径 | 源码／配置／文档（含根README及根脚本等实际相关文本）文件相对路径、行号、路径类型、用途、是否影响运行或仅历史证据、建议处置；Windows、UNC、POSIX等形式和转义表达按实际文件查 | 不只搜一条D盘前缀，不把schema／SQL引用本地路径漏成“无绝对路径” |
| 会被提交的大文件>1 MB与敏感候选 | 先明确实际／候选提交集合，再用工具大小列相对路径、精确字节、忽略／追踪／候选状态及建议；敏感候选仅类别／位置，不回显值 | 不把工作区全部大文件当作一定会提交，也不把没有Git上下文当可认证的提交名单 |
| outputs提交策略 | 对用户“只交一个真实run”倾向给出明确建议、所需引用依赖、公开敏感性、阅读演示与实际可重跑能力取舍 | 不默认提交全部历史run／原数据；不默默删旧证据或宣称单run就支持全部CLI |
| .gitignore新增建议 | 根据实际Git状态／目录提出精确条目和保留例外、顺序／父目录规则影响，说明已跟踪文件不受新ignore撤销 | 不修改.gitignore、不git rm／reset／clean、不暂存或提交 |

>1 MB阈值要注明单位和准确字节，不凭后缀估大小；必要时说明十进制MB／二进制MiB差异，避免漏边界。hash／大小工具结果不得编造。

### 6.2 范围与工具安排

- 首先定位项目根和适用AGENTS／CLAUDE规范，按需核对Git是否存在、已有.gitignore、已跟踪／暂存／未跟踪状态、目标发布模式及实际目录。**当前Git初始化、索引、remote、分支、历史和公开／私有状态均未在本轮查证**，不得猜。
- “准备上传”不是git init/add/commit/push、创建仓库、设置remote或网络认证许可。若需要只读Git命令／本地元数据扫描，先列准确命令、cwd、范围、次数与停止条件并取得许可；不得运行项目、安装或访问网络来完成静态发布检查。
- 为列提交候选允许在获批范围内枚举文件路径／大小；不跟随越界链接，不打开外部生产CSV。venv／cache／下载／scratch可按提交相关性查元数据，不能把它们当源码全量内容读取。
- 文本路径查找应覆盖实际发布候选源码、配置、docs、README和必要根脚本；文档历史路径不能因“只读证据”漏掉。outputs真实run正文／摘要检查属于新真实聚合工具读取，单独准确许可，不复用既有验收许可。
- 敏感候选包括凭据／.env／私钥／认证URL／邮箱或姓名等个人线索、本机用户名／目录、raw行／标识值、低频或真实聚合、开发环境／命令日志、账单与授权记录等，是否实际存在由检查结果决定。
- 凭据值／原始行／标识不能进提示词／聊天，检查工具只返回相对位置、类别和必要脱敏说明；不要为了检查让用户贴密钥。无法安全检查的区域注明未覆盖，不称零敏感或发布安全。
- 如.git历史已存在，说明当前文件检查是否覆盖历史对象；当前无敏感不证明过去commit无敏感，ignore也不能清除历史。需要历史扫描时另列范围，不无边界全审计或自动改写历史。
- 不把README文档静态通过、S6本地确认或v1案例验收当GitHub公开发布授权；外发应按最终选择的提交内容和目标由用户再确认。

### 6.3 outputs与.gitignore：待检查后给建议

当前只登记判断原则，不提供伪实测提交结论：

- 可优先讨论“有限已审核案例展示包”，避免默认将所有outputs、venv／cache、tokenizer下载、scratch、故障／调试包发布。单一真实E3 run可能仍含绝对路径和真实业务聚合，须审阅。
- 若只发布E3 run，应区分“阅读展示证据”和“现有固定CLI可在公开仓库独立重跑”；后者依赖上游链及批准对象，不能随意抽掉引用后仍宣称可跑。
- 需要公开脱敏展示时，单独新建／导出展示文件或后续调整公开说明，保留原run／hash证据不改；这属于未来整改许可，不在首轮只读检查执行。
- 对不可提交原证据做ignore不等于本地删除。README／INDEX若链接被排除文件，要报告断链和披露取舍，不能将未提交证据用作读者可取得的公开证明。
- .gitignore建议依据实际候选集合；可讨论.venv／.cache／__pycache__／IDE文件／凭据候选及outputs默认排除＋精确保留，但不在本轮写入，不假定ignore生效于已追踪文件。

新对话最终首先返回四项清单和具体建议、阻塞／未覆盖范围、用户需决定的真实提交范围。检查结果不自动形成发布许可或整改命令。

## 7. 发布安排之后：V2-EXPLAIN先规划，不复活W2-B2

用户最新优先级为先做执行后解释草稿部分。方向依据：`docs/project-v2-directions-v1.md`及ADR-010；历史“优先级尚未选”保留其当时语境，本交接记录新选择。

- 归属：产品v2 W4／S6可选部件，S4工具结果及S5通过之后，独立S6人工决定之前。
- 已批准的是未来角色例外和方向；专项功能契约、payload、provider／mode和模型W4标准未冻结，未实现／验收，无API许可。
- 不是恢复旧方案解释请求，不移动ADR-004／006授权；旧W2-B2整体未验收／C205未满足保持。
- 模型只组织已核验工具值／口径／限制的解释草稿，不能计算、舍入、新增指标／方法、订单／支付／转化／因果效果或批准行动；结构合法不能认证全部自然语言语义。
- 先明确最小解释价值、输入／数值引用、宿主校验／渲染、最小正常／反向和人审，再设计付费风险／协议另版；保留现有无模型底座和旧结果。
- DeepSeek准确目标／费率／余额／累计数字未知不得填；本地门只限请求次数、已知消费及后续发送资格，不称在途单次费用硬上界。未知计费暂停；风险许可不能让用户为未验证保证签认证。
- 不自动重开官方token计数／tokenizer／chat_template查证、下载、安装或付费probe。确需新增资料／工具先列准确范围和许可，不把静态synthetic账本当真实usage／结算验收。
- 第一次相关功能变更时，按已确认W4-B回归决定合批建设受控新batch合成回归入口及受影响最小反向，不提前另开全量回归或同时做方法发现／入口翻译。

此节只为下一规划导航，不给low执行指令。先完成第一只读发布检查、由用户作发布／整改安排；v2只读设计的正式文档获批后再交low。

## 8. 按需读取导航

新对话优先：本文件→README→INDEX当前权威入口→回归范围决定→产品v2方向／ADR-010。不要重复读全部旧验收／run，当前状态已审定。

核心文件：

- README.md。
- docs/project-position-and-evidence-baseline-v1.md。
- docs/project-v2-directions-v1.md。
- docs/acceptance/results/W3-final-review-v1.md。
- docs/acceptance/results/W4-S6-final-review-v1.md。
- docs/acceptance/results/W4-B-doc-final-review-v1.md。
- docs/acceptance/results/W4-B-regression-scope-decision-v1.md。
- docs/decisions/ADR-005-approval-responsibility-and-confirmation-time.md。
- docs/decisions/ADR-007-batch-consolidation-and-scoped-preauthorization.md。
- docs/decisions/ADR-008-closed-intent-evidence-baseline-and-W3-boundary.md。
- docs/decisions/ADR-009-W3-evidence-calibration-and-minimal-offline-closure.md。
- docs/decisions/ADR-010-product-v2-draft-channels-and-current-no-model-S6.md。

源码按检查目的定向阅读src/datainsight中的入口、源／方法／口径、analysis、旧budget／provider边界；不要执行历史root安装脚本、tests runner、.venv或cache内容。

## 9. 可复制的新规划对话启动文字

```text
请先只读 D:\MyPythonProjects\datainsight\docs\acceptance\results\DataInsight-v1-publication-and-v2-planning-handoff-v1.md，按新稿和已批准ADR接续。
你负责用户指定sol6.1 high规划／验收，不写功能代码、不跑项目、不假装切模型、不创建其他Agent／Session。
W3、无模型S6指定真实案例闭环及README文档已通过，不从零重验、重装或重跑CSV。
下一功能优先V2-EXPLAIN执行后解释草稿；当前先做v1 GitHub发布前只读检查，不实施v2、不上传。
请给四项清单和建议：源码／配置／文档所有硬编码绝对路径；实际或候选提交集合中>1 MB文件与敏感候选；outputs提交策略（我倾向只提交真实E3案例run）；需要新增的.gitignore条目。
该检查此前未做，Git状态／提交集合未知不能猜；读取真实outputs摘要和命令检查先列准确范围获取许可，不读CSV或密钥值入提示词。
只给清单／建议和未覆盖范围，不修改文件、.gitignore、原run或Git索引，不init/add/commit/push、不联网／创建GitHub仓库。
旧C205不满足，W2-B2真实接入停止续作，不重复tokenizer／官方计数查证，不付费probe；v2专项契约／标准／付费和外发另版。
原W4-B独立回归集保留待办、首次相关功能变更合批建设；不为当前收尾再开回归矩阵。
保留封闭intent／方法、工具算数、四道人工门、路径与不覆盖、字节版本绑定；必要证据按已批准基线，不加审计级完备性。
confirmed_at和recorded_at按ADR-005分开；技术判定由规划／验收方承担，用户不替未验证条款认证。
对话40行以内；细节正式落盘另获批准，不保存推理／讨论／临时草稿。下一执行或公开发布范围由人决定并另行授权。
```

## 10. 本轮交付自检与停止

- 已保存当前权威判定、历史语义、真实案例和原生产／合成分层。
- 已登记用户新优先级与v1发布意图，不把它当API或Git动作许可。
- 已列新对话发布前四项交付和只读边界，**没有执行检查或伪造清单**。
- 已保留outputs单run提交偏好及依赖／敏感性／断链需要判断，不替用户决定最终提交范围。
- 已保留W4-B变更触发回归、F-PATH和其他v2方向，不默默删待办。
- 本轮仅新建本交接，不更新INDEX、README、旧标准／证据，不扫描大文件／路径／敏感候选、不改.gitignore、不运行Git／项目、不联网或上传。

用户手动新建对话并复制第9节启动文字。后续真实扫描／发布／v2实现均由该对话列明准确许可，本交接不是通用续作授权。
