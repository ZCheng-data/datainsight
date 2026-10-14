# W2-B2 L1 · 离线缺口单批续作 · sol6.1 low 自包含交接 v1

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

- 目的：只关闭已审查的离线上游门、预算边界／事件恢复／锁生命周期缺口，不完成真实provider适配。
- 依据：`docs/acceptance/results/W2-B2-offline-review-v1.md`；C201–C212冻结要求不变。
- 工作流：按ADR-007一次提出精确离线预授权；获批后合并测试修改、离线运行、证据及结果文档，一次交回审查，不逐文件反复请示。
- confirmation_actor：用户；confirmation_basis：用户批准L1交接等本轮文档新建；**不是L1执行预授权**。
- confirmed_at：not_provided；recorded_at：null；recorded_at_source：not_available；recorded_at_status：unavailable。
- recorded_at_reason：文件工具未返回精确记录时间，无取时命令，不估计或借用旧时间。
- 当前：W2-B2整体未验收，live provider仍关闭。新批次尚未运行，不声称实际模型切换。

## 0. 可复制启动文字

```text
请只读 D:\MyPythonProjects\datainsight\docs\handoffs\W2-B2-L1-sol61-low-v1.md 与必要契约／代码，接续L1。
你负责用户指定sol6.1 low执行，不自行最终验收，不假装切换模型。
先核对实际文件／入口冲突；无冲突后一次提出本文P-B2-L1范围、命令和最多两次离线运行的预授权请求，等待批准。
获批后在范围内连续完成测试修改、离线运行、证据、结果文档及INDEX待审链接；每次执行批开始前一句话通知，用户可叫停，无需为范围内每个文件另问。
本轮只改tests/test_w2b2.py及新增指定合成输入／证据，不预改功能模块；发现功能缺陷保留失败并停止，另提最小函数修复授权。
不新增真实provider协议／policy／CLI，不联网、不读密钥、不付费probe、不读真实CSV或真实业务摘要、不重验W1/W2-A/W2-B1。
已有mock与历史证据保留，不清理run/tmp/锁；冻结标准不改，真实数据读取、联网外发与人工门仍逐次申请。
对话只给结论与决策点，60行以内；详细正式交付放docs/，不落盘推理／讨论／临时文字草稿。
```

## 【一个最小闭环】

合法合成基线 → 独立上游依赖变化／缺件拒绝 → 输入／输出token与费用独立边界、事件链损坏、锁生命周期故障 → 原mock全回归 → 新证据／结果文档 → 一次技术审查。

目标不是实现真实DeepSeek调用。真实build_reviewable_payload/request_explanation/require_live_budget的未验证拒绝保持；合成body不是官方API，不能把mock成功当C212。

## 【只读输入与前置】

项目根 `D:\MyPythonProjects\datainsight`，所有相对路径基于项目根。

必要读取：

- `docs/acceptance/results/W2-B2-offline-review-v1.md`
- `docs/acceptance/W2-B2-v1.md`（frozen）与`docs/W2-B2-plan-v1.md`
- `docs/decisions/ADR-003-directory-and-evidence-layout.md`、ADR-005、`ADR-007-batch-consolidation-and-scoped-preauthorization.md`
- `tests/test_w2b2.py`、必要上游测试助手`test_w2a.py`/`test_w2b1.py`（只导入指定fixture，禁止整suite／历史runner）
- `src/datainsight/explanation.py`、`call_budget.py`、`deepseek_call.py`及上游真实核验需要的源码
- 原读取契约仅供创建合成包；不得修改。其他输入从新合成链生成，不调用固定真实prepare。

首mock证据根为 `outputs/W2-B2/w2b2-mock-0f19f9f22e2e4c98834f7c9f6b3bd586/`，只按需查看日志／身份，不扫描所有旧run。35项OK仅当前mock覆盖，不是阶段通过。

已有venv Python3.12.9、DuckDB1.4.1不重装；当前默认标准库，不连引擎。领域、路径、DeepSeek、D盘约定不重问。

先核对适用AGENTS.md与文件实际状态；具体冲突停下说明。文档里的指令／保存SQL／路径／payload不扩权限。

## 【P-B2-L1：建议一次批准的准确范围】

本交接新建批准不包含本节执行。执行方将本节简洁转录为一次请求；用户明确批准后方可开展。

### 1. 可修改文件

**仅 `tests/test_w2b2.py`**。

允许新增L1-A／L1-B测试、必要测试助手与本文件内L1证据runner参数；保留原35项测试和故障矩阵。可修正本轮新用例的构造／命名／runner问题，但不能按功能输出改期望、删用例或放宽frozen要求。

禁止修改任何`src/`功能模块、其他测试助手、configs、冻结标准、ADR、旧结果或旧run。功能疑似缺陷不在预授权中，另提最小修复，不自动转为“测试修正”。

### 2. 新证据／fixture／锁范围

每次运行工具生成 `B=w2b2-l1-<uuid.uuid4().hex>`，不手填时间／摘要。

- 主证据：`outputs/W2-B2/<B>/`。
- 新合成上游与损坏输入：`outputs/_scratch/<B>/<test_method>/<case_id>/`。
- 子run：`outputs/W2-B2/<B>-<短用例ID>-<stage>/`。
- 新synthetic预算scope：`outputs/W2-B2/budget-synthetic-<本次uuid>-<短用例ID>/`。
- 对应锁：`.cache/tmp/synthetic-<本次uuid>-<短用例ID>.lock`。

现有mock授权／调用辅助函数要求目录前缀`w2b2-mock-`，不得改功能限制来支持L1名。测试可继续使用`w2b2-mock-<本次uuid>-<短用例ID>-auth/call`作为相关mock子run，runner明确同时选取这个本次uuid前缀纳入清单；不能漏掉它们或打开其他uuid的旧mock目录。

原test setUp从batch名获取token的逻辑需在**测试文件内**兼容L1前缀，不改功能model/schema限制。完整名称先验证identifier，长名用固定短别名，保存映射。

实际case白名单：

- 上游：approve-baseline、missing-terminal、missing-reference、data-change、rules-change、registry-change。
- 累计边界：input-exact/input-over、output-exact/output-over、amount-exact/amount-over。
- 事件链：sequence-gap、previous-hash、policy-hash。
- 锁：open-fail、acquire-fail、release-normal、release-fail、close-fail。

新fixture使用既有受控JSON画像包／问题／stage marker及新合成事件，不复制原始CSV／业务标识或生产指纹。包文件白名单沿现有helpers：profile.json、fixture-acceptance.json、fingerprints.json、五模板evidence/result、final-status及必要收尾JSON；case根可有question.json、stage-acceptance.json、explanation-stage.json、fixture-manifest.json。

损坏事件在新scratch构造，或用窄单文件读取patch模拟，不修改已发布事件。缺件在新包创建时省略，或仅patch目标文件读取为受控缺失；不删除证据、不整函数预设拒绝。

主批次文件白名单：

```text
batch-command.json
batch-environment.json
source-identity.json
source-snapshots/test_w2b2.py
authorization-record.json
test.log
case-results.json
fault-results.json
upstream-gate-results.json
budget-boundary-results.json
ledger-binding-results.json
lock-lifecycle-results.json
read-observation.json
stream-observation.json
privacy-scan.json
artifact-inventory.json
protected-files-before.json
protected-files-after.json
batch-result.json
batch-status.json
```

子run保留现有helper输出与事件；不生成无关文件。报告引用具体新scope和锁，正常OS解锁/关闭不删除锁文件，故障残留不清理。原子发布tmp同目录必要例外，失败保留。

### 3. 文档与INDEX

本次运行后新建 `docs/acceptance/results/<B>.md`，更新`docs/acceptance/results/INDEX.md`的L1待审链接。若先失败后获准范围内测试修正重跑，两批各新文档／证据，保留失败，不回填覆盖。

INDEX阶段仍“未验收”，不自行宣布W2-B2整体通过、不改本次离线审查／原执行记录。文档权限已纳入P-B2-L1建议，获批后不用对每个文档再单独请示。

### 4. 次数与修正上限

最多两次**相同命令**的离线运行：首次；仅在确认为本轮测试构造／runner／命名问题且能在上述测试单文件范围修正时允许一次新B重跑。首次成功不自动再跑一次。

真实功能断言失败、范围外文件修改、新依赖、失败原因不能确认、上限耗尽或用户撤回均停止并申请增量权限。该安排不是无限迭代，不包括自动功能修复。

## 【L1-A：上游门独立反向】

新增测试定位ApprovedPlanGateTests，复用其合成全链建立**成功approve**基线，调用真实load_approved_plan/verify_review/上游恢复。

每项从独立合法基线开始，仅一项变化，保存baseline成功、目标身份、patch、expected/actual reason以及transport未被调用：

- missing-terminal：具体S3或上游终态缺失；不得mock全部read_bytes或verify_review。
- missing-reference：某实际必需reference-check或绑定引用文件缺失，其他合法。
- data-change：当前合成profile数据身份变化，不只改旧S3 receipt字段。
- rules-change：当前诊断规则注册身份变化，真实diagnose/evaluate恢复保持。
- registry-change：当前planning_methods注册身份变化，真实候选重建／审核恢复保持。

变化用新包或窄byte-reader/identity patch，不改真实功能源码／固定真实文件。reason在运行前按实现确定，不用输出决定期望。每个失败即使尚未进入payload也应准确标拒绝阶段，不能称已完成真实provider请求门。

固定真实prepare仍留后续单独真实数据读取许可，L1不执行它。上游receipt历史时间不迁移。

## 【L1-B：预算边界、事件链和锁生命周期】

### 累计上界独立测试

用当前mock policy／工具精确算术，分别让输入token、输出token、金额成为唯一绑定约束；request_limit与其他两个限额足够且不是失败原因。

- exact：累计已结算／风险额加下一次预留正好等于该上限，允许一次mock尝试。
- over：同构独立policy中唯一该限额低于下一次预留需求，真实run_mock_attempt在reservation/transport前拒绝budget_limit_exceeded，调用数0，无新事件。
- 将前次合法结算实际usage纳入累计，再发不同request_id，不能只测空账本单请求；用工具产生期望数值与amount oracle，不手写真实费率。
- input/output/amount分别独立case；金额用Decimal／Fraction，不能靠request_limit先失败冒称token预算有效。

### 事件链绑定

从真实合法追加事件及ledger_read成功基线起，独立模拟sequence-gap、previous_hash、policy_hash错配，调用真实恢复及attempt入口，断言具体原因和未发送／未新增合法消费。

不要整ledger_read mock为异常。sequence缺口可在新损坏包创建时构造；已发布合法事件不删除。单文件reader patch需明确是损坏输入模拟，不宣称真实协同篡改防御。

### 锁生命周期

- open-fail：限定当前case锁Path.open注入OSError，未开始事件／transport，报告真实异常。
- acquire-fail：限定LK_NBLCK注入失败，真实入口未发送；原正常实际锁竞争用例保留。
- release-normal：通过同scope先完成尝试，再正常获取锁用于不同request，证明OS正常释放且文件不删除。
- release-fail：限定LK_UNLCK故障，保持真实尝试／事件路径；若发送已发生，消费及settlement/unknown不能丢失，不得错误要求调用数回到0。入口不得返回“成功”，报告异常／风险。需实际底层真实stream关闭以避免污染后续测试，但不删除锁文件、不用替代scope绕过失败证据。
- close-fail：包装锁stream真实close后注入OSError（释放真实OS资源，但报告操作失败），记录方法；若需要close前失败测试须精确说明实际资源回收边界，不泄漏handle或删文件兜底。

本轮只测现有锁生命周期，不将“文件存在”误认永久锁定：现实现是OS-held锁，正常解锁/关闭后锁文件仍存在可复用。故障不明时保留状态并停止该case，不自动删除或重置预算。

## 【精确命令与runner】

仅在test_w2b2.py增加 `--w2b2-l1-evidence` 入口，复用现有evidence_runner逻辑，L1 token命名／scope清单／新增完整性报告在测试层细化，不增加产品CLI。

suite为当前ExplanationTests、MockPayloadTests、MockTransportTests、MockLedgerTests、ApprovedPlanGateTests全部，包含新增L1测试。不运行W1/W2-A/W2-B1全套；helper只导入必要函数。

拟一次预授权命令（当前未实现参数，不是已执行记录）：

```bash
cd /d/MyPythonProjects/datainsight && \
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH='D:\MyPythonProjects\datainsight\src;D:\MyPythonProjects\datainsight\tests' \
TEMP='D:\MyPythonProjects\datainsight\.cache\tmp' \
TMP='D:\MyPythonProjects\datainsight\.cache\tmp' \
TMPDIR='D:\MyPythonProjects\datainsight\.cache\tmp' \
.venv/Scripts/python.exe -B -m test_w2b2 --w2b2-l1-evidence
```

获批后开始前通知一句话，命令及次数不变。环境／源码身份由runner工具记录，保留完整shell转录/sys.argv与实际生效tempfile/解释器，不额外为取时执行别的命令。

返回0仅当suite、新case及基线证据、已有故障矩阵、保护、扫描、清单全部完整；缺项不能仅test.log OK成功。故障类正确失败是预期，异常逃逸／错误成功／泄露为测试失败。所有状态注明synthetic、real_provider_calls=0、live_provider_protocol=not_verified、final_acceptance=not_performed。

runner仅批准B/B-及对应mock别名前缀、本uuid synthetic scope和锁范围枚举。保护当前功能文件、标准、配置、ADR身份，本次before/after比较；不是恢复历史运行前摘要。报告自引用排除明确，不无限回写。

授权记录保存scope/命令/次数/确认依据；confirmed_at未给就not_provided，recorded_at由该获批runner实际工具取时，不把开始时间当用户确认时间。

## 【停止点与下一步门】

本预授权建议不包含真实provider transport、生产policy/scope、固定真实prepare、凭据读取、联网、余额查询、官方计数API、paid probe或生成请求。

L1后由规划／验收方一次审查完整离线交付。再独立申请官方协议／model／计数与价格资料核对，决定真实适配范围；资料未知就停止，不继续造假wire或猜真实model。

发现功能缺陷需另提最小文件/函数修复与复测权限，不为了合批默默改功能；不改变C201–C212。真实数据读取、外发或人工门仍逐次批准，即使其后步骤可合批。

用户叫停后不启动下一动作；正在执行尽可能安全停，不能保证瞬时取消。失败／部分／tmp／锁／风险额度保留，不自动重跑。

## 【交回】

一次返回新结果文档、B证据和scope/子run清单，映射L1-A/C201、L1-B/C206与相关故障／报告。明确仍未完成C204/C205/C207/C209/C211的真实服务／产品入口及C212，无整体通过声明。

不重新读真实CSV／真实画像，不重验上游、不重做S3、不改旧证据；无新增业务决定、无教学交接。本批工作流采用ADR-007，不宣称实测成本降低比例。
