# 官方 tokenizer ZIP 限定下载与静态检查执行结果

**待规划／验收方审查。下载／当前静态工具流程完成；完整计数证据矩阵仍有缺口，C205 未满足。W2-B2整体仍未验收。**

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

## 授权及时间

用户明确批准 P-B2-TOKENIZER-STATIC 一次固定URL GET、宿主脚本、ZIP静态检查、证据及结果文档／INDEX。本次没有安装、整体解压、导入或执行包内任何代码／模板、凭据／账户读取、生成API或真实数据读取。

confirmation_actor=用户；confirmed_at=not_provided。本文recorded_at=null、recorded_at_status=unavailable、recorded_at_source=not_available：文件工具未返回精确文档记录时间。运行authorization-record由获批Python工具另取记录时刻，不是用户确认时间或本文保存时刻。不回填旧记录。

## 命令与实际字节

```bash
cd /d/MyPythonProjects/datainsight && PYTHONDONTWRITEBYTECODE=1 TEMP='D:\MyPythonProjects\datainsight\.cache\tmp' TMP='D:\MyPythonProjects\datainsight\.cache\tmp' TMPDIR='D:\MyPythonProjects\datainsight\.cache\tmp' .venv/Scripts/python.exe -B 'outputs/_scratch/tokenizer-check-9d62e031a4b84ef59cb776e043c13821/inspect_tokenizer.py' --url 'https://cdn.deepseek.com/api-docs/deepseek_v4_tokenizer.zip' --output-dir 'D:/MyPythonProjects/datainsight/outputs/W2-B2/tokenizer-check-9d62e031a4b84ef59cb776e043c13821' --deadline-seconds 120 --max-download-bytes 67108864 --max-members 2048 --max-total-uncompressed-bytes 134217728 --max-member-bytes 67108864 --max-text-bytes 1048576 --max-compression-ratio 100 --max-json-depth 32
```

真实主命令退出0；final-status为success，仅表示本检查器已实现检查／必需报告完成，不表示交接所有语义矩阵充分或C205通过。

证据：[tokenizer-check-9d62e031a4b84ef59cb776e043c13821](../../../outputs/W2-B2/tokenizer-check-9d62e031a4b84ef59cb776e043c13821/)。download-record原值：HTTP200、request_count=1、redirects_followed=0、retries=0、proxy_used=false、authentication_sent=false；Content-Length与实际下载均1911504字节；开始2026-10-10T09:10:54.872773+00:00，结束2026-10-10T09:10:55.239321+00:00。仅GET固定cdn URL，不访问README链接或其他站点。

ZIP SHA-256：`e7310d1dafe0a86d8a5629fe78a7c763760f651db9b8682718a1781dcd6fe495`，来自package-sha256工具记录。没有独立官方签名／发布hash，身份只证明本次HTTPS来源字节，不是供应链真实性认证。

## ZIP完整目录及必要读取

zip-inventory记录全部四个成员：

| 成员 | 声明未压缩字节 | 本次处理 |
|---|---:|---|
| deepseek_v4_tokenizer/ | 0 | 目录元数据，不解压 |
| deepseek_v4_tokenizer/deepseek_tokenizer.py | 277 | UTF-8完整内存读取、CRC校验，仅读静态匹配行 |
| deepseek_v4_tokenizer/tokenizer_config.json | 3128 | 完整内存JSON读取、深度检查／CRC，结构摘要 |
| deepseek_v4_tokenizer/tokenizer.json | 6367096 | 完整内存JSON读取、深度检查／CRC，词表仅输出条目数，不输出词表／token ID清单 |

路径／大小／压缩／模式／加密中央目录先检查，archive-boundary-check保存通过。成员未落盘、未调用extractall、无包内脚本副本作为可执行文件。检查器自己源码快照保存在source-snapshots，是宿主工具，不是下载代码。

selected-member-check中的实际结构：tokenizer.json model.type=BPE，vocab_entries=128000，added_token_entries=1283；normalizer/pre_tokenizer为Sequence，post_processor/decoder为ByteLevel。tokenizer_config顶层包括bos/eos/pad/unk、tokenizer_class、chat_template等键，chat_template_present=true。上述是工具计算或解析结果，不是计数运行值。

包目录没有README、LICENSE、NOTICE、requirements、pyproject或其他独立依赖声明。demo静态第1/3行注明pip3 install transformers、import transformers；第7行调用AutoTokenizer.from_pretrained，第11行裸文本encode。没有安装/执行示例。示例未锁依赖版本，许可证未知，不能根据“官方链接”推定许可证。

## 完整输入计数证据矩阵与不足

| 问题 | 静态所见 | 当前不能证明 |
|---|---|---|
| 当前model／版本适用 | 官方文档下载链接及v4包名；JSON结构已读取 | V4.1-Flash/deepseek-flash适用声明与不可变版本证据未发现／未充分提取；文件名不算保证 |
| 裸文本或messages | demo只见裸文本encode；config有chat_template字段 | 未执行apply_chat_template或encode，没有完整messages计数值 |
| role/special/generation/thinking/JSON编码 | special相关键及chat_template存在 | 本工具只输出字段存在性，未保存具体模板内容／特殊token结构或逐项语义定位；静态证据不足，不假称已核对 |
| API包装／prompt_tokens | 当前包结构不提供服务端实测 | 服务额外包装、JSON模式注入、与usage.prompt_tokens一致性或可靠上界未建立 |
| 依赖／许可证 | demo明确transformers；无独立LICENSE等成员 | 精确兼容版本、动态/远程加载行为与许可仍待审，不运行或自行联网找补 |
| 已证明范围 | 单次来源字节、完整目录、当前选择成员的结构／静态匹配行 | tokenizer运行、模型兼容、完整计费输入可靠上界均未验证 |

尤其chat_template“存在”不是其适配当前服务的证明。本批检查器的JSON摘要没有提取tokenizer_class值、chat_template完整内容、特殊token配置值，demo只保存固定关键字匹配行而非全部源码行。因此下载及工具流程成功不意味着交接D节证据矩阵已完整；规划／验收方应决定是否需要另一次限定静态读取补证或官方资料。不得据此安装、运行包或发真实付费probe。

## 清单／安全／剩余门

正式run包括ZIP、package-sha256、download-record、zip-inventory、archive-boundary-check、selected-member-check、tokenizer-static-report、authorization-record、environment、command-record、artifact-inventory、final-status及宿主检查器快照。工具脚本另在批准scratch位置。实际清单逐文件摘要见artifact-inventory；自身及final-status排除自摘要明确。

ZIP成员安全检查采用固定宿主代码，包内文字未作为命令；没有将全词表或包内任意raw内容放提示词。声明大小与必要成员实际完整读取均受设计限额；CRC仅验证归档内部一致，不认证来源真实性。JSON摘要/parser及路径校验是否充分，由验收方检查宿主源码快照，不据“success”宣称攻击穷举或资源完美隔离。

本批不改功能模块、上游、冻结标准、policy、ADR或旧证据；一次下载额度已用，不自动重试或执行额外检查命令。C205仍有实质缺口，真实调用保持禁止。用户将本文及证据目录转回规划／验收方一次审查，再独立制定必要静态补证／离线计数运行／依赖授权；不自动进入POLICY、prepare、OUTBOUND或CALL。无新ADR、业务决定或教学交接。
