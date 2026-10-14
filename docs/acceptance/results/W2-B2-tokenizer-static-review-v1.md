# W2-B2 tokenizer 静态审查 v1

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

## 1. 判定与效力

**完整静态核对交付：不通过。C205：仍未满足。W2-B2 整体：未验收。**

下载和已实施的目录／结构检查有真实证据；不通过的直接原因是交接要求的 chat template、特殊 token 与完整输入编码语义核对没有完成，不是下载失败。不能把“没有计数保证”本身当成静态检查失败：充分检查后发现依据不足也是有效结论；但目前小型配置的必要内容尚未提取、定位。

- 对应交接：[tokenizer-check low v1](../../handoffs/W2-B2-tokenizer-check-sol61-low-v1.md)。
- 原执行记录：[tokenizer-check-9d62e031a4b84ef59cb776e043c13821](tokenizer-check-9d62e031a4b84ef59cb776e043c13821.md)，保留其原状态。
- 冻结标准：[W2-B2-v1](../W2-B2-v1.md)，不修改技术条款。
- 公共资料依据：[provider-check-v1](W2-B2-provider-check-v1.md)，本轮不重新联网核对。
- confirmation_actor：用户。
- confirmation_basis：用户批准新建本审查、离线补证交接及更新 INDEX。
- confirmed_at：not_provided。
- recorded_at：null；recorded_at_source：not_available；recorded_at_status：unavailable。
- recorded_at_reason：当前文件工具未返回可信精确记录时间，没有取时命令许可，不使用日期或旧运行时刻代填。
- authorization_scope：仅上述文档动作；不是补证运行、安装、包代码执行或真实调用许可。

本轮最小闭环是只读审查结论及有限补证交接落盘。没有运行命令、联网、安装、执行包内容或独立重算摘要。

## 2. 直接证据

项目根：`D:\MyPythonProjects\datainsight`。

证据根：`outputs/W2-B2/tokenizer-check-9d62e031a4b84ef59cb776e043c13821/`。

直接读取执行文档、download-record、package-sha256、zip-inventory、archive-boundary-check、selected-member-check、tokenizer-static-report、final-status、environment、authorization-record、artifact-inventory，以及 source-snapshots/inspect_tokenizer.py。

### 已有可信观察（限本次工具证据）

- download-record：固定 HTTPS URL、HTTP 200、request_count=1、无重试／跟随跳转／代理／认证头；实际下载与 Content-Length 均 1,911,504 字节。
- 工具记录 ZIP SHA-256：`e7310d1dafe0a86d8a5629fe78a7c763760f651db9b8682718a1781dcd6fe495`。验收方未独立计算；没有独立官方签名／发布摘要，不能据本地哈希认证供应链真实性。
- 中央目录四成员：目录、deepseek_tokenizer.py、tokenizer_config.json、tokenizer.json。必要文件读取有字节摘要与 CRC 内部核对，未落盘解压。
- demo 声明 transformers，存在 from_pretrained 与裸文本 encode；未执行。
- tokenizer_config 声明 chat_template 字段存在，但未保存值。
- tokenizer.json 工具结果为 BPE、词表条目 128000、added_token 条目 1283、Sequence／ByteLevel 相关类型。它们是静态结构，不是 tokenizer 运行数或模型适用认证。
- 目录无 README、LICENSE、NOTICE 或独立依赖声明。该缺失本身可记录，不推定许可证或完整依赖。
- 环境为已有项目 venv、Python 3.12.9、D 盘 .cache/tmp；最终状态 success、退出 0 的 scope 明确为下载／静态工具，不是 C205 通过。

源码表明读取限定包成员，没有安装、extractall、导入／执行包内代码或模板。该范围审查不宣称攻击穷举或通用 ZIP 沙箱。

## 3. 直接缺口定位

检查器快照第 225–241 行只保存顶层键、chat_template_present、处理器类型和关键字匹配行。因此：

| 必需内容 | 现有证据 | 缺口 |
|---|---|---|
| tokenizer_class | 只有字段名 | 没有准确值／适用加载路径 |
| chat_template | 存在性为 true | 没有完整静态内容、role／分隔符／generation prompt 等定位 |
| 特殊 token 配置 | bos/eos/pad/unk 等字段名 | 没有相关配置值与模板／处理器关系 |
| demo | 部分匹配行 | 没有完整源码定位，from_pretrained 参数等上下文未完整审查 |
| thinking／JSON 模式 | 未有语义报告 | 不知模板是否支持这些参数；不能将未提取当不支持 |
| 当前模型／API包装 | 包名和公共链接 | 无当前 Flash 适用或完整服务端 prompt_tokens 等价／上界依据 |

主要阻塞是小型配置与 demo 的可取得静态证据未完整交付。补证后仍可能找不到模型／服务包装保证；届时可以判定静态补证完成而 C205 未满足，两者必须分开。

## 4. 最小修复：只读原包静态补证

交接：[W2-B2-tokenizer-static-supplement-sol61-low-v1](../../handoffs/W2-B2-tokenizer-static-supplement-sol61-low-v1.md)。

只新增受控宿主脚本和新证据 run，仅读已下载、固定摘要的 ZIP：

1. 完整读取小型 tokenizer_config.json，保存 tokenizer_class、相关特殊 token 配置及 chat_template 的原始字符串／编号行；不执行模板。
2. 完整读取 demo，保存编号源码并静态定位 from_pretrained 参数／裸文本或 messages 调用；不导入。
3. 必要时从 tokenizer.json 仅读有限 special-token／处理器结构，与配置／模板明确引用的项目对照，不输出全词表／token ID 清单。
4. 按 role、special token、generation prompt、非思考／JSON 参数、当前模型版本、服务端包装与计数保证逐项给源位置或 not_found/not_verified，不猜语义。
5. 以工具摘要核对原包本次前后不变，新报告与原记录分开；没有任何再次下载、依赖安装、模板运行或付费探测。

不用修原检查脚本或回填旧 selected-member-check。新工具只补必要提取，不建设通用归档审计框架。标准与 C205 通过条件保持。

## 5. 未扩大为补证要求的边界

本审查不要求重做下载、全面 ZIP 攻击测试、许可证联网检索、tokenizer 动态加载、所有特殊 token 枚举或当前模型付费测试。原下载记录、完整目录及结构成果可复用。

检查器源码中的一般边界与状态能力仍限已观察范围；本次不据代码静态阅读认证它是完善通用安全框架。补证只对这个固定包、必要小型内容生效。

## 6. 当前状态与下一步

L1 离线限定通过、W1/W2-A/W2-B1 通过保持；最后生产计算与修复后合成收尾继续分开，不重验、不重装、不读 CSV。

原 tokenizer 批次及其失败／临时证据原位保留，INDEX 仅链接新的审查，不修改原执行记录、ZIP 或终态。

下一步由用户手动转交补证文件，执行方一次申请其精确离线合批预授权。补证完成后规划／验收方核对静态矩阵充分性，再判断是否有必要且有依据安排最小动态计数验证；当前不批准安装、执行包、POLICY、真实 prepare、OUTBOUND 或 CALL。

新增 ADR：本轮无。用户业务决定：本轮无。完整静态交付当前不通过，C205 缺口保留，**W2-B2 整体仍未验收**。
