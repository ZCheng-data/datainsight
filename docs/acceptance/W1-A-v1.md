# W1-A 验收标准 v1

- 状态：frozen
- 冻结人：用户（依据执行交接引用，不替用户签名）
- 冻结时间：未提供；不得用文档落盘时间替代。
- 批准原文：“确认 W1-A 范围、契约和验收草案，批准 low 按 P1–P3 执行。”
- 规格 / ADR：指定 D:/DataInsight-Prep/insight-agent-planner/references 新稿；ADR-001-W1-scope-and-query-boundary.md；本执行交接的 A01–A10 为冻结依据。
- 本轮目标：选定单文件 → 路径/文件层体检 → JSON 与运行证据。
- 输入：D:/大数据项目/电商用户行为分析/第9章/UserBehavior.csv（精确单文件只读授权）。
- 授权写入：D:/MyPythonProjects/datainsight；输出边界 outputs/W1-A；测试目录 tests/fixtures（非递归枚举）。
- 非目标：内容解析、行数/缺失/基数/时间/重复统计、SQL、画像、业务报告、第三方安装、网络、模型调用、旧项目执行、源文件复制修改、全局环境修改、Git。
- 环境：已有 Python 3.12.9；独立无 pip 环境的实际运行路径由 P3 证据验证。仅标准库。
- 前置门：P1/P2/P3 各动作门确认；失败/权限拒绝/源变化/泄露时停止。

| ID | 验收标准 | 正常/反向 | 阻塞级别 | 真值/期望 | 可重跑命令 | 证据要求 |
|---|---|---|---|---|---|---|
| A01 | 主文件合规 S0 JSON，不声称解析/画像/可分析 | 正常 | 必需 | parse_validation=not_run；无 readable | 下方 CLI | inspection.json |
| A02 | 工具元数据及前后分块 SHA-256；变化停止；记录实际开销 | 正常 | 阻塞 | 哈希对照由工具产生，无预估 | 下方 CLI | fingerprints.json，起止时间/耗时/读取字节 |
| A03 | 候选契约来源及未知项明确，不伪造 schema | 正常 | 必需 | header=false，五列代码预期；其余待验证 | 下方 unittest/CLI | configs/w1a-source.json，inspection.json |
| A04 | 空目录、仅代码无数据候选，不执行代码 | 反向 | 必需 | missing/no_data_candidates | 下方 unittest | test.log |
| A05 | 缺失、空文件、权限不足、读失败、不支持分别报告 | 正常/反向 | 必需 | 不静默成功；权限使用受控 mock | 下方 unittest | test.log |
| A06 | 拒绝 ..、相似前缀、越界链接/重解析、URI、通配符；拒绝前不打开/哈希/枚举目标 | 反向 | 阻塞 | 受控 mock 不访问未授权目标；标记真实平台覆盖 | 下方 unittest | test.log；未测范围说明 |
| A07 | 越界输出/已有输出拒绝；文件名指令不扩权 | 反向 | 阻塞 | 独占输出，无任意操作入口 | 下方 unittest | test.log |
| A08 | JSON/日志/交回无原始记录、标识值、伪造统计或业务结论 | 反向 | 阻塞 | 本地合成敏感哨兵扫描；不展示真实记录 | 下方 unittest；P3 本地扫描 | test.log，privacy-check.json |
| A09 | 无产品模型/网络调用、无需 key；测试/演示路径网络阻断并记录观察 | 正常/反向 | 阻塞 | 本 Python 进程观察不称系统隔离；代码检查补充 | 下方 unittest/CLI | network-observation.json，test.log，static-check.json |
| A10 | 标准库校验结构/状态；环境、输出、可控缓存在 D 盘；实际命令/退出状态 | 正常/反向 | 阻塞 | 不安装校验库，工具实际值 | 下方命令 | environment.json，commands.json，manifest.json |

## 实际入口与必要进程变量（Git Bash）

以下是实现后的可重跑命令，不代表已经成功运行。RUN 必须指向批准输出根内新建的空目录。目录创建也是授权动作，不复用既有输出文件。

```bash
export TEMP='D:\MyPythonProjects\datainsight\.cache\tmp'
export TMP="$TEMP" TMPDIR="$TEMP"
export UV_CACHE_DIR='D:\MyPythonProjects\datainsight\.cache\uv'
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH='D:\MyPythonProjects\datainsight\src'
'D:/MyPythonProjects/datainsight/.venv/Scripts/python.exe' -B -m unittest discover -s 'D:/MyPythonProjects/datainsight/tests' -p 'test_w1a.py' -v
'D:/MyPythonProjects/datainsight/.venv/Scripts/python.exe' -B -m datainsight inspect --source textbook_userbehavior --output-dir "$RUN"
```

## Windows PowerShell 等价入口

```powershell
$env:TEMP='D:\MyPythonProjects\datainsight\.cache\tmp'
$env:TMP=$env:TEMP; $env:TMPDIR=$env:TEMP
$env:UV_CACHE_DIR='D:\MyPythonProjects\datainsight\.cache\uv'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONPATH='D:\MyPythonProjects\datainsight\src'
& 'D:\MyPythonProjects\datainsight\.venv\Scripts\python.exe' -B -m unittest discover -s 'D:\MyPythonProjects\datainsight\tests' -p 'test_w1a.py' -v
& 'D:\MyPythonProjects\datainsight\.venv\Scripts\python.exe' -B -m datainsight inspect --source textbook_userbehavior --output-dir $RUN
```

## 必需限制及停止线

不递归扫描教材目录，不打开来源教材代码、不继承业务解释。不解析源内容。扩展名仅识别候选格式。missing、unsupported、unreadable、needs_configuration 按交接区分；W1-A 不产生 readable。

真实链接覆盖与 mock 必须分开记录。网络保护仅测试与演示 Python 进程，不宣称全系统隔离。JSON 结构验证不等于数据可解析或结果业务正确。

环境不可用、权限拒绝、既有文件冲突、源变化、边界无法验证、测试失败或输出泄露时停止相应步骤，保留失败证据，不删测试、不跳边界、不改为有条件通过。

执行结果单独保存 docs/acceptance/results/<run_id>.md；总判定固定为“未验收，待验收者判定”。本文件不回写测试结果。文档生成时间如需记录，单列工具时间，不作为冻结确认时间。
