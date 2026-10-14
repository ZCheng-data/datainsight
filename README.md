# DataInsight

**面向封闭分析意图、提供可复核结论与证据的受控分析系统。**

当前是个人／小团队的本地受控分析原型：先诊断数据及方法前提，明确人工决定和指标口径，再用确定性工具计算、校验并生成带证据的报告。不是万能分析师，也不无条件保证业务结论可信。

当前案例没有产品模型调用。指定真实案例已完成 **S4确定性计算 → S5三层技术校验 → S6限定解释的独立人工确认**；S6是文档化人工审核，不是自动化产品接口或报告发布。

## 当前状态与权威依据

从[权威结果INDEX](docs/acceptance/results/INDEX.md)进入；历史文档中的阶段状态保留当时语境，当前判定按最新权威记录阅读。

|范围|已验收状态／能力|依据|
|---|---|---|
|W1：S0／S1|固定来源文件体检和原始画像通过|[W1最终验收](docs/acceptance/results/W1-final-acceptance-and-handoff.md)|
|W2-A|固定结构化问题、确定性前提诊断和S2记录通过|[W2-A最终验收v2](docs/acceptance/results/W2-A-final-review-v2.md)|
|W2-B1|封闭候选、完整口径及S3审核通过|[W2-B1最终验收v2](docs/acceptance/results/W2-B1-final-review-v2.md)|
|W2-B2|真实接入停止续作，整体未验收／真实调用暂停；旧C205未满足|[W2状态收尾](docs/acceptance/results/W2-final-state-v1.md)|
|W3|限定离线、G3.5、真实唯一方法计算／S5／本地草稿通过|[W3最终验收](docs/acceptance/results/W3-final-review-v1.md)|
|无模型S6|指定案例的限定业务解释人工确认通过|[S6最终验收](docs/acceptance/results/W4-S6-final-review-v1.md)|

这不表示全项目、全部W4、全量回归、产品v2、LLM Agent或业务效果已完成。本README是交付说明，不是新增运行证据；本次未执行项目、测试、安装或新环境验证。

## 无需运行：阅读一个已验收案例

按下列顺序阅读，不需要重新打开CSV或执行命令：

1. **需求与诊断**：[固定问题JSON](configs/w2a-question-v1.json) → [诊断文件](outputs/W2-A/local-syn-3178ad8b677e49edb91de623be0c3905/diagnosis.json) → [S2执行说明](docs/acceptance/results/s2-accept-3178ad8b677e49edb91de623be0c3905.md)。该诊断目录含`local-syn`，但其输入是历史生产画像，不能据名称认作合成数据。
2. **方法与口径**：[候选方案](outputs/W2-B1/w2b1-candidates-1f9fa1e612fa4c19b48181111a3a35d6/candidate-plans.json) → [S3审核执行说明](docs/acceptance/results/w2b1-review-219e79901d08444bab62c6e61f6e2211.md)。预期输出schema是方案元数据，不是已计算结果。
3. **独立策略**：[真实preserve_all记录](outputs/W3/strategy-g35-real-v1-a/strategy.json) → [G3.5权威判定](docs/acceptance/results/W3-G35-final-review-v1.md)。S3口径批准不自动替代该决定。
4. **真实计算与S5**：[结果](outputs/W3/analysis-e3-real-v1-a/result.json)、[固定SQL／参数与计算证据](outputs/W3/analysis-e3-real-v1-a/calculation-evidence.json)、[三层校验](outputs/W3/analysis-e3-real-v1-a/validation.json) → [E3执行说明](docs/acceptance/results/w3-e3-real-v1-a.md)。
5. **报告与人审**：[本地报告](outputs/W3/analysis-e3-real-v1-a/report.md) → [独立S6人工记录](docs/acceptance/results/W4-S6-human-review-v1.md) → [S6最终验收](docs/acceptance/results/W4-S6-final-review-v1.md)。

原报告及run中的`human_review_state=pending`是生成时状态，原位保留；后续独立S6记录和权威判定表达当前人工确认，不回填历史文件。S6确认不授权外发。

历史W1生产画像／模板重跑与修复后合成收尾是两类证据，不能拼称修复后完整生产CLI实测；新W3真实E3是独立run，不是补跑W1。详见[INDEX的历史证据说明](docs/acceptance/results/INDEX.md)。

## 职责分工

|部分|职责与边界|
|---|---|
|文件与画像工具|本地来源及读取契约核对；原始数据只读，不把原始行放进提示词|
|确定性诊断／封闭方法库|检查意图和方法前提；只接受已注册、已审查版本，不自动创造可执行方法|
|DuckDB|执行固定受信SELECT／WITH并产生业务数值，不由模型计算|
|人工门|S2受理、S3方法／口径、S3.5策略、S6业务解释；每道决定独立，外发另有许可|
|S5与固定宿主报告|执行／口径／边界三层核对，数值和声明绑定工具结果与SQL|
|当前S6|独立文档化人工决定，非S6模块／CLI／JSON执行引擎|

设计依据：[定位与必要证据基线](docs/project-position-and-evidence-baseline-v1.md)。当前无模型与LLM版本的效果／成本比较不适用，未做模型效果实测。

## 环境与已有入口（不是安装快速开始）

已验收环境是Windows本地项目`D:\MyPythonProjects\datainsight`，已有项目`.venv`、Python **3.12.9**／DuckDB **1.4.1**。版本依据[真实E3执行记录](docs/acceptance/results/w3-e3-real-v1-a.md)，本次未重新运行版本命令。

代码位于`src/datainsight`，模块执行依赖`PYTHONPATH`指向项目`src`；测试用途另需`tests`，但本README不运行测试。已有命令使用项目`.venv/Scripts/python.exe -B`、`PYTHONDONTWRITEBYTECODE=1`，TEMP／TMP／TMPDIR集中到项目`.cache/tmp`；DuckDB临时／扩展目录在项目`.cache/duckdb/tmp`和`extensions`，自动扩展安装／加载关闭。

根目录当前没有`pyproject.toml`、`requirements.txt`或通用安装入口；不能使用虚构的`pip install -e .`步骤。本次没有全新机器安装／跨平台验证。历史安装、supervise、verify_record工具不是新读者默认安装入口；需要迁移环境时必须另定范围与许可，不自动安装或迁移缓存。

不存在涵盖全部阶段的统一总CLI：

|模块|已有子命令|参数来源／限制|
|---|---|---|
|`python -m datainsight`|`inspect`、`profile`、`replay`|inspect／profile用固定`--source textbook_userbehavior`及`--output-dir`；replay用`--evidence`及`--output-dir`，来源受控|
|`python -m datainsight.feasibility`|`diagnose`、`decide`|diagnose的`--question`仅允许固定问题文件；decide需诊断引用、实际决定／actor／确认时间及新输出|
|`python -m datainsight.planning`|`candidates`、`review`|固定真实S2链；review需方案引用、实际选择及完整口径确认参数|
|`python -m datainsight.analysis`|`strategy`、`execute`|strategy需实际策略决定／actor／时间；execute需有效策略receipt和新输出|

参数详情应结合实际[入口源码](src/datainsight/__main__.py)、[诊断模块](src/datainsight/feasibility.py)、[规划模块](src/datainsight/planning.py)、[计算模块](src/datainsight/analysis.py)及对应已批交接，不能仅凭子命令名称取得运行权。

### 历史实测示例：仅用于理解证据

以下是[已实测E3的历史命令](docs/acceptance/results/w3-e3-real-v1-a.md)，**不是可直接重跑命令**。其输出目录已存在，再运行会拒绝；README没有授予数据读取或计算许可。

```text
.venv/Scripts/python.exe -B -m datainsight.analysis execute
  --strategy D:\MyPythonProjects\datainsight\outputs\W3\strategy-g35-real-v1-a\strategy.json
  --output-dir D:\MyPythonProjects\datainsight\outputs\W3\analysis-e3-real-v1-a
```

原命令的cwd及完整环境见历史执行说明。新运行必须另行准确批准来源、当前有效批准链、策略、读取动作、命令／环境及不存在的新run；不得仅替换路径就分析任意新数据，不默认业务批准，不覆盖旧run。

## 已验收支持范围与未实现能力

当前证明场是固定`UserBehavior.csv`及[严格读取契约](configs/w1b-read-contract-v1.json)，封闭JSON intent `behaviour_record_counts`／`raw_record`，唯一注册方法`M-BEHAVIOUR-RECORDS`。定义见[planning_methods](src/datainsight/planning_methods.py)。

固定文本pv／fav／cart／buy，NULL→missing，其余非NULL→other；全文件绑定版本、原始记录全部保留。辅助row_count只验证覆盖，不形成占比或新指标。固定问题文件、真实上游批准链和本地路径仍有硬编码限制。

不宣称任意数据／自由文本问题／任意字段映射可分析，其他数据或格式分析未验收；文件层支持不等于已验收Parquet分析。未实现自由SQL接口、通用SQL沙箱、OS硬实时／总内存或全系统网络隔离。当前合作式deadline与固定worker监督只支持已批查询的有限资源控制。

原始记录计数不是订单／支付、独立用户、比例／转化、日期覆盖、总体推广、因果或业务效果。hash只支持字节身份，技术校验不认证源真实性、天然业务语义、总体代表性或协同篡改防御。当前案例S6仅接受这些限定描述和限制，不批准行动。

## 安全与权限

- 原数据只读，先诊断后决定；只有固定受信SELECT／WITH可计算，禁止DDL／DML／ATTACH等管理或写入SQL，不开放用户自由SQL。
- 真实CSV／历史聚合工具读取必须明确本次授权；方法批准、数据读取、模型／网络／付费及外发不能互相推定。
- 四道人工门独立；未知、绑定变化、源身份变化、解析错误、超时、S5或写入失败均停止，不自动改口径／提高上限／重试。
- 新run独占写入，旧证据不覆盖、删除或迁移；同目录原子发布tmp不是成功终态，失败残留保存。
- 不把原始行、标识或密钥写入提示词／报告；当前不调用本地或远端模型。

## 剩余工作与产品v2

[产品v2方向登记](docs/project-v2-directions-v1.md)及[ADR-010](docs/decisions/ADR-010-product-v2-draft-channels-and-current-no-model-S6.md)不是实现或调用许可；产品v2也不是W3验收标准v2修订号。

|方向|归属与状态|
|---|---|
|F-PATH|原W4-C／W2-A可用性扩展：固定问题文件硬编码的受控入口改进，已登记、未实施|
|V2-EXPLAIN|产品v2 W4／S6可选执行后解释草稿；未实施／未验收，不能替代人工确认或工具数值|
|V2-METHOD|产品v2 W5-B入库前方法候选／人审／实现测试／版本发布；未实施，未注册候选永不执行|
|V2-INTENT|产品v2 W5-A执行前意图草稿／人确认；未实施，仍不得跳过确定性诊断及人工门|

旧W2-B2 C205未满足、真实调用暂停保持，不因v2登记放行。W4-B原评测／回归方向仍待定，本次只是交付文档子闭环，没有全量回归／新机器复现或模型比较结果；后续每次单独确定一个最小闭环，不能称全部W4已完成。
