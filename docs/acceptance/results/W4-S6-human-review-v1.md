# 无模型S6独立人工审核记录 v1

状态：实际决定已记录，固定包字节核验通过，待high按H601–H606核对。执行方不自行宣布S6验收通过、案例闭环完成或全部W4完成。本文件是文档化人工审核，不是新增S6产品功能run／CLI／JSON终态。

## 1. 实际人工决定及许可

- decision：approve_limited_interpretation。
- actor：user；用户明确确认此本地标记代表当前用户，不声称身份认证。
- review_source：用户自行在本地审阅固定report.md后明确回复，不由核验工具或记录方代签。
- confirmation_basis：用户明确表示“我已审阅上述固定报告，选择approve_limited_interpretation，接受限定解释及全部限制”，并确认actor=user、confirmed_at=not_provided；另分别批准P-S6-LOCAL-RECORD-V1的固定七文件读取、准确单次字节核验及本文／INDEX写入，零重跑。
- confirmed_at：not_provided。未提供用户字面确认时间，不代填时区／秒，不使用工具时间或run日期代替。
- scope：S6_local_limited_interpretation_only。
- external_release：not_authorized。
- authorization：P-S6-LOCAL-RECORD-V1。三个效力分别为必要读取／核验许可、用户实际业务决定、本地文档／导航写入许可，不互相推定。
- bound_versions：W4-S6-no-model-v1 frozen、W4-S6-no-model-plan-v1 accepted、W3-final-review-v1、W4-S6-no-model-sol61-low-v1、ADR-003／005／007／008／009／010。

用户只决定是否接受固定报告的限定解释，不承担hash算法、S5实现或技术验收认证责任。规划／验收方负责技术判定，执行方仅记录真实选择和工具证据。

## 2. 固定对象与必要身份

项目根：D:\MyPythonProjects\datainsight。
固定run：outputs/W3/analysis-e3-real-v1-a/。
固定报告：outputs/W3/analysis-e3-real-v1-a/report.md。
技术前置：docs/acceptance/results/W3-final-review-v1.md，W3已通过；本轮不重验W3、不重算数据。

本次terminal实际核验当前文件字节与必要引用，再比较交接固定已验收锚，verification_state=passed，命令退出0。

|必要产物|核验相符的工具SHA-256|
|---|---|
|report.md|a843329fb63a5ce8638a348667cef31e082673a2252022691a98e1c2c5b380bd|
|bindings.json|59401aec63c30e65b39351d4488b2e17e7a4f00449c10aec688b2dbbb929da4f|
|calculation-evidence.json|4fc1d869fb4411db9c28ed09fdef24224d3668ce6b3cb45b3b1a2690ee89417e|
|result.json|020942cc3f09d73b28d8aa4daf2ced9d92c754cafa9491c44b410b493d299861|
|validation.json|7a49f84cf7e30306958e6a5f7a93a3c41b736d9eb3bfd5860a54a9472b1d85ec|
|operation.json|01fa6b9b9fd28fe29359f95d40a961a2b67a7ced1353d7f130b43290cce5248a|

其他必要身份引用仅在固定包内消费，不跟随其路径打开上游文件：

- dataset_version：7095a57fbd6eb1292bec5ccde4713ac256678b8551eb478d3b5aaad89612cfb4；bindings.json#/dataset_version，本次只比较保存身份，没有读取CSV或计算当前源hash。
- question：bindings.json#/question_identity，ref=configs/w2a-question-v1.json、version=v1、hash=200ae28ffb5492c3bc891eec16896f85ca103324ec8117a4885ea867d7fa9889。
- rules：bindings.json#/diagnostic_rules_identity，id=W2-A、version=v1、hash=5b373b52fb33f509f2f73892697aff2c22d1cf35ea2533a1c51b8fd0f04675a7。
- method／plan：bindings.json#/plan，M-BEHAVIOUR-RECORDS／P-BEHAVIOUR-RECORDS、plan_version=v1。
- registry：bindings.json#/registry_identity，id=W2-B1、version=v1、hash=c158f87f997a07404d9faddfa578a72f19f56c607b8d2316f86db80f2b9cbc30。
- metric：bindings.json#/plan/metric_definition，metric_definition_version=v1、hash=567762be0d1ea69a2b3095b8132fee269e15e2288a86dc3dc486eb3fac6d7951。
- strategy：calculation-evidence.json#/strategy_ref，outputs/W3/strategy-g35-real-v1-a/strategy.json，工具保存hash=c081b59260443bded2c1695fdddf755b55df414478bd3b51f4505e1230f70160。本轮没有打开该策略run，引用已验收绑定，不重做G3.5。
- result：固定result.json；报告value_ref指向该文件桶值，计算SQL引用calculation-evidence.json#/sql/behaviours。本轮无新计算或新数值结论。

## 3. 被接受的解释及限制

用户接受的仅是：在指定真实文件版本和既有已批口径下，描述固定行为代码的原始记录数；pv／fav／cart／buy只按精确文本分桶，NULL进入missing，其他非NULL进入other。

全文件版本窗口、原始记录全部保留；不去重、过滤、填补、trim或改大小写。不是订单／支付、独立用户、比例／转化、日期覆盖、总体推广、因果或业务效果，不认证天然代码业务语义、源数据真实性或代表性，不批准行动或外发。

没有请求扩大结论，没有模型解释或新指标。审核数值沿用已验收工具结果和固定报告，不心算业务效果或产生估计。

## 4. 单次字节核验命令及实际证据

仅运行下面命令一次，自动重跑0；不生成脚本，不调用execute、load_strategy、load_w3_context、verify_review、SQL／画像查询或worker。

```bash
cd /d/MyPythonProjects/datainsight && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH='D:\MyPythonProjects\datainsight\src' TEMP='D:\MyPythonProjects\datainsight\.cache\tmp' TMP='D:\MyPythonProjects\datainsight\.cache\tmp' TMPDIR='D:\MyPythonProjects\datainsight\.cache\tmp' .venv/Scripts/python.exe -B - <<'PY'
from pathlib import Path
import json
import sys
from datainsight import analysis as a
try:
    directory = Path('D:/MyPythonProjects/datainsight/outputs/W3/analysis-e3-real-v1-a')
    terminal = a.terminal(directory, 'execute')
    anchors = {
        'bindings.json': '59401aec63c30e65b39351d4488b2e17e7a4f00449c10aec688b2dbbb929da4f',
        'calculation-evidence.json': '4fc1d869fb4411db9c28ed09fdef24224d3668ce6b3cb45b3b1a2690ee89417e',
        'operation.json': '01fa6b9b9fd28fe29359f95d40a961a2b67a7ced1353d7f130b43290cce5248a',
        'report.md': 'a843329fb63a5ce8638a348667cef31e082673a2252022691a98e1c2c5b380bd',
        'result.json': '020942cc3f09d73b28d8aa4daf2ced9d92c754cafa9491c44b410b493d299861',
        'validation.json': '7a49f84cf7e30306958e6a5f7a93a3c41b736d9eb3bfd5860a54a9472b1d85ec',
    }
    if terminal['required_hashes'] != anchors:
        raise ValueError('review_anchor_changed')
    bindings = a.f.parse(a.read(directory / 'bindings.json'))
    validation = a.f.parse(a.read(directory / 'validation.json'))
    evidence = a.f.parse(a.read(directory / 'calculation-evidence.json'))
    if set(validation) != {'execution', 'metric', 'boundary'} or any(v.get('state') != 'pass' for v in validation.values()):
        raise ValueError('review_validation_not_passed')
    if bindings['dataset_version'] != '7095a57fbd6eb1292bec5ccde4713ac256678b8551eb478d3b5aaad89612cfb4':
        raise ValueError('review_dataset_changed')
    if bindings['plan']['metric_definition_hash'] != '567762be0d1ea69a2b3095b8132fee269e15e2288a86dc3dc486eb3fac6d7951':
        raise ValueError('review_metric_changed')
    if bindings['plan']['method_id'] != 'M-BEHAVIOUR-RECORDS' or evidence['strategy_ref'] != 'outputs/W3/strategy-g35-real-v1-a/strategy.json':
        raise ValueError('review_object_changed')
    print(json.dumps({'verification_state': 'passed', 'run_ref': 'outputs/W3/analysis-e3-real-v1-a/',
        'required_hashes': anchors, 'dataset_version': bindings['dataset_version'],
        'metric_definition_hash': bindings['plan']['metric_definition_hash'],
        'strategy_ref': evidence['strategy_ref'], 'strategy_hash': evidence['strategy_hash'],
        'recorded_at': a.f.now(), 'recorded_at_source': 'python_datetime_utc',
        'scope': 'fixed_report_identity_check_only', 'model_usage': 'not_applicable'}, ensure_ascii=True))
except Exception:
    print(json.dumps({'verification_state': 'failed', 'reason_code': 'fixed_report_verification_failed'}))
    sys.exit(1)
PY
```

实际cwd／环境如上。terminal核验合法execute success、必要当前字节hash，再与固定锚相符；少量元数据检查确认S5三层pass、固定数据／口径／方法及策略引用。stdout verification_state=passed、scope=fixed_report_identity_check_only、model_usage=not_applicable，进程退出0。

工具输出recorded_at=2026-10-14T10:43:52.769332+00:00，recorded_at_source=python_datetime_utc。此值仅是本次固定包核验记录时刻，不是用户确认时刻或本文文件落盘时间。本文实际精确写入时刻未取得：document_recorded_at=null、document_recorded_at_source=not_available、document_recorded_at_status=unavailable；未另跑取时命令，不以历史工具时间代填。

读取只固定七文件及允许规范／导入依赖；没有生产CSV、其他run、上游全链、密钥／.env／账户、网络、SQL、模型或安装。Python／DuckDB仅现有包导入，没有引擎连接。本轮未修改固定run、源码或报告pending，没有新增S6运行协议。产品费用not_applicable；开发token／金额／耗时unknown。

## 5. H601–H606记录检查（待high判定）

|ID|执行方记录检查／实际证据|技术判定|
|---|---|---|
|H601|W3权威通过；固定包一次terminal核验成功、S5三层pass、当前必要字节与锚相符|待high|
|H602|用户明确已本地审阅固定报告并选择approve_limited_interpretation；actor映射和实际决定来源明确，不以技术核验代替决定|待high|
|H603|仅接受行为代码原始记录数及全部列明限制，无新指标／效果／行动或外发|待high|
|H604|本文独立保存决定及report／data／question／rules／method／metric／strategy／result必要绑定，旧run不回填|待high|
|H605|confirmed_at=not_provided；工具核验时间独立，精确文档落盘时间unavailable；scope限定本地、external_release未授权|待high|
|H606|决定已记录、待high核对；未宣称S6验收／案例闭环或全部W4完成，非产品S6自动化|待high|

反向底线按冻结标准：缺实际决定、锚／run不符、缺合法success或S5、版本变化、伪造时间或扩张解释均不登记有效approve；reject/cancel不形成案例完成。本轮没有制造反向fixture、故障矩阵或重新计算生产数据。

## 6. 一次交回与停止状态

记录动作完成，无本次工具核验失败或新增记录缺口；单次核验额度已消耗，不重跑。INDEX仅新增本审核记录导航，旧技术记录／report／final-status中的pending保持原历史语义。

下一步仅交回high只读核对实际决定及本文绑定。只有high核对有效approve后才可判定S6通过并称该指定案例S4→S5→S6完成；不因此完成全部W4、产品v2或报告外发。当前没有新增功能代码、模型／外发安排或ADR，产品v2三通道仍只登记，旧C205未满足保持。
