# W2-B2 官方公共协议核对 v1

> 技术条款的判定由规划／验收方负责；用户确认的是范围、目的与验收安排，以及技术判定由谁承担。用户不对未逐条验证的技术条款承担认证责任。

## 1. 核对结果与权限

**公共协议核对已完成；W2-B2 整体仍未验收，真实请求仍禁止。**

官方文档支持制定实际 Chat Completions 适配：明确 endpoint、当前模型名、JSON 模式、非思考切换、max_tokens 和 usage 字段。当前 mock body 不是实际 wire 协议，不能直接发送。最主要的首请求前缺口仍是完整模型输入计数／可靠上界、实际计费配置及人批准的余额／累计限额。

- confirmation_actor：用户。
- confirmation_basis：用户明确批准 P-B2-CHECK-PUBLIC，一次完成官方公共资料读取、核对报告新建与 INDEX 更新。
- confirmed_at：not_provided。
- recorded_at：2026-10-10T08:53:27.401Z。
- recorded_at_source：浏览器工具执行 `new Date().toISOString()`，官方公开文档页面内的本地记录操作时钟；不是 provider 时间或用户确认时间。
- recorded_at_status：available。
- recorded_at_scope：资料读取结束后的工具取时；不是文件系统精确落盘时刻，也不作为文档发布／费率生效时间。
- authorization_scope：仅读取 `https://api-docs.deepseek.com/` 及同站公共相关文档，新建本文件、更新 INDEX；没有生成 API、认证账户／余额、密钥、下载、安装或实现权限。
- bound_versions：W2-B2-v1 frozen、ADR-006、ADR-005、ADR-007、W2-B2-offline-review-v2。

本轮使用网页读取工具；web_fetch 对长文档有截取，重要 API／价格内容另以浏览器主文档及表格读取核对。没有使用搜索引擎，没有访问同站链接指向的外域、下载包、账户页面或 API 服务。请求中没有发送本地项目路径、schema、数据、方案、摘要或密钥。

本文件是官方文档核对，不是已验证 API model ID、真实 usage、扣款、tokenizer 或 transport 运行证据；没有调用模型或运行项目。

## 2. 核对入口及重读方法

以下均为本轮实际读取的同站公开文档地址。可用网页工具重新读取 URL，浏览器 `main` 文本及价格表单元格定位相关段落；页面可能更新，后续首请求配置冻结前再次核对必要变化。

| 文档 | 实际 URL | 核对重点 |
|---|---|---|
| 首次调用 | https://api-docs.deepseek.com/ | base_url、推荐当前模型名、请求格式 |
| Chat Completions API（英） | https://api-docs.deepseek.com/api/create-chat-completion | 请求类型、response_format、finish_reason、usage |
| Chat Completions API（中） | https://api-docs.deepseek.com/zh-cn/api/create-chat-completion | endpoint、max_tokens、中文定义交叉核对 |
| 价格（英） | https://api-docs.deepseek.com/quick_start/pricing | 模型版本、美元公开单价与时段 |
| 价格（中） | https://api-docs.deepseek.com/zh-cn/quick_start/pricing | 人民币公开单价与时段；逐单元格读取 |
| JSON Output | https://api-docs.deepseek.com/guides/json_mode | json_object、提示要求、空响应警告 |
| Thinking Mode | https://api-docs.deepseek.com/guides/thinking_mode | 默认思考、关闭参数、reasoning_content |
| Token 用量 | https://api-docs.deepseek.com/quick_start/token_usage | 近似字符比例非上界、官方离线 tokenizer 链接 |
| Context Caching | https://api-docs.deepseek.com/guides/kv_cache | cache hit/miss、最佳努力、服务端缓存 |
| Rate Limit & Isolation | https://api-docs.deepseek.com/quick_start/rate_limit | 非流式 keep-alive 空行与请求等待 |
| Change Log | https://api-docs.deepseek.com/updates | 当前 Flash 命名／版本变更，不用旧知识推断 |

仅记录了 tokenizer 下载链接存在；没有打开 `cdn.deepseek.com`，没有访问 GitHub、平台或其他外域，没有下载／安装／运行其代码。公共更新日志中的基准分数与本项目无关，不引用为产品效果。

精确网页内容没有声明本轮报价的未来有效截止日期。记录的是本次工具观察到的当前公开表，不凭页面时钟补造价格版本号或未来不变保证。

## 3. 官方事实与本地判断分开

### 3.1 endpoint 与当前模型

官方首页列出的 OpenAI 格式 base_url 为 `https://api.deepseek.com`；Chat Completions 文档对应 `POST https://api.deepseek.com/chat/completions`。当前请求模型名列 `deepseek-flash` 与 `deepseek-v4-pro`。[cite:203184f6-1][cite:1536378e-2]

官方当前将 `deepseek-flash` 对应 DeepSeek-V4.1-Flash、`deepseek-v4-pro` 对应 DeepSeek-V4-Pro-0813；旧 `deepseek-v4-flash`／`deepseek-v4-flash-vision-exp` 模型已退役，旧名请求兼容路由到 V4.1-Flash。更新日志也说明当前推荐使用 `deepseek-flash`。[cite:203184f6-1][cite:1536378e-1][cite:73cd5fa1-2]

**本地建议，待用户配置确认：**首次小范围方案解释采用 `deepseek-flash` 与 OpenAI Chat Completions 非流式路径，不采用 legacy 名或 Anthropic／Responses 多协议。它符合既有 DeepSeek 选择，但准确 model／endpoint 尚未由用户批准配置，不默认据本报告生成请求。

响应中的 `model` 是服务返回的实际模型名，必须记录并验证与已批准映射相容；文档列出可用请求名不等于本轮验证实际响应值。不得为了接受不一致结果无限扩 allowlist，服务变更需显式核对。

### 3.2 实际请求字段与 mock 差异

API 要求 `messages` 与 `model`；系统消息内容是字符串。`max_tokens` 限制 completion 生成长度，`stream=false` 为非流式；`response_format` 当前文档允许 text／json_object。[cite:1536378e-2]

在同 URL 浏览器 `main` 完整读取的关键定义：

- messages 的 content 为 string；结构化业务描述应规范序列化成字符串内容，而不是将 user.content 直接设为任意嵌套业务对象。
- max_tokens 范围 1–393216；未设置时非思考默认8K、思考默认64K，最高努力默认128K。这些都是服务参数／默认值，不是本项目实际预算或建议输出上限。
- response_format.type 的 enum 为 text、json_object；工具函数中的 strict 是另一工具调用能力，不能据此声称响应 json_object 强制本项目 JSON Schema。

本项目需要将 synthetic wire shape 改为实际受信编译器：

| 当前 mock 形态 | 后续实际适配 |
|---|---|
| `output_limit` | 明确已批准的 `max_tokens`；数值待预算配置，不用服务默认 |
| 顶层 `response_schema` | 本地仍保留 schema；请求使用 `response_format={"type":"json_object"}`，通过受控提示／示例描述结构 |
| user.content 是 dict | 编译成受控 JSON 字符串，嵌入符合文档的 messages |
| mock://local-only、synthetic-model | 只在测试存在；实际配置独立批准 HTTPS endpoint/model，未批准即拒绝 |
| mock input/output 两类 usage | 实际 prompt／completion 与 cache 分类提取、校验及有来源费率 |

上述是**适配建议，不是本轮修改代码许可**。synthetic 测试可以保留作为本地逻辑基础，不能伪装成真实协议。

### 3.3 JSON 结构化能力不是业务 schema 保证

官方 JSON Output 使用 `response_format={"type":"json_object"}`，提示需包含“json”并给预期格式示例；文档警告可能偶尔返回空内容，max_tokens 不合理会使 JSON 截断。[cite:4c76ec3b-3]

API 文档说明 `finish_reason=length` 对应输出／上下文限制；实际 choice 的 finish_reason 还可能是 content_filter、tool_calls、insufficient_system_resource、aborted 等，不能当正常解释成功。[cite:1536378e-2]

**本地判断：**无需为本闭环加入 tools 或 beta strict function；现有范围禁止模型工具调用。使用 json_object 加现有严格本地 JSON／字段／alias 校验，非 stop、空 content、截断、不合 schema 均受控失败、不补修、不重试。符合 frozen C208，不需要为了文档只保证合法 JSON 而放宽本地校验。

自由解释文字仍是 structurally_valid_draft、human_review_state=pending；官方支持 JSON 不证明其符合指标口径或业务事实。

### 3.4 非思考模式建议与输出计费边界

官方思考默认开启，默认努力 high。可通过 `thinking={"type":"disabled"}` 关闭；reasoning_effort=none 也表示关闭。reasoning_content 仅适用于思考模式。[cite:4c76ec3b-4][cite:1536378e-2]

API 对 max_tokens 的定义是限制模型生成 completion 的最大 token 数；response usage 描述 completion_tokens 与可选 completion_tokens_details.reasoning_tokens。[cite:1536378e-2]

**本地推荐：**首次方案解释明确非思考 `thinking.type=disabled`，不同时发冲突的 effort 开关，避免默认思考带来的返回内容／预算复杂性。不接 tools，不保存或外发 reasoning_content；如果非思考请求仍返回非空推理或非零 reasoning_tokens，安全记录异常及 usage，停止成功发布／后续付费，不把它当正常草稿。

max_tokens 是有文档依据的 completion 上限，但目前没有实际输出计费实测，也没有本轮读取到的额外承诺可以覆盖未知计费类别。非思考可缩小范围，**不能单靠参数名宣称所有未来模型输出费用已被硬上界证明**。后续必须绑定此 model、模式、费率与 usage 分类，在 mock 中拒绝异常计费类别；实际服务违约／超预留按既有 unknown_charge 门处理。

## 4. Token 计数：首请求前仍有实质缺口

官方 Token 页面给字符比例的是“approximately”，并明确实际 token 以模型 usage 返回为准，不能将字符比例当可靠预留上界。页面提供离线 tokenizer ZIP 的链接。[cite:4c76ec3b-5]

浏览器读取同页下载链接实际指向 `https://cdn.deepseek.com/api-docs/deepseek_v4_tokenizer.zip`；本轮只观察链接，没有请求该地址。

当前不能确认：

- ZIP 实际内容／来源字节摘要、许可证、依赖、tokenizer 版本与当前 Flash 的适用性。
- 是否提供完整 chat template 编码，包含 role／special token／JSON 模式、系统／用户边界或服务内部包装。
- 单独对 message 文本 tokenize 是否精确等于 prompt_tokens，或提供可靠保守上界。
- 使用 raw HTTP JSON body 字节数与实际输入 token 的可靠关系；不能自创“一个字节一定最多一个 token”来替代官方保证。

官方页面文字支持进一步核验工具，不证明它已安装／可运行或完整计数已验证。可靠输入上界不足时按 C205 继续禁止付费。

**最小下一技术步骤：**先独立申请官方 tokenizer 包的限定下载与静态检查（新 D 盘位置、实际摘要、内容／依赖／chat template 核对，不安装、不执行包代码），或用户提供已有可信计数资料。确定确实需要什么工具后再申请最小运行／依赖权限。若仍无完整输入上界依据，记录阻塞，不去做一次真实付费请求“测测差多少”。

替代的极宽输入上界需要本地可复核证明与用户明确预算选择，不在本报告直接使用服务 context length 当具体调用 token 上限或估算费用，也不为避免工具核验偷换 frozen 口径。

## 5. usage 与公开费率

### 5.1 usage 字段与算术口径

Chat Completions 文档列出 prompt_tokens、completion_tokens、total_tokens、prompt_cache_hit_tokens、prompt_cache_miss_tokens；prompt_tokens 等于 cache_hit＋cache_miss，total_tokens 等于 prompt＋completion。另有 prompt_tokens_details.cached_tokens 与可选 completion_tokens_details.reasoning_tokens。[cite:1536378e-2]

缓存指南也说明 hit／miss 两字段；缓存按最佳努力运行，不保证命中，缓存可能在服务端保留数小时到数天。[cite:1536378e-3]

**本地结算建议：**只根据真实返回的上述用量及已批准费率，用工具 Decimal 计算：

```text
usage_cost = (cache_hit_tokens × hit_rate
            + cache_miss_tokens × miss_rate
            + completion_tokens × output_rate) / price_unit
```

这只是待实现公式，不是本轮计算结果。reasoning_tokens 是 completion 细分时不得重复相加计费；分类含义或价格映射不明确就停止结算，不按字符数补 usage。缺必需字段、整型边界或合计不一致，保留风险额度。

调用前预留使用输入全 cache-miss 的最高适用费率，不假定缓存命中，也不把缓存带来的实际低费率当更小发送预算。未得到 provider 账单佐证的费用只能叫按 usage／费率计算成本，不声称实际扣款已认证。

服务端缓存机制是用户外发风险说明的一部分，不能宣称外发“不落盘”。本轮没有提交任何项目内容；将来实际 payload 仍需人审批最小内容。[cite:1536378e-3]

### 5.2 当前公开人民币价格表（不是已批准 policy）

中文官方价格页以百万 tokens 计价，币种人民币；下表由浏览器完整 `main` 文本与对应表格核对，不能拿英文美元表无汇率证据转换。[cite:1536378e-1]

| 模型／类别 | 空闲时段（元／百万 tokens） | 高峰时段（元／百万 tokens） |
|---|---:|---:|
| deepseek-flash 输入 cache hit | 0.02 | 0.04 |
| deepseek-flash 输入 cache miss | 1 | 2 |
| deepseek-flash 输出 | 4 | 8 |
| deepseek-v4-pro 输入 cache hit | 0.15 | 0.30 |
| deepseek-v4-pro 输入 cache miss | 4.5 | 9.0 |
| deepseek-v4-pro 输出 | 13.5 | 27.0 |

中文同页说明：北京时间周一至周五（不含中国法定节假日）9:00–12:00、14:00–18:00 为高峰，其余时段、周末与中国法定节假日全天为空闲；费用按 token 用量×价格扣减，赠送余额优先，价格可能变动。本轮没有账户信息或扣款验证。

英文同页另以美元报价：Flash hit 0.003／0.006、miss 0.15／0.3、output 0.6／1.2；Pro hit 0.022／0.044、miss 0.66／1.32、output 1.98／3.96（顺序均空闲／高峰，每百万 tokens）。英文时段使用 UTC 01:00–04:00、06:00–10:00。两套表是官方不同币种原值，不用它们自算换汇。

上述费率是此次官方页面观察值，无本轮费率发布／生效精确时间、不可变版本号或未来截止保证。配置应保存实际核对 URL、观察时间、币种／单位／全部类别与快照身份，首请求前必要时复核变化，不伪造“永久固定单价”。

**尚需明确：**实际账户使用哪个币种与余额；provider 对跨高峰边界的请求采用哪个时间点定价。本轮文档未确认请求提交、生成开始或 completion.created 哪个决定费率，不能用客户端时间擅自称精确实际成本。最高高峰费率可用于保守预留；把 usage×最高费率当结算时必须叫成本上界，不冒称实际扣费。真正精确结算仍需实际适用时段规则／证据或独立批准的清晰计费口径。

## 6. 非流式 transport 需要处理的协议细节

官方说明等待响应时，非流式请求可能连续收到空行；这些不影响 JSON body 解析。如果十分钟后仍未开始推理，服务器可能关闭连接。[cite:73cd5fa1-1]

因此实现整体 60 秒 deadline 时不能按每次读到 keep-alive 空行重新计时。所有接收字节（含前导空行）计入已冻结的 64 KiB wire body 限额；允许 JSON 的前导空白，不将超限内容截断再认成功。60秒本地停止不证明服务没有处理或计费，保持 unknown_charge 及无自动重试。

这里服务默认等待规则不替换本项目 frozen deadline；没有要求将60秒改成十分钟。原缓存／隔离文档的可选user_id也不纳入本项目请求，避免加入不必要标识字段。[cite:73cd5fa1-1]

实际 HTTPS 客户端、证书验证、禁代理／重定向、认证头保密、请求发送至读取全过程期限与安全响应校验仍待明确实现和受控测试。本轮没有构造客户端或请求目标服务。

## 7. 对当前 frozen 标准的影响

本次只补充真实官方事实，不修改 C201–C212。

- C202/C208：实际 content 为字符串、json_object模式及本地schema校验的路线已可设计；禁止直接发送mock body。
- C204：endpoint／当前推荐模型名与非思考开关已有公共文档依据，但用户未批准准确配置、实际服务未运行。
- C205：输入完整计数可靠性、全部计费输出上界与费率适用性仍有首请求前缺口。
- C206/C209：可将cache hit／miss／completion分账加入真实usage映射，须保留不确定计费停止门，不能用现有二类mockusage直接结算真实响应。
- C207/C211：实际non-stream keep-alive提示明确，仍须完成真实transport与产品prepare/call协议、持久顺序及故障证据。
- C212：没有真实生成请求，仍未验收。

结构化模式支持与本地严格校验相容，不需要为了JSON能力引入tools或放宽响应契约。下载tokenizer、安装依赖、准确model与预算配置、真实payload准备／外发／调用则都有各自许可门。

## 8. 最小续作安排

**建议先计数依据核验，再单批真实适配的离线实现／测试。**

1. 请求限定官方 tokenizer 包下载／静态检查许可，或用户提供可用计数证据；不顺带安装／执行、不读key或调用模型。下载域不是本轮已批准同站文档范围，必须新批准。
2. 取得完整输入计数／模式与计费依据后，由规划方一次给真实适配闭环：实际body编译、单服务transport、usage映射、真实scope／批准对象及prepare/call本地协议，按ADR-007合并离线实现／测试／结果文档，单批交回。
3. 用户确认实际provider/model/mode、币种、余额与累计数值，再冻结独立policy。建议候选是官方直接 `deepseek-flash`／非思考，不等于已经选择或授权。
4. 固定真实上游prepare属于真实摘要工具读取，另许可；完整实际payload可见后才OUTBOUND，再批准一次CALL。未满足可靠上界／实际余额／限额就不付费。

余额、密钥来源、具体累计request/token/费用数值本轮不提前重问，等待对应policy门；不因公共资料已知就自动试请求。若用户选择不同DeepSeek服务或model，核对资料与实现范围重新绑定，不能偷偷换路由。

## 9. 本轮交付与未验证项

本轮只新建本文并更新 INDEX；不改代码、测试、标准、ADR、旧执行记录或证据，不运行命令。

尚未取得：账户币种／余额、密钥存在性、tokenizer字节／chat template及运行计数、模型输出／usage实测、精确费用／扣款、实际 transport与首请求成功证据。

没有新增ADR，没有发布执行交接，没有业务选择或外发批准。下一步仍需明确限定下载／静态检查权限；本报告不会代替该请求，也不会以公开表填真实policy。

**W2-B2整体仍未验收；L1限定通过保持。** W1最后生产计算与修复后合成收尾保持分离，不重验、不重装、不重跑CSV。所有既有证据稳定保留。
