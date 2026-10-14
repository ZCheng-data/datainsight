# W4-B交付文档子闭环：sol6.1 low自包含交接 v1

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

- 状态：accepted（有限文档契约）；README／结果记录／INDEX写入仍待精确许可。
- confirmation_actor：用户。
- confirmation_basis：用户批准当前版本“只补README、不新增功能或重跑回归”的最小闭环，以及本交接／最小标准新建；low随后申请准确写入范围。
- confirmed_at：not_provided。
- recorded_at：null；recorded_at_source：not_available；recorded_at_status：unavailable。
- recorded_at_reason：本批仅文件工具，无可信精确记录时刻，不执行取时或估计。
- authorization_scope：P-W4B-DOC-PLAN仅本交接及W4-B-doc-v1标准新建；不授权README、结果文档或INDEX写入、命令／数据工具读取／发布。
- bound_versions：[W4-B-doc-v1](../acceptance/W4-B-doc-v1.md) frozen、当前定位、ADR-003／005／007／008／009／010、W3／S6权威验收。

## 【目标】

只补本地README交付说明：读者能顺着一个已验收固定真实案例找到需求诊断、方法／口径、策略、计算／S5、报告及独立人工S6记录，准确理解环境／已有CLI／限制／v2方向。

不重跑，不把文档完成称作全量回归或全新环境验证。不新增功能、方法、依赖配置／包装、模型调用、自动发布或S6产品接口。

## 【角色与前置状态】

你是用户指定sol6.1 low执行角色；按文档范围执行，不假装切换模型，不创建Agent／Session，不自行验收通过。

W1、W2-A、W2-B1、W3和无模型S6限定案例已通过。指定案例S4→S5→S6闭环完成，但不是全部W4完成、业务效果证明、S6产品自动化或LLM Agent。W2-B2停止真实接入续作、整体未验收，旧C205未满足；产品v2三通道仅正式方向。

项目根：`D:\MyPythonProjects\datainsight`。当前项目已有`.venv`，Python3.12.9／DuckDB1.4.1来源于已验收记录，不在本轮重新运行版本命令。规划只读检查未见根README.md、pyproject.toml和requirements.txt；执行前用文件工具定向检查目标，若有新内容不要覆盖。

## 【启动和准确文档许可】

先只读本交接、冻结标准和下列必要文件。说明本批只写三处准确目标，申请P-W4B-README-DOC-V1：

1. `D:\MyPythonProjects\datainsight\README.md`：新建。
2. `D:\MyPythonProjects\datainsight\docs\acceptance\results\w4-b-doc-v1-a.md`：新建简洁交回。
3. `D:\MyPythonProjects\datainsight\docs\acceptance\results\INDEX.md`：仅新增本批导航／状态，不追改旧记录。

获批后一句话通知，连续完成README、静态核对和结果导航，一次交回high；不按小段拆批。仅文档写入，不执行任何shell／Python／CLI／test／hash／安装／网络命令，包括--help也不跑。

目标README或结果文档已存在则停，不默认覆盖或另换名称。许可可以允许该次新建README在交回前按J401–J408修正静态措辞／链接，不包括旧文件内容重写、无限迭代或功能修复。明确一次文档批次即可，无运行次数／付费配置。

## 【只读输入：定向，不全仓扫描】

权威状态与设计：

- `docs/project-position-and-evidence-baseline-v1.md`。
- `docs/project-v2-directions-v1.md`及ADR-008／009／010必要章节。
- `docs/acceptance/results/INDEX.md`作为导航，不将其历史段落旧状态当当前真值。
- `docs/acceptance/results/W1-final-acceptance-and-handoff.md`。
- `docs/acceptance/results/W2-A-final-review-v2.md`。
- `docs/acceptance/results/W2-B1-final-review-v2.md`。
- `docs/acceptance/results/W2-final-state-v1.md`。
- `docs/acceptance/results/W3-offline-final-review-v1.md`、`W3-G35-final-review-v1.md`、`W3-final-review-v1.md`。
- `docs/acceptance/results/W4-S6-human-review-v1.md`、`W4-S6-final-review-v1.md`。
- 必要历史环境／命令说明可读取以上文档链接中的具体执行结果.md，不重读全部run日志。
- 原W4-B归属可读准备包`D:\DataInsight-Prep\insight-agent-planner\references\roadmap.md:90–96`；本轮不改准备包。

入口静态核对：

- `src/datainsight/__main__.py`：inspect／profile／replay。
- `src/datainsight/feasibility.py`：diagnose／decide和固定问题入口。
- `src/datainsight/planning.py`：candidates／review、固定真实S2链。
- `src/datainsight/analysis.py`：strategy／execute、固定真实链／源与当前S5／草稿。
- `src/datainsight/planning_methods.py`：唯一method／metric定义。
- `configs/w2a-question-v1.json`、`w1b-read-contract-v1.json`：无原始行的问题／读取契约。

现有报告／run／receipt只需README链接和静态存在性，优先依据权威结果，不打开生产CSV或工具读取真实聚合包做新核验。确需读取报告正文而超出当批明确文件许可，先说明准确文件目的，不复用旧数据动作授权。

文件存在性用Read／Glob精确路径；禁止根递归通配导致扫描.venv／cache／所有outputs，禁止全产物清单／扫描范围报告／独立hash。不得读取密钥、.env、原始行／ID、旧淘宝项目或账户。

## 【README最小内容契约】

1. **定位和当前状态**：采用已批准定位；当前无产品模型。写出哪些阶段／案例通过，W2-B2未验收／停止续作单列，不概括为“全项目／全部W4完成”。
2. **无需运行的案例阅读入口**：README→权威INDEX→问题／诊断→候选／口径→策略→真实结果／SQL／S5→report→独立S6审核／最终判定。给有限路径，不复制整批证据或全部run目录。
3. **架构职责简图或表**：程序确定性前提／封闭方法、DuckDB数值、人工四道门、固定宿主报告；S6当前是文档化决定，不是产品CLI。
4. **环境与入口**：已有Windows本地项目venv、已验证版本、src／PYTHONPATH及D盘可控缓存规则。当前没有打包配置／通用安装入口，不写pip install -e .或虚构requirements。历史install_w1b／supervise／verify_record工具不是新读者快速开始，不能给作默认安装步骤。
5. **命令说明**：可以列既有模块／子命令及参数来源；推荐仅一段已实测历史execute示例，并明确“历史证据，非可直接重跑命令”。新运行需独立源读取、有效批准链、新输出及精确许可，不能把历史目标换成任意新数据。
6. **支持／硬编码限制**：已验收固定CSV读取、封闭intent JSON、唯一M-BEHAVIOUR-RECORDS、固定问题文件／上游批准链／本地路径，其他格式／数据／intent／字段映射不宣称可用；通用SQL沙箱未实现。
7. **证据与解释边界**：原始记录计数不是订单／支付／用户／比例／转化／日期／效果；hash和技术校验不认证源真实性／总体代表性，案例S6仅有限本地人工接受。原report pending与后续独立确认记录不冲突。
8. **安全及权限**：原始数据只读；SELECT／WITH仅受信模板；四道人工门与外发独立；未知／变化／失败停下；禁止覆盖旧run。真实读取许可不是方法／外发许可。
9. **未完成与v2**：V2-EXPLAIN／METHOD／INTENT只登记未实施，阶段归属清楚；F-PATH硬编码缺陷、W4-B评测／回归方向待定、不消失。无模型与LLM比较不适用，不能写模型效果实测。

README保持易读、以导航和准确能力说明为主，详细契约用链接。不强制大段重复验收文档，业务数字可全部省略；若引用，必须已有工具文档来源，不新增比率、估计或心算。

## 【验收：J401–J408与反向静态检查】

冻结标准为`docs/acceptance/W4-B-doc-v1.md`。交回需逐项列准确依据／文件路径：

- J401定位／状态；J402已验收案例链；J403环境／CLI；J404命令与许可；J405支持／缺陷；J406证据／数字；J407 v2及回归待定；J408文档保护／链接。
- 反向拒绝：“已接入模型”“任意数据／问题都支持”“准确率X%”“新机器安装已经验证”“S6自动化完成”“全部W4完成”“可直接运行历史输出命令”“回归全通过”等无依据宣传。
- 静态核对所有核心README文档链接／路径存在；内部引用用README所在根目录的相对路径。源码依据按实际模块和符号，不编造函数或统一总CLI。
- 无新运行证据，仅文档核对；不为验证命令去跑CLI，也不为演示再读CSV／重做人工决定。

若发现关键能力与实际实现不符，修改本次README措辞使其如实，不修改功能去适配文档。引用失效若需更改旧证据／范围外文件，停止，不搬移run补链接。

## 【交回记录／INDEX与时间】

新建`docs/acceptance/results/w4-b-doc-v1-a.md`：本批权限／实际文档动作、J401–J408实际静态检查与证据映射、没有命令／数据／网络动作、遗留项；执行方标“未验收，待high文档验收”，不自行通过。

按ADR-005保存confirmation_actor／confirmation_basis、confirmed_at用户字面值或not_provided、recorded_at独立工具时间；文件工具没可信时刻则null／unavailable说明，不另跑取时命令、不以文件mtime／会话日期／旧运行时间代填。不复制完整聊天或推理。

INDEX仅新增本批结果导航，历史判定／run不改。README不是新增业务运行证据，不生成outputs run、日志runner或manifest。不要把文档动作伪造成回归tests输出。

## 【禁止与停止条件】

不改src／tests／configs／frozen／ADR／旧结果／outputs／环境／缓存，不新增pyproject／requirements／lockfile或安装脚本；不运行命令、SQL、画像、hash、模型、网络、发布、Git提交／推送，不创建Agent／Session或教学交接。

当目标已存在、许可缺失、需要额外文件／命令／来源、关键证据不可定位或想扩大原功能／回归范围时停止。用户叫停停止新写入动作，已有文档不自动删除；失败如实交回，不无限修正或启动v2。

一次交回README、结果记录与INDEX路径、静态判定／遗留和未运行说明；对话40行以内。规划／验收者只读检查后给该文档子闭环结论，不把它当完整W4回归完成。
