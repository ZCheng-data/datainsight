# tokenizer 原 ZIP 离线静态补证执行结果

**待规划／验收方审查。宿主静态流程完成；C205仍未满足，W2-B2整体未验收。**

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

## 授权、命令与状态

用户明确批准P-B2-TOKENIZER-SUPPLEMENT合批范围：新宿主工具、固定ZIP离线读取、最多两次限定运行及结果／INDEX。首次成功，未使用第二次。没有联网、下载、安装、整体解压、包代码／模板执行、凭据／真实数据／API读取或调用；不改原包、原工具、功能源码、标准、ADR或旧证据。

confirmation_actor=用户，confirmed_at=not_provided。本文recorded_at=null，recorded_at_source=not_available，recorded_at_status=unavailable：文件工具未提供可信精确文档记录时间，不借运行时间回填。新运行authorization-record独立保存工具取得recorded_at，不是用户确认时刻。

实际命令：

```bash
cd /d/MyPythonProjects/datainsight && PYTHONDONTWRITEBYTECODE=1 TEMP='D:\MyPythonProjects\datainsight\.cache\tmp' TMP='D:\MyPythonProjects\datainsight\.cache\tmp' TMPDIR='D:\MyPythonProjects\datainsight\.cache\tmp' .venv/Scripts/python.exe -B 'outputs/_scratch/tokenizer-static-supplement-7f9c82d4a6034b71b18d0d12e609c5ae/supplement_tokenizer_static.py' --archive 'D:/MyPythonProjects/datainsight/outputs/W2-B2/tokenizer-check-9d62e031a4b84ef59cb776e043c13821/deepseek_v4_tokenizer.zip' --expected-sha256 e7310d1dafe0a86d8a5629fe78a7c763760f651db9b8682718a1781dcd6fe495 --output-dir 'D:/MyPythonProjects/datainsight/outputs/W2-B2/tokenizer-static-supplement-7f9c82d4a6034b71b18d0d12e609c5ae' --max-small-member-bytes 65536 --max-tokenizer-json-bytes 16777216 --max-json-depth 32 --max-referenced-special-tokens 64
```

真实退出0。stderr有宿主脚本第211行SyntaxWarning：正则字符串使用非raw的反斜杠转义；工具正常完成。没有掩盖警告、修改已保存源码快照或为消除警告再运行。final-status仅表示静态流程及必需报告完成，不是技术验收或计费门通过。

证据：[tokenizer-static-supplement-7f9c82d4a6034b71b18d0d12e609c5ae](../../../outputs/W2-B2/tokenizer-static-supplement-7f9c82d4a6034b71b18d0d12e609c5ae/)。实际源包字节／SHA由主工具重算并核对历史身份，source-package-identity保存结果；source-protection-before/after覆盖指定原包／小型JSON／原宿主快照，一致是成功必要条件。不是恢复旧运行前摘要或供应链认证。

## 完整静态原文与定位

- config-values.json：准确配置字段值、类型、来源成员与摘要。
- chat-template-static.txt：原chat_template字符串，未改写或渲染；chat-template-lines.json提供原字符串摘要、长度与编号行。
- demo-source-static.txt与demo-lines.json：完整静态源码，未复制为可执行.py或导入。
- special-token-processor-summary.json：model非词表参数、处理器必要结构、工具总数／类型统计，以及仅配置／模板直接引用标记的added-token关联；不输出全词表／ID清单。
- counting-evidence-matrix.json：逐项角色、生成提示、thinking/JSON、demo加载／调用、模型／API包装／计数、许可证／依赖与运行未验证状态。

工具读到tokenizer_class=LlamaTokenizerFast、model_max_length=16384、add_bos_token=false、add_eos_token=false、clean_up_tokenization_spaces=false、legacy=true、unk_token=null、sp_model_kwargs={}。model_max_length是包内配置值，不是当前服务输入上界或已确认模型context。

bos为`<｜begin▁of▁sentence｜>`，eos/pad为`<｜end▁of▁sentence｜>`，相关AddedToken对象原值见config-values。模板显式输出bos_token，说明不能将add_bos_token=false解释为完整messages没有起始标记；静态配置与模板各自作用仍须运行及服务依据核对。

完整模板逐行可见：汇集system内容、messages迭代、user/assistant/tool分支、User/Assistant及工具调用／输出分隔标记、sentence结束标记；末尾add_generation_prompt可追加Assistant标记。没有执行或对变量取默认值渲染。continue_final_message／thinking具体开关未在此模板出现不意味着API不支持；模板中的json文本用于工具调用参数代码块，不应误作API response_format=json_object模式支持。矩阵的关键词命中只是定位，须结合原文语义审阅。

完整demo第3行import transformers，第5行相对目录`./`，第7–9行AutoTokenizer.from_pretrained(chat_tokenizer_dir, trust_remote_code=True)，第11行裸文本encode("Hello!")。没有apply_chat_template/messages示例或local_files_only参数，没有锁定依赖版本；源码存在trust_remote_code并不表示本批实际启用／执行远程代码。将来运行加载必须另获权限并明确关闭／限制路径，不能照demo自动运行或pip install。

原归档四成员复核及实际完整读取／CRC记录见archive-boundary-check；包内没有README/LICENSE/NOTICE/依赖锁成员的事实保持，无联网补查。未知许可证不能猜为开源授权。

## 计数矩阵结论与局限

| 维度 | 静态证据 | 仍未验证 |
|---|---|---|
| 类与加载 | LlamaTokenizerFast、AutoTokenizer加载参数、BPE及处理器结构 | 兼容依赖版本、安全离线实例化、运行计数 |
| 文本／messages | demo仅裸文本encode；模板含messages与角色边界 | apply_chat_template实际路径／参数及特殊token叠加规则 |
| role／special／generation | 完整模板、配置标记及有限关联结构可审查 | 服务是否使用此模板、generation参数与服务内部处理 |
| thinking／JSON | 源位置或未出现状态；JSON字面命中不能推为响应模式 | 非思考及JSON模式是否额外影响服务端prompt |
| 当前Flash适用 | 原官方下载链接与包自身配置 | deepseek-flash/V4.1-Flash精确适用声明未建立 |
| API包装／计费输入 | 本批包内静态资料 | 额外服务提示、prompt_tokens等价／可靠保守上界未建立 |
| 许可证／依赖 | demo import与trust_remote_code参数完整可见 | 许可证、依赖锁／兼容版本、运行权限 |

本批“not_found”只限已完整读到的固定成员或具体模板文本，“not_verified”指静态资料不能认证的模型／运行／服务事实。不能以包存在、模板存在、字符比例、固定额外token、UTF8字节假设或付费probe凑C205通过。

## 产物、保护与交回

新run仅交接白名单：source-package-identity、source-protection-before/after、archive-boundary-check、config-values、chat-template-static.txt/lines、demo-source-static.txt/lines、special-token-processor-summary、counting-evidence-matrix、static-supplement-report、authorization-record、environment、command-record、artifact-inventory、final-status、source-snapshots/supplement_tokenizer_static.py。静态.txt是证据，不是原成员路径解压。工具脚本仅新scratch范围；原包未复制至新run。

artifact-inventory记录实际路径／字节／摘要，自己及final-status排除自摘要；检查器实现是否充分满足字段、语义矩阵与边界，由规划／验收方审阅快照。执行者不自行认证完整静态交付通过。

新证据与旧不通过记录分开，INDEX仅增加待审导航。首次成功不重跑；没有新ADR、业务决定或教学交接。下一步用户转回本文和证据目录，技术审查后再制定最小动态计数／依赖或官方资料许可；当前没有tokenizer执行、POLICY、真实prepare、OUTBOUND/CALL或S4授权。
