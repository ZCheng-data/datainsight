# W2-A · R1–R4 补测 · sol6.1 low 自包含执行交接 v1

> 仅补测与补证，不改变功能接口或冻结标准。本文由用户请求制作，**不是执行动作授权**。由用户手动转交 low；不创建 Agent／Session，不声称实际模型已切换。

## 0. 可复制启动文字

```text
请只读 D:\MyPythonProjects\datainsight\docs\handoffs\W2-A-R1-R4-sol61-low-v1.md 及其中必要文件，按冻结标准完成 R1–R4 补测。
你负责用户指定 sol6.1 low 执行，不自行最终验收。
先核对测试、功能实现与目录边界；只报告具体冲突，无冲突则按本交接提出 P-RTEST 文件修改权限，等待确认。
本轮只允许申请修改 tests/test_w2a.py 与生成指定的新受控合成 fixture；不改任何功能实现。
只有真实运行失败且确认是功能缺陷，才提出定位到函数的最小实现修复，单独请求授权；不能先改功能再补测，也不能按输出放宽断言。
P-RTEST 不包含命令；测试修改后另申请 P-RRUN，运行本文规定的补测／证据命令。结果文档与 INDEX 另申请 P-RDOC。
不重跑生产 CSV、不重新验收 W1、不修改或移动旧证据、不安装、不联网、不调用模型、不自动进入 W2-B。
对话只给结论与决策点，60 行以内；完成后返回新结果文档和新证据目录，由用户转回规划／验收者复验。
```

## 【目标与前置状态】

一个闭环：独立反向输入 → 真实发布路径故障注入 → 输出哨兵扫描／产物枚举 → 新运行证据 → 交回复验。

W2-A 当前总判定为 **不通过**，依据 `docs/acceptance/results/W2-A-final-review-v1.md`。需要关闭的是 R1–R4，涉及 A02、A03、A12、A13–A15；不是重新设计 W2-A。

正常历史画像诊断与独立 S2 accept 已运行，保留原位。本轮不重新进行真实诊断、真实 accept 或生产计算；受控 fixture 的 diagnose／decide 调用仅用于合成回归及故障测试。

W1 已通过，B01–B09 不重新验收、不重新安装。两项既有接口单测只是有限回归，不称 W1 全回归。W1 历史生产计算和修复后合成收尾仍是两种证据，不合并。

项目根为 `D:\MyPythonProjects\datainsight`。现有 `.venv/Scripts/python.exe`，Python 3.12.9；已安装 DuckDB 1.4.1 不改。本轮补测采用标准库，W1 两项接口单测允许导入既有模块，但不得连接／查询引擎。

## 【权威输入：先只读核对】

必要文档：

- `docs/acceptance/results/W2-A-final-review-v1.md`
- `docs/acceptance/W2-A-v1.md`（frozen）
- `docs/decisions/ADR-003-directory-and-evidence-layout.md`
- `docs/acceptance/results/s2-accept-3178ad8b677e49edb91de623be0c3905.md`
- `docs/acceptance/results/INDEX.md`

必要代码：

- `tests/test_w2a.py`
- `tests/test_w1b_profile.py`：只核对本交接指定的两项接口回归及 import 行为。
- `src/datainsight/feasibility.py`、`feasibility_rules.py`：只读真实被测函数，禁止修改。
- 需要确认既有接口单测依赖时按需读 `profile.py`／`profile_templates.py`，不要运行历史工具。
- `configs/w1b-read-contract-v1.json`：只读，用于生成契约副本；不得修改。

新稿约定沿用 `D:\DataInsight-Prep\insight-agent-planner\SKILL.md`，不采用安装旧技能中自动教学／全阶段交接要求。领域、路径、DeepSeek、D 盘规则不重问。

核对适用 AGENTS.md 与目标当前状态；文件／功能签名有实际变化则报告具体冲突，不能按旧行号盲改。

## 【精确写入范围】

所有相对路径均在项目根内；下面是可申请的范围，不是当前动作许可。

### P-RTEST：唯一可修改的源码位置

**只修改 `tests/test_w2a.py`。**

允许该文件内新增／调整：R1–R4 测试、fixture 生成助手、受控 I/O 包装、补测批次 runner 和只读扫描／证据输出助手。runner 只用于测试与证据，不得成为新功能入口。

- 不改 `src/datainsight/` 下任何文件。
- 不改现有配置、W1 测试、冻结标准、ADR、旧执行记录或旧证据。
- 保留原 W2-A 正常／反向测试；R1 隔离修复原累积错误用例，不删除原需求。
- 不新增项目根 runner、辅助安装脚本或其他测试模块。若实际需要额外文件，停下提出精确增量范围。
- 不先落盘静态 fixture 到 `tests/fixtures/w2a/`；本轮全部新增合成输入由获批测试运行在下述 scratch 范围生成。

### P-RRUN：批次、fixture 与证据命名

工具生成批次 ID：`B = r1r4-<uuid.uuid4().hex>`，后缀是工具实际生成的 UUID，不手填、不冒充运行时间。

- 主证据：`outputs/W2-A/<B>/`。
- 新合成输入：`outputs/_scratch/<B>/<test_method>/`。
- 本轮 CLI／决定等子 run：`outputs/W2-A/<B>-<test_method>-<case_id>/`；既有测试已有 `<B>-cli-<index>`、`<B>-<test_method>` 等后缀可保持，但全部必须使用本轮 B 前缀。
- `<test_method>` 是实际 unittest 方法名；新增方法命名建议 `test_R1_*`／`test_R2_*`／`test_R3_*`／`test_R4_*`，不能取用户输入路径。
- 每个 case_id 固定于测试代码，先列用例清单，不接收任意路径或规则。
- B、scratch 或某子 run 已存在时拒绝复用。下一次运行工具生成新 B，重跑仍需批准。

每个新增 R1／R2 case 的合成包固定放在：

`outputs/_scratch/<B>/<test_method>/<case_id>/profile-package/`

包内文件白名单：

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

case 目录下仅按用例需要新增：

- `read-contract.json`：本用例独立契约副本。
- `question.json`：本用例结构化问题。
- `oversized.json`：受控边界样本；仅边界测试使用。
- `fixture-manifest.json`：受控输入清单／工具摘要／用途，不含真实业务行。

既有测试在新 scratch 下的 `profile-package/`、`question.json`、`oversized.json` 等生成位置可保持。新增包不复制生产数据或生产指纹，使用工具生成的聚合 oracle 与 fixture 版本。哨兵均是人工构造测试标记，不是真实标识。

可在当前用例的未发布 scratch 输入内构造单一错误，但不可修改另一用例输入，更不可修改旧 scratch／证据。缺失场景在创建新包时就省略目标文件，不用删除已生成文件制造缺失。

### 主批次证据文件清单

只在新 `outputs/W2-A/<B>/` 新建：

```text
batch-command.json
batch-environment.json
batch-source-identity.json
batch-result.json
test.log
case-results.json
r3-publication-results.json
r4-read-observation.json
r4-privacy-scan.json
artifact-inventory.json
protected-files-before.json
protected-files-after.json
batch-status.json
source-snapshots/test_w2a.py
```

既有测试在新 B 主目录产生 `cli-finalization-<index>.json`、`decide-fault-<index>.json` 与 `<test_method>-reads.json` 可保留；完整实际文件名写入清单，不称这些文件族就是完整枚举。

子 run 输出只使用被测现有实现的诊断／决定证据与 `final-status.json`，不得回填旧 run。主批次 `batch-status.json` 表示补测／扫描批次状态，不冒充功能 CLI 的 `final-status.json`，也不表示阶段最终验收。

同目录 `.tmp` 是原子发布必要例外：保持在目标 run 同目录／同文件系统，不迁到 `.cache/tmp/`，不当垃圾清理。一般临时工具文件仅在 `outputs/_scratch/<B>/` 或项目 `.cache/tmp/`，不散落根目录。

### P-RDOC：结果文档

测试／补证结束后另行请求：

- 新建 `docs/acceptance/results/<B>.md`。
- 更新 `docs/acceptance/results/INDEX.md`：只增加补测结果链接，标“待复验”，保留当前不通过记录与原执行记录。

不回写 `W2-A-final-review-v1.md`，不把旧不通过记录抹成通过。本文以外新的修复交接／ADR 如有必要，必须另行申请。

## 【被测接口：不修改】

```text
load_accepted_profile(profile_ref, acceptance_ref) -> ProfileSnapshot
main(argv=None) -> int
publish(directory, data)
load_diagnosis(path)
verify_decision(path)
```

功能接口以当前只读源码为准。测试可 patch 常量为新合成路径或包装底层 I/O；这不是改功能实现、扩大生产访问范围或制造产品“新能力”。

## 【R1：独立反向输入】

定位 `tests/test_w2a.py` 的 `test_A02_json_strictness`。

固定 case_id：`extra-key`、`unknown-profile-version`、`bad-reading-schema`。每项有独立 case 目录与合法基线，不复用累积变更。

1. 先用合法同构基线验证 adapter 可正常载入，保留成功证据。
2. 每项仅改一个前提。
3. 分别断言对应 reason_code（当前源码对应 invalid_object_keys／profile_identity／reading_schema）；不是只断言任意异常。
4. 在 `case-results.json` 保存 case、输入身份、基线结果、实际失败原因、预期与实际是否一致。不因真实结果不同而改预期。

原 JSON 重复键、非有限数等反向继续回归，不用新的绿灯掩盖旧项。

## 【R2：契约／文件／引用绑定】

定位 A03 测试与 `load_accepted_profile`。

固定 case_id：

- `contract-digest-mismatch`：合法独立契约副本，单个 evidence 的 read_config_sha256 与实际副本不符。
- `contract-version-mismatch`：独立契约副本 version 不符，证据／其余结构保持合法，测试拒绝读取契约变化。
- `missing-result`：构造时省略 `summary-result.json`；证明真正缺文件拒绝，而非整 read_bytes mock。
- `missing-evidence`：构造时省略 `summary-evidence.json`。
- `evidence-run-mismatch`：仅 summary evidence run_id 不符。
- `evidence-dataset-mismatch`：仅 summary evidence dataset_version 不符。
- `evidence-reference-mismatch`：仅 summary metric evidence_id／引用不符；必须明确实际变更键。

每项先保留合法基线证据；如果需要缺件基线，先在另一 `baseline/` 子目录生成合法同构包，坏包创建时直接省略指定文件。新增 baseline 下只使用同一包文件白名单。

`f.CONTRACT` 与 `f.FIXTURE` 只在当前测试上下文 patch 到本轮新 scratch 中相应路径，退出恢复；真实契约和固定生产源只读不改。expected 契约值保持已批准口径；摘要由工具计算。记录 mock／patch 范围，不能宣称抵御协同篡改。

每项断言对应拒绝原因、没有源 CSV 打开／SQL 执行，既有结果篡改及指纹错配测试继续保留。

## 【R3：两条 CLI 经真实 publish 的故障】

定位两条 A12 CLI 故障测试及发布 helper 测试。新增 case_id 为：

`normal`、`tmp-open`、`tmp-write`、`tmp-flush`、`tmp-fsync`、`tmp-rename`。

分别对 `diagnose` 与 `decide` 执行上述矩阵，全部使用新受控合成输入／新输出。decide 选择 `cancel`、actor=`controlled_test_actor`，不发起新的真实用户决定。

- 保持真实 main 与真实 publish，禁止用整函数 mock publish 当发布故障证明。
- 针对 `.tmp` 文件的打开、写入、flush、fsync、rename 操作注入受控 OSError。包装仅匹配本 case run 的临时目标；其余文件、源诊断、fixture、报告及底层真实方法不受影响。
- 默认对 success／failed 两个终态临时发布均施加该 case 同类故障，验证双重不可写时非零和 failure_evidence_persisted=false；若增加仅成功发布失败、失败终态可发布的辅助 case，须在同一命名范围记录，不替代双重失败用例。
- 测试现有代码真实打开／写入／关闭流程，不能用只记录但不发生的 flush 或 fsync 冒充注入。
- `tmp-open` 可能无残留；write／flush／fsync／rename 失败可留下 `.tmp`。按实际观察记录，不统一断言所有故障都应有残留。
- 每项记录实际 argv、故障定位、返回值、捕获 stdout／stderr、终态、diagnosis 计算状态或 receipt 可用状态、源诊断前后工具摘要、临时路径及残留。
- normal 返回 0、合法 success 终态；故障返回非零、无已发布 success；不能写失败终态时如实报告未落盘。
- 环境／输入允许受控 patch，必须标注合成同进程 CLI 范围，不称真实生产进程实测。
- 已有收尾文件写入故障测试继续回归；新增矩阵补发布路径，不能删除旧故障项或移动 tmp。

若出现错误成功终态、异常逃逸、信息泄露或其他真实功能缺陷：保留失败证据，停止后续“成功交付”，提出定位到函数的最小修复与权限，不改 src。不要声称测试失败必然是功能缺陷；先只读区分测试注入错误和实现问题。

## 【R4：扫描、读取观察与完整清单】

### 哨兵

在新合成输入的允许元数据位置使用受控哨兵（如 source_path／parameters／sql），不在真实数据中植入内容；非法键／类型用例必须标明预期拒绝，不能把 schema 不合法导致测试根本没到输出环节当有效扫描。

固定标记 ID：`SOURCE`、`ROW`、`IDENTIFIER`、`SECRET`、`INSTRUCTION`；测试值格式 `W2A_R1R4_<ID>_SENTINEL`。这些是合成探针，不表示实际密钥或用户记录。

- 合法元数据负载证明标记不进入 diagnosis、receipt 或产品错误／trace，不诱发读文件／执行 SQL／调用模型。
- 原始行探针仅使用合成文本标记，不读取或复制原始业务行。
- 捕获正常与故障 stdout／stderr；所有产品输出／错误及可用 trace 都列入明确扫描清单。
- 扫描报告只记 marker_id、文件／stream、命中位置或计数与判定；不要在测试失败异常或日志中回显敏感探针内容。
- 哨兵注册表、受控输入、测试源码快照允许含合成标记，应单列为 intentional_fixture／test_source，不混为产品泄露。不得把所有报告或所有出错输出都豁免。
- 记录读取／调用观察范围；不读取 `.csv`、不执行保存 SQL、不启动数据库或模型。使用 mock／受控断言验证未调用；静态声明不能冒充独立动态观察。

### 只读保护／枚举范围

新增批次主目录与所有 `<B>-` 子 run，以及 `outputs/_scratch/<B>/`，全部完整枚举。

既有可读证据范围严格限于：

1. `outputs/W2-A/syn-3178ad8b677e49edb91de623be0c3905/` 与名字以 `syn-3178ad8b677e49edb91de623be0c3905-` 开头的旧子 run。
2. `outputs/W2-A/local-syn-3178ad8b677e49edb91de623be0c3905/`。
3. `outputs/W2-A/s2-accept-3178ad8b677e49edb91de623be0c3905/`。

只允许非递归列出 `outputs/W2-A` 的直接目录名以选取上述前缀，不打开其他 run，更不递归扫描全仓／venv／系统缓存／原始数据。枚举前检查组件，拒绝链接／重解析、越界和未知文件族；不跟随它们访问。

- 旧诊断与旧决定目录仅有 JSON 证据；scan／inventory 只读，报告写新主批次。
- 旧文件前后当前工具摘要写 `protected-files-before/after.json`；证明本次补证只读前后不变，不冒充原运行前哈希。
- 功能源码两文件、冻结标准、ADR、原读取契约和原问题配置纳入本次保护身份清单；不授权修改它们。
- artifact-inventory 逐项记录相对路径、类别、文件大小与实际工具摘要（若采用），源头标明 new_synthetic／old_synthetic／historical_profile_diagnosis／real_s2_decision／fixture_input。
- 扫描报告列 scanned_files／streams、明确 exclusion 原因、不可读／遗漏；有限工具返回不得冒充完整。实际枚举失败或扫描发现泄露则批次非成功。
- 清单／扫描报告自身允许排除自摘要，明确“self-referential report”；通过最终目录枚举校验所有实际路径都已覆盖或明确排除，不为追求自摘要无限改写证据文件。
- 旧测试源码快照并不存在就写未知，不猜旧 run 当前源码身份。本次 batch-source-identity 记录当前源码的工具摘要与工具版本；snapshot 保存本次实际测试文件。

扫描／枚举在测试结果汇总后完成；测试失败也尽可能留下真实日志与失败批次记录，但不把扫描成功当测试成功或进入新业务运行。

## 【精确拟执行命令】

**下面的命令定义补测 runner 契约，不表示当前 test_w2a.py 已支持该参数，更不是已执行记录。** 执行者只在 P-RTEST 获批后于该测试文件的 `__main__` 分支实现 `--w2a-supplement`，不新增 runner 文件。

runner 职责：检查环境 → 工具生成 B 并拒绝已存在目录 → 设置 W2A_TEST_RUN → 保存原始 sys.argv／shell 命令转录／环境与测试源身份 → 执行 suite → 生成 R1–R4 证据、扫描／清单／保护摘要 → 保存 batch-result/status → 返回真实退出状态。

suite 精确选择：

```text
test_w2a
 test_w1b_profile.ProfileReferenceTests.test_unknown_template_before_connection
 test_w1b_profile.ProfileReferenceTests.test_result_boundaries_and_nested_types
```

第一项加载完整 W2-A 测试（包含新增补测）；只有两项 W1 接口用例，不 discover W1 全套、不运行安装／生产命令。

拟批准的 Git Bash 命令（单次补测批次）：

```bash
cd /d/MyPythonProjects/datainsight && \
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH='D:\MyPythonProjects\datainsight\src;D:\MyPythonProjects\datainsight\tests' \
TEMP='D:\MyPythonProjects\datainsight\.cache\tmp' \
TMP='D:\MyPythonProjects\datainsight\.cache\tmp' \
TMPDIR='D:\MyPythonProjects\datainsight\.cache\tmp' \
.venv/Scripts/python.exe -B -m test_w2a --w2a-supplement
```

- 不额外运行 diagnose 固定历史输入命令、decide 用户 accept、profile／replay、安装脚本或其他环境。
- 环境核对由 runner 的标准库流程完成，必须记录实际 tempfile、sys.executable、cwd、变量与新 B；不因测试中 mock environment 就宣称真实环境已验证。
- 命令返回 0 仅当测试、R1–R4 必需报告、扫描／枚举和保护检查都成功；否则非零。batch-result 报实际 testsRun、失败／错误、报告状态及 final_acceptance=not_performed，不猜测试数量。
- runner 完整实现作为 tests/test_w2a.py 的新测试支持代码，需 P-RTEST。如执行者不能在该范围实现此入口，停止提出冲突，不擅自改命令或功能模块。
- 本命令的具体 shell 转录和真实 argv、时间、退出状态保存在新证据中；新 run 不能原地重跑，后续每次运行另获批准、新生成 B。

## 【验收与停止】

复验标准保持 `docs/acceptance/W2-A-v1.md`。补证只关闭 `W2-A-final-review-v1.md` 第 4 节 R1–R4，不新增产品决策、不放宽冻结要求。

交回必须能回答：

- R1 每项是否独立且正确原因拒绝？
- R2 是否真正构造了缺件、契约与版本／引用错配，真实固定输入是否未改？
- R3 两条 CLI 是否经真实 publish，底层故障是否生效，失败是否没有 success，tmp 是否原位保留？
- R4 哨兵覆盖、读取／调用观察、实际产物范围是否明确完整，旧证据本次只读前后是否一致？
- 全 W2-A 测试和仅两项 W1 接口回归是否真实成功？
- 新运行日志／命令／退出状态和结果文件是否齐全且不冒称最终验收？

路径冲突、环境错误、测试失败、实现疑似缺陷、泄露、旧文件变化、枚举／扫描失败时停止，不扩大读写权限、不删除失败 run、不自动安装／重试或修复功能。

## 【权限顺序】

1. 用户转交后只读核对；提出 **P-RTEST**：仅测试文件修改，列新增 helper／用例及运行时 fixture 命名，等待确认。
2. 测试修改完成后说明完整命令、批次／fixture／旧证据读取范围，提出 **P-RRUN**，等待确认；它包含本轮生成受控 fixture、运行、只读扫描和新证据写入，不包含功能实现修复。
3. 真实功能失败：保存实际失败证据，只读定位，另提 **P-RFIX** 的最小实现文件／函数修改及复测权限。没有单独批准不得修改；若只是测试注入错误，说明依据并独立申请测试修正／新 run。
4. 完成后提出 **P-RDOC**：新增本次结果文档与 INDEX 链接，等待确认。不自行最终验收。

本文生成许可不等于上述权限已获批；过去 P-IMPL／P-SYN 等是历史记录，不复用。

## 【禁止与完成后】

不读／重跑生产 CSV，不重新验收 W1、不初始化项目、不安装任何包、不联网、不调用模型或外部 API、不移动／删除／覆盖／回填旧证据、不清理 tmp、不自动进入 S3/W2-B、不提交或推送 Git、不自动创建其他 Agent／Session。

所有数值、哈希、耗时、退出状态与测试结果由工具取得；原始数据与真实标识不得进入提示词或输出消息。

完成后交回 `docs/acceptance/results/<B>.md`、`outputs/W2-A/<B>/` 及实际子 run 清单，按 R1–R4／相关 A 项映射证据，报告真实失败及未测项。结果状态为“未验收，待规划／验收者复验”，不得自行把 INDEX 的阶段总状态改为通过。

本轮无新 ADR、无用户业务决策、无额外教学交接。用户转回后由规划／验收者只读新旧证据进行复验，不因补测日志 OK 自动通过。
