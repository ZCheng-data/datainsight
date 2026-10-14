# W2-B2 tokenizer 静态审查 v2：限定补证通过，C205 仍未满足

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

## 1. 当前判定与权限

**限定静态补证：通过。范围内阻塞项：无。**

**C205：仍未满足。W2-B2 整体：未验收。真实调用保持关闭。**

前次小型配置、完整模板、demo 和必要有限结构的提取缺口已经关闭；模型适用、服务包装与完整计费输入的可靠上界仍无证据。静态交付完整与计数安全门满足是两个不同结论。

- 冻结标准：[W2-B2-v1](../W2-B2-v1.md)，C201–C212 不改。
- 原审查：[tokenizer-static-review-v1](W2-B2-tokenizer-static-review-v1.md)，当时不通过原文保留，不回填。
- 补证交接：[原包离线静态补证](../../handoffs/W2-B2-tokenizer-static-supplement-sol61-low-v1.md)。
- 补证执行：[tokenizer-static-supplement-7f9c82d4a6034b71b18d0d12e609c5ae](tokenizer-static-supplement-7f9c82d4a6034b71b18d0d12e609c5ae.md)，保留其“待审”状态。
- 首次下载执行：[tokenizer-check-9d62e031a4b84ef59cb776e043c13821](tokenizer-check-9d62e031a4b84ef59cb776e043c13821.md)。
- confirmation_actor：用户。
- confirmation_basis：用户对“新建本审查 v2 并更新 INDEX”的请求回复“批准”。
- confirmed_at：not_provided。
- recorded_at：null；recorded_at_source：not_available；recorded_at_status：unavailable。
- recorded_at_reason：本轮文件工具未返回可信精确记录时间，没有取时命令许可，不以日期、旧运行时刻或模型估计代填。
- authorization_scope：仅新建本文件并更新 INDEX；不批准联网、安装、执行 tokenizer／模板、读取密钥、真实准备或付费调用。

本轮最小闭环是一次只读静态复验结论落盘和导航同步。规划／验收职责为用户指定 sol6.1 high，不探测或切换实际模型，不创建其他会话。

## 2. 直接读取证据与方法

项目根：`D:\MyPythonProjects\datainsight`。

新证据根：`outputs/W2-B2/tokenizer-static-supplement-7f9c82d4a6034b71b18d0d12e609c5ae/`。

先读取执行结果，再直接读取：

- config-values.json。
- chat-template-static.txt、chat-template-lines.json 的必要原文／定位。
- demo-source-static.txt。
- special-token-processor-summary.json。
- counting-evidence-matrix.json。
- source-package-identity.json、source-protection-before.json、source-protection-after.json。
- archive-boundary-check.json、static-supplement-report.json、final-status.json、authorization-record.json。
- source-snapshots/supplement_tokenizer_static.py。
- INDEX 的当前相关导航。

没有联网、运行命令、执行模板、动态加载 tokenizer 或独立重算文件摘要；没有逐个独立打开清单中的所有文件。字节身份／CRC／前后保护依据已保存工具结果及其生成检查逻辑，不冒称独立计算。

final-status 记录 exit_status=0、status=success、started_at=`2026-10-13T04:46:27.050191+00:00`、completed_at=`2026-10-13T04:46:27.401771+00:00`、c205_state=not_satisfied、final_acceptance=not_performed。该终态是宿主静态流程结果，不是计费门或阶段验收。

## 3. 补证范围验收

| 范围 | 直接核对结果 | 判定与边界 |
|---|---|---|
| 原包身份与保护 | 工具重算原包为 1,911,504 字节、SHA-256 e7310d1dafe0a86d8a5629fe78a7c763760f651db9b8682718a1781dcd6fe495；指定原包／JSON／旧脚本 before／after 一致 | 通过；支持本次窗口保护，不认证供应链或恢复旧运行前身份 |
| 完整小型配置 | 准确保存 tokenizer_class、model_max_length、bos/eos/pad/unk、add_bos/eos、legacy及相关对象 | 通过；配置值不是当前 API 参数或服务上界 |
| 原始模板与编号行 | 完整 chat_template 字符串、成员／字符串摘要和编号行可读；没有渲染或修改模板 | 通过；静态定位不能证明服务实际采用 |
| 完整 demo | 完整 import／相对目录／from_pretrained 参数及裸文本 encode 原文可读 | 通过；没有执行代码，不自动接受加载参数 |
| 有限处理器与标记关联 | BPE 非词表参数、子处理步骤、相关特殊标记配置与 added-token 的有限关联；无全词表／ID清单 | 通过；关联不等于运行编码验证 |
| 计数证据矩阵 | 各项有成员／字段／行号或明确 not_found/not_verified，原文用于审查关键词实际语义 | 通过；当前 model／服务包装保证仍未建立 |
| 不执行／不联网 | 检查器为标准库固定归档读取，没有HTTP客户端、模板加载／eval、包导入或extractall；成员落盘为静态证据 .txt | 通过（本次限定源码／证据范围）；不宣称全系统独立隔离 |
| 新旧证据分离 | 新 run、旧包和原工具未修改，终态与 C205 状态分开 | 通过；旧 v1 不通过记录保持历史 |

本次仅限定静态补证通过，不认证工具是通用 ZIP 沙箱、全部漏洞测试完备或当前 tokenizer 可运行。

## 4. 静态事实与技术解释

### 4.1 配置值

config-values 记录 `tokenizer_class=LlamaTokenizerFast`、`model_max_length=16384`、`add_bos_token=false`、`add_eos_token=false`、`clean_up_tokenization_spaces=false`、`legacy=true`、`unk_token=null`、`sp_model_kwargs={}`。

16384 是**包内配置原值**，不是当前服务 context length、实际输入 token 上限或保守预算保证；本文件没有将它用作 C205 上界。

bos 为 `<｜begin▁of▁sentence｜>`，eos/pad 为 `<｜end▁of▁sentence｜>`，相关 AddedToken 对象及配置值保留。模板静态原文显式输出 bos_token，因此 add_bos_token=false 不能推成“完整 messages 不含起始标记”。运行加载与模板渲染的叠加行为仍未验证。

### 4.2 模板角色与 generation prompt

模板原文可定位：

- 汇集 system 内容并拼接到开头。
- 迭代 messages，区分 user、assistant、tool 分支。
- 显式 User／Assistant、工具调用与工具输出分隔标记，及 sentence 结束标记。
- 末尾 add_generation_prompt 条件可追加 Assistant 标记。

这些是静态分支观察，不执行模板变量、默认值或任何 Jinja 编译；不推断 API 服务采用相同模板。

continue_final_message 和 thinking 开关未在该模板原文出现，含义仅为“本模板未声明”，不是 API 不支持，也不能证明非思考模式无需额外服务包装。

**JSON 关键词的语义已核对：**原模板中的 ```json 出现在工具函数参数代码块拼接。它不是 Chat Completions response_format=json_object 的系统包装支持证据；矩阵中的 template-json observed 只说明关键词位置，不能作为服务 JSON 模式输入计数证明。

### 4.3 demo 与后续加载风险

demo 完整原文：import transformers；`chat_tokenizer_dir="./"`；`AutoTokenizer.from_pretrained(chat_tokenizer_dir, trust_remote_code=True)`；裸文本 `tokenizer.encode("Hello!")`。

没有 apply_chat_template/messages 示例、local_files_only、精确依赖锁版本或 LICENSE 声明。源码存在 trust_remote_code=True 不表示本次执行过远程代码，但**后续不得照抄该示例进行加载**。若未来确需运行，必须另行明确本地来源、关闭／限制动态代码与网络、依赖／缓存／权限；本报告不授权它。

### 4.4 有限特殊 token／处理器结构

special-token-processor-summary 记录 BPE、byte_fallback=false 等非词表参数，normalizer 空 Sequence，pre_tokenizer 的 Split/ByteLevel 子步骤，以及 ByteLevel post_processor／decoder 配置。

工具计数为 vocab_entries=128000、added_tokens_total=1283、special_flag true=1237／false=46。它们是工具解析的静态统计，**不是文本 token 计数**。

配置／模板直接引用的标记被有限关联到 added_tokens 字段路径，ID 值未输出。User／Assistant 等部分标记的 special 属性与 bos/eos 不同，不能仅靠字符串形状假定它们均为同一种“特殊 token”；按原配置区分，不臆造计费算法。

## 5. 非阻塞 warning

执行结果明确记载宿主脚本第211行正则字符串使用非 raw 反斜杠产生 SyntaxWarning。源码快照及 demo-encode 的实际定位可核对，工具退出0；本次没有发现该警告改变提取匹配或使必需矩阵失效。

处理：保留警告与旧源码，不为消除它修改已保存证据或再次运行本闭环。后续若复用宿主检查代码，可在新脚本中按正常代码规范修正字符串，不将它作为本次不通过项或额外补证轮。

## 6. C205 的剩余实质缺口

本次已完成可取得静态内容，不再重复补读原包。仍未建立：

1. 当前 deepseek-flash／DeepSeek-V4.1-Flash 与该包的明确适用映射／版本依据。
2. 实際服务是否采用这份模板、role/special/generation 参数，以及非思考／JSON模式是否额外注入 prompt。
3. 完整 API 输入与 provider usage.prompt_tokens 的等价关系，或可复核的可靠保守上界。
4. 兼容依赖／许可证与安全本地运行证据；当前未安装、加载或运行 tokenizer。

因此 C205 仍未满足，不能用包存在、chat_template存在、字符比例、固定额外token或UTF-8字节假设填预算上界。不进行付费请求“测差多少”，不以当前静态计数推定实际扣费。

**不建议现在安装并运行 tokenizer。** 动态计数只能证明这个本地工具对给定字符串算出了什么，不能补上当前模型适用与服务端包装的权威依据。先解决这类来源问题，再判断是否需要限定动态验证；避免在相同静态证据上反复安装／运行却无法关门。

## 7. 最小下一步

下一闭环仅针对模型适用与完整输入计数保证，列精确官方公共资料目标／问题后申请限定联网核对；当前没有联网许可。

若官方依据仍不足，明确记录计数门阻塞，再由规划／验收方讨论是否存在可证明的保守预算方案及其必要批准。不能凭经验余量降低已冻结可靠上界要求；若技术口径确需变化，须保留旧标准、明确影响和新增 ADR／批准，不默默改 C205。

本文件不选择准确 model、实际币种／余额／累计预算，不批准安装、动态计数、POLICY、真实 prepare、OUTBOUND 或 CALL。W2-B2 其他真实产品入口／transport／usage／费用闭环仍未完成，整体保持未验收。

## 8. 本轮落盘与历史保存

仅新建本审查 v2 并更新 INDEX：不改 frozen、功能源码、配置、ADR、v1审查、执行记录、原包或任何 run。没有执行项目／命令、联网、读取密钥或独立重新计算哈希。

所有 evidence run 稳定保留；同目录原子发布 .tmp 是必要例外，不移动／清理；静态证据文本不是待执行脚本或聊天草稿。

L1 限定通过、W1/W2-A/W2-B1 通过保持；W1最后生产计算与修复后合成收尾继续分开，不重验、不重装、不重跑CSV。

新增 ADR：本轮无。新增执行／教学交接：本轮无。用户业务决定：本轮无。后续官方依据核对权限另行申请，技术判定仍由规划／验收方承担。
