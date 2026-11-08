# agent-memory-hygiene

[English](https://github.com/AirXsLink/agent-memory-hygiene/blob/main/README.md) | [简体中文](https://github.com/AirXsLink/agent-memory-hygiene/blob/main/README.zh-CN.md)

Agent 记忆的写入端卫生：什么该存、什么该丢、这条事实记到谁头上。

## 问题

大多数 agent 记忆项目都在优化检索：向量、重排、时间衰减、相似度阈值。很少人先问一个更便宜的问题：**这条东西当初就不该写进去吧？**

什么都收的库会变成日志。工具输出、报错堆栈、粘贴的链接、提问和寒暄都漂进去，最后只能靠「把检索阈值调高」在读取端打补丁。那是检索端的补丁，不是写入端的判据。

第二个失败是归属。抽取器把「小雨的妈妈是老师」写成「用户是老师」，把「豆豆特别能吃」写成「用户特别能吃」。事实是真的，主语错了。检索端发现不了——存下来的句子看起来完全正常。

这个库用纯函数覆盖这两件事，不调用任何模型。

**速览：**

| 输入 | 决策 |
| --- | --- |
| 空串 / 纯空白 | `empty` |
| 短于 8 字 | `too_short` |
| 长于 2000 字 | `too_long` |
| 非空行超过 12 行 | `too_many_lines` |
| 含 Traceback / `WinError` | `error_dump` |
| 只有链接、正文很少 | `link_only` |
| 以短问句收尾 | `question` |
| 短寒暄 | `chitchat` |
| 其余 | `ok` |
| 「我的妈妈是老师」 | `relation_subject` 标记 |
| 「豆豆特别能吃」（豆豆是已知宠物） | `pet_subject` 标记 |

## 安装

```bash
pip install -e .
```

## 快速开始

```python
from agent_memory_hygiene import MemoryHygieneConfig, assess_write, assess_attribution

verdict = assess_write("用户喜欢喝咖啡和茶")
print(verdict.ok, verdict.reason)        # True ok

verdict = assess_write("明天下午的会议是几点？")
print(verdict.ok, verdict.reason)        # False question

cfg = MemoryHygieneConfig(known_pets=("豆豆",))
risk = assess_attribution("豆豆特别能吃", cfg)
print(risk.shifted, risk.kind, risk.subject)  # True pet 豆豆
```

## 写入判据

判据刻意保持简单。每条规则回答一个不需要模型的问题：

- **过程不是记忆。** 堆栈和工具输出可以重新得到。存「症状 → 根因」，不存转录。
- **体积是信号。** 一条「记忆」比一屏还长，它多半是转录，不是结论。
- **提问不是事实。** 「明天几点开会？」是一个请求，记住它只会污染检索。
- **寒暄不是事实。** 「ok」「嗯嗯」「好的好的」不携带信息。

`assess_write` 返回 `WriteVerdict`：`ok`、`reason`、命中的规则，以及计数（`chars`、`meaningful_chars`、`lines`、`urls`）。把原因记进日志；静默丢弃和「判据根本没加载」在日志上完全一样。

## 主语归属

`assess_attribution` 标记两种形状：

- **relation**：`X 的 <关系名词> ...` —— 这条事实属于关系人，不属于说话人。
- **pet**：已知宠物名后面跟着动词或形容词 —— 这条事实属于宠物。

它**不改写**文本。改写需要你的抽取器或模型，而库不该悄悄改变存进去的东西。标记足以挡住最常见的失败。

## Fail-open，但要留痕

```python
from agent_memory_hygiene import safe_assess_write

verdict = safe_assess_write(text)
if verdict.reason == "fail_open":
    ...  # 判据自己崩了；写入被放行，同时打了 warning
```

判据本身坏掉时，不能把主流程卡死。但「判据全放行」和「判据根本没加载」在日志上完全一样，所以包装器一定先打日志再放行。

## 它不做什么

- 不调用任何模型。
- 不存储记忆，不拥有数据库。
- 不连接向量库或 embedding 服务。
- 不改写文本，只返回判定。

## 这个库刻意止步的地方

- **重要性。** 它判断不了一条事实对用户重不重要，那需要调用方的领域知识或模型。
- **去重。** 近义去重需要 embedding；这个库刻意保持零依赖。
- **多语言规则。** 默认规则面向中文，因为归属失败是在中文场景观察到的；阈值可配，短语表不穷尽。
- **归属改写。** 标记便宜且安全；改写给抽取器做。

## 测试

```bash
pytest -q
```

## 许可证

MIT
