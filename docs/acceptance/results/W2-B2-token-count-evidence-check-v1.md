# W2-B2：完整输入 token 官方依据核对 v1

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

## 1. 结论：本轮查证收尾，C205 保持阻塞

**在本轮授权并实际读取的官方公共资料中，没有找到足以闭合 C205 的当前 tokenizer／完整服务输入计数保证。C205 仍未满足，付费入口不放行。W2-B2 整体仍未验收。**

这是范围明确的“未找到充分依据”，不是“官方不存在该能力／文档”的证明。静态补证已通过，无需再重读原包、重复安装或运行本地计数来掩盖服务端依据缺口。本轮官方资料查证到此结束，不自动继续扩大搜索、联系支持、下载其他包或付费探测。

同时发现一个可用于后续设计的不同事实：官方 Responses API 对输出上限明确包括可见输出和推理 tokens，但它没有为本轮提供完整输入计数保证。不能据此自动换接口或宣布 C205 已满足。

- confirmation_actor：用户。
- confirmation_basis：用户批准 P-B2-COUNT-CHECK，仅读指定官方页面及直接相关同站链接，新建本报告并更新 INDEX。
- confirmed_at：not_provided。
- recorded_at：2026-10-13T05:20:50.539Z。
- recorded_at_source：浏览器工具执行 JavaScript `new Date().toISOString()`，本地资料观察时钟。
- recorded_at_status：available。
- recorded_at_scope：资料读取结束后的工具记录时间，不是用户确认、provider 发布时间或精确文件落盘时间。
- authorization_scope：限定公共文档核对及上述文档动作；没有代码／标准变更、账户访问、凭据读取、下载、安装、生成或计数 API 请求许可。
- bound_versions：W2-B2-v1 frozen、tokenizer-static-review-v2、ADR-005／ADR-007。

本轮最小闭环：官方依据核对 → 正面事实与证据缺口分别记录 → 明确停止 → 结论与导航落盘。技术安排和验收仍由规划／验收方判定，用户批准不是技术条款认证。

## 2. 实际范围与方法

已读指定页面：

| 编号 | URL | 核对位置 |
|---|---|---|
| D1 | https://api-docs.deepseek.com/quick_start/token_usage | 全文，Calculate token usage offline |
| D2 | https://api-docs.deepseek.com/api/create-chat-completion | Request/messages、max_tokens、response_format、Responses/usage |
| D3 | https://api-docs.deepseek.com/guides/json_mode | Notice、示例与 JSON 模式参数 |
| D4 | https://api-docs.deepseek.com/guides/thinking_mode | 模式控制、输入输出参数、多轮与工具上下文说明 |
| D5 | https://api-docs.deepseek.com/updates | 当前 Flash 发布／路由变更及历史更新全文 |

实际读取直接相关同站链接：

| 编号 | URL | 相关性与读取范围 |
|---|---|---|
| D6 | https://api-docs.deepseek.com/api/create-response | D2 导航链接；输入／输出计数及输出上界字段，完整主文档 |
| D7 | https://api-docs.deepseek.com/guides/responses_api | D6 直接链接；完整兼容表与输入／usage 说明 |
| D8 | https://api-docs.deepseek.com/guides/multi_round_chat | D4 直接链接；客户端 messages／历史上下文拼接 |
| D9 | https://api-docs.deepseek.com/news/news260910 | D5／导航直接链接；当前模型发布与兼容路由，完整主文档 |
| D10 | https://api-docs.deepseek.com/quick_start/pricing | D2／D5 直接链接；当前模型映射与 context length，完整主文档 |

web_fetch 对部分长页只返回截取内容；D1–D7、D9–D10 的关键判断另使用浏览器 `main` 全文读取，未见工具截断通知。D8 的 fetch 内容提供所引用的多轮段落。负面结论以这些已读页面为限，不推定站点所有隐藏／历史／其他接口都覆盖。

只请求公开 URL，未发送本地项目内容、schema／摘要、数据、密钥或账户标识。没有搜索引擎、站内搜索服务调用、支持联系、外域访问、认证页、包下载／安装或模型 API 请求。浏览器只读查看公开主文档及链接／取时，不运行项目代码。

本轮没有独立计算业务数值、token 或费用，没有读取原始数据，没有修改 frozen 或旧 run。

## 3. 问题一：当前 Flash 与已有包的适用保证

### 已见事实

D1 的离线计数段落写：

> “You can run the demo tokenizer code in the following zip package to calculate the token usage for your input/output.”

页面链接指向此前已获取的 deepseek_v4_tokenizer.zip。页面还明确字符与 token 比例是 approximately，实际用量以返回 usage 为准。[cite:7a536a46-1]

D5 当前发布段落与 D9 写当前 API 请求名为 deepseek-flash，对应 V4.1-Flash，旧 Flash 名兼容路由到新模型。[cite:7a536a46-5][cite:b5fea031-3]

### 仍不足的依据

在这些已读段落没有看到：

- 指定已有 ZIP 的内容摘要／版本与当前 V4.1-Flash 的明确绑定。
- 该包的 chat_template 与当前 Chat Completions 服务完全一致的承诺。
- 包中 tokenizer_config 的 model_max_length 等值可作为当前 API 计费输入边界的说明。

因此，“当前官方计数页面仍链接此包”可以作为来源背景，但不能提升为“该静态模板已被认证与当前服务包装完全相同”。原包的静态事实保持，既有补证通过也不自动填补该映射。

## 4. 问题二：完整 messages／模式包装如何计入输入

D2 请求参数定义 messages 为对话消息列表，role／content 为输入结构；usage 定义 prompt_tokens 与缓存细分。官方 D4 说明工具请求中历史 reasoning_content 会传回并纳入上下文，无工具时该内容不会拼入下轮上下文。[cite:7a536a46-2][cite:7a536a46-4]

D8 明确 Chat Completions 是 stateless，上下文历史由客户端每次拼接发送。[cite:b5fea031-2]

这能说明客户端需要发送哪些历史内容，不代表服务不使用内部包装，也不能把 stateless 理解为不缓存或绝不保存任何信息。

D3 说明启用 json_object 时需在提示中包含 json 并提供格式示例，可因 max_tokens 截断或偶尔返回空内容。[cite:7a536a46-3]

本轮没有发现完整的服务端序列化模板、role／special-token／generation 边界计费算法，或对非思考／JSON 模式额外包装的完整计数说明。没有读取到“用户可见 messages 自行 encode 的数量就是 prompt_tokens”这一可靠等价保证。

`thinking.type=disabled` 或 reasoning_effort=none 是有文档依据的模式开关；关闭思考不等于已经证明输入计数或隐藏包装数量。JSON 示例也不是模板计费规范。

## 5. 问题三：请求前完整计数／可靠上界能力

### 5.1 Chat Completions 已见正面事实

D2 完整 API 文档可重读定位：

- max_tokens：限制生成的 chat completion token 数。
- “The total length of input tokens and generated tokens is limited by the model's context length.”
- usage.prompt_tokens：输入 tokens，等于 prompt_cache_hit_tokens＋prompt_cache_miss_tokens。
- usage.total_tokens：prompt＋completion。
- 可选 completion_tokens_details.reasoning_tokens：推理 token 细分。

这些是公开参数／响应定义，不是本轮 API 实测。usage 是响应后观测，不能单独解决发送前预留问题。

### 5.2 Responses API 的新发现（不自动采用）

D6 完整主文档的 max_output_tokens 定义：

> “An upper bound for the number of tokens that can be generated in the response, including both the visible output tokens and the reasoning tokens.”

同页 input_tokens／output_tokens 和 reasoning 细分公开定义；text.format 列出 json_object 与 json_schema。[cite:b5fea031-1]

D7 兼容表说明 instructions 插入为首个 system message，input 转为消息／输入项；超 context window 的请求返回400，truncation 参数不支持。它还说明有些兼容参数会被忽略，因此不能仅凭通用 OpenAI SDK 参数名推定本服务支持全部功能。上述事实依据 D6/D7 的浏览器完整 `main`，不是 fetch 截取部分的推测。

**技术判断：**Responses 对“输出上限涵盖推理”的表达比已读 Chat Completions max_tokens 更直接，但它仍未提供本轮需要的完整请求前输入计数算法／可靠精细上界。使用 Responses 将改变请求、响应、usage 与现有首调用适配建议，必须另行明确设计与批准，不为了躲计数缺口偷偷切接口。模型工具调用仍不纳入范围。

### 5.3 查证收尾结论

在实际已读页面／兼容表中未找到可用的完整请求前计数接口定义、完整模型／模式计数映射保证或精细保守上界公式。本轮也未发送任何计数 API 请求。

不将此表述为“官方不存在计数接口”。只说明本轮授权资料未建立可用于 C205 的保证，不能以未核实的接口、字符经验、固定加 token 或付费试探放行。

**C205 在当前方案中仍阻塞。公共计数保证查证到此结束，不再自动开启同类查证轮。**

## 6. 资料冲突与适用边界

D9 首发新闻写 Pro 将在指定日期后路由至 Flash；D5 更新日志同时写继续提供 Pro 服务且费用不变，D10 当前价格表仍列独立 Pro。资料口径不完全一致。[cite:b5fea031-3][cite:7a536a46-5][cite:b5fea031-4]

本项目尚未选 Pro，冲突不通过猜测解决，不访问账户/API探测；后续推荐直接当前 deepseek-flash，并在准确policy批准时绑定目标／响应允许身份。不得将旧新闻或模型文件名自动用作计数兼容证据。

本轮不新增benchmark／价格预测或业务效果结论。文档中示例和历史模型都不证明当前计数运行能力，当前账户余额／币种／价格适用及限额仍未由用户确认。

## 7. 可讨论的续作候选（尚未批准、尚未满足 C205）

为避免继续反复查同类资料，下一轮应改为**有界的预算设计决策**，不再静态补读或默认安装 tokenizer。

### 候选 A：基于服务 context ceiling 的保守预留（优先论证）

D2 明确输入＋生成受到模型 context length 限制；D10 当前模型表标 context length 为1M，D7说明 Responses 超窗返回400。这提供一个与精细文本计数不同的候选思路：对已批准固定模型／模式，用有明确精确整数解释和适用依据的整个 context ceiling 作为输入预留上界，输出另用覆盖全部计费类别的硬上限。

**它是候选，不是当前已成立结论。** 仍需逐条确认：

- “1M”对应的精确 token 整数及该数是否涵盖所有计费输入；不得擅自将缩写转换为某个二进制／十进制值。
- 限制适用当前模型／endpoint／模式，内部额外计费输入是否受相同 ceiling 约束。
- 服务错误、超窗或发送后中断仍可能产生费用，无法证明上界时仍不能发请求；已批准消费模型必须覆盖这些风险。
- context ceiling 预留可能比本次小请求实际用量大很多；它是预算上界不是估计 usage，更不是已计算成本。
- 输出限制及最高适用费率、币种与余额须实际核对；不凭 context label 自算本轮费用。
- 若官方输出约束更明确的 Responses 被选用，应先确认范围变更／ADR及新协议测试，不同时支持两条接口。

现有 C205 接受可靠上界，不必为了“不用精细tokenizer”自动放宽它；若能证明这个候选符合标准，可明确新的有依据实现。但若只剩不可验证假设，必须保持阻塞，不能把保守措辞当证明。

### 候选 B：明确更改风险／验收口径

若可靠硬上界无法证明，而用户仍希望推进真实演示，可提出新版本／ADR的有界费用风险安排，并清楚标明它不能保证旧 C205 的发送前最高费用要求。原 frozen 保留，用户需明确批准改变范围与验收安排；规划／验收方承担技术判定，不能让用户替未验证保证签字。

本候选仅列出可做产品安排，不推荐在本轮直接放宽或调用。单请求／输出上限／账户限额等组合可能降低风险，但不是未证最高费用的替代认证，不能悄悄算旧标准通过。

### 当前推荐与决定门

优先在下一轮只读设计中论证候选 A 是否确有可复核的保守上界；没有证据则明确放弃该证明路线，再由用户选择暂停真实调用或是否讨论候选 B。一次列全前提／成本工具计算需要的输入／权限，不继续堆叠小轮次“再查一点”。

本轮没有请求或作出预算／模型／接口选择，不生成policy、不计算或猜任何实际调用成本。后续算术必须由获批工具取得，明示上界与实测之别。

## 8. 本轮交付与保持项

仅新建本报告并更新 INDEX；不改标准、源码、测试、配置、ADR、旧报告、ZIP或运行证据。没有 shell／项目运行、安装、包下载、密钥／账户访问、支持联系或 API 请求。

L1 与限定静态补证通过保持；W1/W2-A/W2-B1 不重验、不重装，最后生产计算与修复后合成收尾仍分别引用。原始数据只读，本轮未读取。

新增 ADR、执行交接及用户业务决定：本轮无。下一步是预算设计候选的明确论证／选择，**不是继续无边界查证或自动真实调用**。W2-B2 整体仍未验收。
