# W2-B1 · T1–T2 补测 · sol6.1 low 自包含执行交接 v1

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

- 当前阶段判定：不通过，依据 `docs/acceptance/results/W2-B1-final-review-v1.md`。
- 本交接目的：只关闭 T1 上游依赖变化拒绝、T2 本阶段已有输出保护，关联 B103／B108／B109／B112。
- 文档权限依据：用户对 P-B1-TDOC 回复“批准”，仅授权本文件新建。
- confirmation_actor：用户；confirmed_at：not_provided。
- recorded_at：null；recorded_at_source：not_available；recorded_at_status：unavailable。
- recorded_at_reason：本轮文件工具未提供精确记录时间，没有执行取时命令，不估计或用会话日期代替。
- 本交接不是测试修改、运行或实现修复授权；不自动创建 Agent／Session，不声称切换实际模型。

## 0. 可复制启动文字

```text
请只读 D:\MyPythonProjects\datainsight\docs\handoffs\W2-B1-T1-T2-sol61-low-v1.md 及必要代码／文档，接续 T1–T2 补测。
你负责用户指定 sol6.1 low 执行，不自行最终验收，不假装切换模型。
先只读核对，报告具体冲突（无则写无），提出 P-B1-TTEST：仅修改 tests/test_w2b1.py，等待确认。
测试修改获批不包含命令；修改完成后另申请 P-B1-TRUN，生成新受控 fixture／证据并运行本文命令。
不改功能实现；只有真实运行失败并定位为功能缺陷，才提出最小函数修复，单独申请 P-B1-TFIX。
不重跑生产CSV、不重验W1/W2-A、不重做真实S2或S3批准、不安装、不联网、不接DeepSeek、不移动／修改／删除旧证据。
标准 B101–B112 保持冻结，补测仅限 T1–T2；不加入时间字段重构或历史迁移。
新记录与结果文档按ADR-005分开 confirmed_at与recorded_at；工具时间不能冒称用户确认时间。
对话只给结论与决策点，60行以内；结果文档另申请权限，交回用户转给规划／验收方复验。
```

## 【目标与前置状态】

一个最小闭环：合法受控上游链＋成功候选／审核 → 独立依赖变化／已存在输出反向 → 新测试及证据 → 交回复验。

正常候选、固定真实 S2 核验与独立真实 S3 approve 已运行。本轮不是重新生成真实候选或重新approve，不进行生产计算。现有业务决定不因补测需要而重发。

W1与W2-A通过，不重装、不重新从零验收。项目已有Python 3.12.9与DuckDB 1.4.1；本轮使用标准库，允许两项既定W1接口回归导入既有模块，不连接／查询引擎。

项目根：`D:\MyPythonProjects\datainsight`。所有相对路径基于项目根，不是聊天工作区。

## 【输入：只读核对】

- `docs/acceptance/results/W2-B1-final-review-v1.md`，尤其第4节T1／T2。
- `docs/acceptance/W2-B1-v1.md`（frozen）。
- `docs/handoffs/W2-B1-sol61-low-v1.md`、`docs/W2-B1-plan-v1.md`。
- `docs/decisions/ADR-003-directory-and-evidence-layout.md`、`ADR-005-approval-responsibility-and-confirmation-time.md`。
- `tests/test_w2b1.py`：当前测试、chain助手、短run别名、runner。
- `tests/test_w2a.py`：仅必要fixture／I/O观察／发布故障助手，禁止修改或运行其整套runner。
- `src/datainsight/planning.py`、`planning_methods.py`、`feasibility.py`、`feasibility_rules.py`：只读被测逻辑。
- `configs/w1b-read-contract-v1.json`、`configs/w2a-question-v1.json`及behaviours模板定义：只读必要契约，不运行查询。
- `tests/test_w1b_profile.py`：只核对两项必要接口回归的依赖与读写行为。

旧执行记录 `docs/acceptance/results/w2b1-review-219e79901d08444bab62c6e61f6e2211.md` 和成功批次 `outputs/W2-B1/w2b1-syn-60e61a5474ca4536bca9a5fff29487e4/` 的命令／源码身份可按需只读引用；不自动枚举全部旧run，不在旧目录运行任何测试。

真实候选与审核目录不属于本补测写入范围；不用它们作覆盖测试或修改依赖。原真实CSV不属于读取范围。适用AGENTS.md及文件实际状态先核对，发现实际冲突停下报告，不根据旧行号盲改。

## 【精确写入范围】

### P-B1-TTEST：唯一可修改文件

`tests/test_w2b1.py`。

允许新增T1／T2用例、必要测试助手及本文件内证据runner入口，复用原有全阶段正常／反向测试。原测试及故障矩阵保留，不删断言、不放宽期望，不改既有上游helper文件。

禁止修改 `src/datainsight/`、其他测试、配置、冻结标准、ADR或旧结果。无需新增静态fixture、根目录runner或新依赖。目标有实际变化／需要额外文件先提出冲突。

### P-B1-TRUN：新批次与fixture命名

工具生成 `B = w2b1-t1t2-<uuid.uuid4().hex>`。UUID由实际运行工具取得，不手填，不把它当运行时间。

- 主证据目录：`outputs/W2-B1/<B>/`。
- 新输入：`outputs/_scratch/<B>/<test_method>/<case_id>/`。
- 合成输出：`outputs/W2-B1/<B>-<短别名>-<case_id>-<suffix>/`。
- case_id固定于测试代码，禁止任意路径输入。
- suffix白名单：s2diagnosis、s2receipt、source-candidates、candidates、review、target。
- 新增方法建议 `test_T1_dependency_changes`（别名t1）、`test_T2_existing_output_protection`（别名t2）。原测试短别名保留。
- 创建前验证**完整拼接名称**符合现有identifier长度／格式；不能为测试改功能限制。过长就缩短测试别名／case_id并记录映射。
- 所有新run和scratch不得复用已存在目录；下一次重跑新B且另获批准。失败run保留、不清理。

T1固定case_id：data、rules、registry。T2固定case_id：candidates、review、newrun。

每项fixture包：`outputs/_scratch/<B>/<test_method>/<case_id>/profile-package/`，文件白名单：

```text
profile.json
fixture-acceptance.json
fingerprints.json
summary-evidence.json        summary-result.json
columns-evidence.json        columns-result.json
behaviours-evidence.json     behaviours-result.json
duplicates-evidence.json     duplicates-result.json
timestamp-evidence.json      timestamp-result.json
final-status.json
reference-check.json
environment.json
network-observation.json
cli-command.json
```

case根下可按现有chain助手生成 `question.json`、`stage-acceptance.json`、`fixture-manifest.json`；仅已有边界回归生成oversized.json。新增预期缺件通过新包创建时省略，不删除既有文件。上游版本来自合成工具数据，不复制生产CSV、生产指纹或原始业务值。

### 新批次证据文件

```text
batch-command.json
batch-environment.json
source-identity.json
source-snapshots/test_w2b1.py
test.log
case-results.json
fault-results.json
read-observation.json
privacy-scan.json
artifact-inventory.json
protected-files-before.json
protected-files-after.json
t1-dependency-results.json
t2-existing-output-results.json
authorization-record.json
batch-result.json
batch-status.json
```

当前runner已有证据文件名可复用，新增只限上表；子run使用现有功能／上游helper的证据文件，不添加无关调试文件。T2的待保护目录可以先生成 `marker.json`，只写当前测试的新target，不写任何旧run。

一般临时产物只在新scratch或项目 `.cache/tmp/`；原子发布 `.tmp` 必须在目标run同目录／同文件系统，是必要例外，不迁移／自动清理。对话推理、讨论与临时文字草稿不落盘。

### P-B1-TDOC-RESULT：运行后文档

另外申请新建 `docs/acceptance/results/<B>.md` 和更新INDEX待复验导航。保留当前不通过判定、原执行记录、首次失败与成功批次，不回写它们，不自己改为通过。

## 【被测接口：不修改】

```text
planning.load_s2_accept(decision_ref)
planning.build_candidate_plans(context, registry)
planning.load_plan_set(path)
planning.verify_review(path)
planning.new_run(value)
planning.main(argv=None)
feasibility.rules_module.registered_rules()
planning_methods.registered_methods()
```

上游helper常量可在测试上下文限定patch到本轮scratch／W2-B1合成目录，退出恢复；真实核验／生成／恢复函数保持调用，不用整函数mock替掉要验证的行为。

## 【T1：当前依赖变化，不只是保存字段变化】

每个case独立建立完整合法上游链，生成成功candidate和受控S3 receipt（建议cancel，actor=controlled_test_actor）。先实际 `load_s2_accept`、`load_plan_set`、`verify_review` 成功，保存基线身份。

随后只改变一个**当前依赖**，原candidate／receipt／manifest保持原字节：

### data

针对本case合成profile输入的dataset_version／数据身份提供变化字节，或者构造新版本包并让当前依赖指向它；不要只改旧S3 receipt.dataset_version。

最小可行测试允许单文件读取patch提供改变的profile.dataset_version，由真实adapter拒绝与既有acceptance／evidence／manifest不一致。记录实际生效对象及拒绝原因。若需要构造内部一致的新版本链，须保持旧批准绑定不动；不重建旧批准来掩盖失效。

### rules

通过受控patch让当前 `feasibility.rules_module.registered_rules()` 返回新的版本／hash身份（使用工具计算的新合成摘要），保留原数据与已保存诊断不动；调用真实load_diagnosis的规则重建路径。不只修改保存diagnosis中的ruleset_hash。

patch应只改变身份，不替换diagnose／evaluate／load_diagnosis为预设拒绝。记录真实拒绝原因，证明现有批准不再匹配当前规则。

### registry

让当前 `planning_methods.registered_methods()` 返回新的registry身份，保留已有candidate／receipt内容与数据不动；不只改旧candidate.registry_hash。真实方法生成／load_plan_set重建继续运行，核对旧计划及审核被拒绝。

若改变的是注册表字节源，可用限定单文件读取patch；若直接patch注册函数返回值，明确这是当前registry身份模拟，不宣称真实源码部署变更已发生。

### 每项必须检查

- 旧AcceptedContext／旧registry输入的复用或旧上下文重建被拒绝。
- 旧候选 `load_plan_set` 恢复拒绝。
- 旧审核 `verify_review` 恢复拒绝。
- 保存合法基线、实际dependency、patch范围、每条入口、expected／actual reason_code、旧文件本次前后摘要。

原因由只读实现确定，不能先运行再把输出写成期望；有不同但正确的拒绝阶段应说明技术依据，不按字符串凑通过。不要在data失败后叠加rules错误，每项必须新链。

**重要语义：** 有效的新数据／新规则／新registry配合新的批准，可以在后续授权流程生成新的候选。本测试验证的是旧上下文／旧批准失效，不要求程序永久拒绝所有新版本；不能为了补测改成禁止任何新版本。

## 【T2：本阶段已有输出保护】

分别在新case建立合法受控链。review使用合法成功candidate作为源，先核对其恢复有效；不能用上游错配代替已有输出拒绝。

1. 创建当前新target目录，保存marker或当前已完成合成证据；对其文件集合与实际字节计算before身份。
2. candidates与review各调用真实 `planning.main`，将output-dir指定该已存在target。review使用受控cancel，不重新发起真实用户approve。
3. 断言非零、reason_code=output_exists；target文件集合、大小／摘要与before完全一致，不能新增final-status／tmp或其他文件。
4. `newrun` case直接调用真实 `planning.new_run` 对已存在新target，断言output_exists且不变。
5. 限定观察写入模式，确认拒绝路径未打开target写入；报告stdout／stderr、退出、终态存在性及本次before／after清单。
6. 旧source candidate本次前后摘要不变，范围只包括新测试文件／run，不触碰真实历史review或候选。

监控层不得故意使写入失败然后把OSError当output_exists通过；断言应观察真实入口自行在写入前拒绝。标记文件仅属于当前获批受控case，不是覆盖旧证据授权。

## 【精确拟执行命令】

当前尚无下述参数入口；P-B1-TTEST获批后仅在 `tests/test_w2b1.py` 的runner／__main__中增加 `--w2b1-t1t2-evidence`。不是新的功能CLI或当前可执行能力。复用既有证据runner逻辑、只增加T1/T2报告与完整性检查，不实现通用框架。

suite固定为：

```text
PlanningLogicTests 全部
PlanningChainTests 全部（含新增T1/T2）
test_w1b_profile.ProfileReferenceTests.test_unknown_template_before_connection
test_w1b_profile.ProfileReferenceTests.test_result_boundaries_and_nested_types
```

不discoverW1/W2-A全套，不调用test_w2a补测runner。导入共享helper允许，但不执行helper模块的__main__。

P-B1-TRUN拟批准的单次Git Bash命令：

```bash
cd /d/MyPythonProjects/datainsight && \
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH='D:\MyPythonProjects\datainsight\src;D:\MyPythonProjects\datainsight\tests' \
TEMP='D:\MyPythonProjects\datainsight\.cache\tmp' \
TMP='D:\MyPythonProjects\datainsight\.cache\tmp' \
TMPDIR='D:\MyPythonProjects\datainsight\.cache\tmp' \
.venv/Scripts/python.exe -B -m test_w2b1 --w2b1-t1t2-evidence
```

命令不能在实现前或获批前执行。runner实际记录项目cwd／sys.executable／tempfile／变量，工具生成B并设置W2B1_TEST_RUN；保存完整shell转录、真实sys.argv、测试源码快照／摘要、功能模块与原标准／配置保护身份。

返回0必须同时满足全suite、T1三项的基线／依赖变化拒绝、T2三case内容保护、既有故障矩阵及扫描／清单／保护检查。测试数量、耗时、摘要与退出状态由工具取得，不手填。报告标final_acceptance=not_performed，批次成功不等于阶段通过。

功能模块、原读取契约／问题、冻结标准及ADR保护前后必须不变。扫描／清单仅覆盖本轮B主目录、B-子run和新scratch；不为了保护记录无界扫描旧run。旧证据只读引用需要什么另明确列出，不增加真实入口重跑或旧目录迁移。

报告自引用排除明确，产品输出不能笼统豁免。测试失败也保存真实日志／失败状态，停止后续成功交付；新一次运行需新B和新许可，不原地重跑或回填。

## 【记录与时间：ADR-005】

新授权／结果模板使用本文件开头责任声明。authorization-record简洁记录当批真实批准内容、scope及标准／交接版本，不保存完整聊天或模型推理。

- 用户给出确认字面时间则原样保存；未给出 confirmed_at=not_provided。
- 获批执行工具另取实际记录时间为recorded_at并给时间来源，任何情况下不得冒充confirmed_at。
- 记录时间是工具操作时间，不是用户消息时刻；不能把保存时间或运行开始时间倒填为确认时间。
- 受控合成审核仍按现有功能schema提供其测试confirmed_at参数，明确 synthetic_test_input、not_user_confirmation；它不是实际用户决定或新时间规范迁移。
- 不改当前功能schema、timestamp校验或旧receipt；不把时间字段重构加入T1／T2，不增加新时间验收要求。

## 【权限门与停止条件】

1. **P-B1-TTEST**：先只读核对、列新增用例／测试支持变更，仅修改test_w2b1.py，等待用户批准。
2. **P-B1-TRUN**：修改后提出上述真实完整命令、新输出／fixture范围、观察与保护名单，等待批准；一次合成批次，不接真实入口。
3. **P-B1-TFIX**：真实失败后只读判断测试注入错误还是功能缺陷。确认功能缺陷才提出最小文件／函数修复与复测许可；未单独批准不得改功能。测试修正／重跑也另请权限，不按失败结果放宽断言。
4. **P-B1-TDOC-RESULT**：交付时申请新结果文档与INDEX待复验链接，保留当前判定，等待批准。

路径冲突／环境错误／测试失败／旧文件变化／不完整证据／泄露时停止；保留真实失败，不自动安装、联网、重试、清理或改标准。

## 【禁止与交回】

不读或重跑生产CSV，不重验W1/W2-A，不重新发起真实S2/S3批准，不运行生产profile/replay／历史安装或RECORD脚本，不修改功能实现、原配置、冻结标准、ADR或旧证据，不移动／删除／清理失败run或tmp，不联网、不调用DeepSeek／外部API、不做Git提交或自动会话协作。

完成后交回 `docs/acceptance/results/<B>.md` 和 `outputs/W2-B1/<B>/`，映射T1–T2与B103/B108/B109/B112证据，报告真实命令／退出、未测／patch范围、保护与扫描。执行结果标“未验收，待规划／验收者复验”，不自行修改阶段为通过。

本轮无新ADR、无用户业务决定、无教学交接；当前不通过不因交接创建消失。用户手动转回新证据后由规划／验收方依据冻结标准复验。
