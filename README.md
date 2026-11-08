# agent-memory-hygiene

[English](https://github.com/AirXsLink/agent-memory-hygiene/blob/main/README.md) | [简体中文](https://github.com/AirXsLink/agent-memory-hygiene/blob/main/README.zh-CN.md)

Pure-policy write-time hygiene for agent memory: what to store, what to drop, and whose fact it is.

## Problem

Most agent-memory projects optimize retrieval: embeddings, re-ranking, recency, similarity thresholds. Very few ask the cheaper question first: **should this ever have been written?**

A store that accepts everything becomes a log. Tool output, stack traces, pasted links, questions and greetings all drift in, and the only remaining defense is a higher similarity threshold at read time. That is a patch on the retrieval side, not a decision on the write side.

The second failure is attribution. An extractor turns "小雨的妈妈是老师" into "the user is a teacher", or "豆豆特别能吃" into "the user eats a lot". The fact is real; the subject is wrong. Retrieval cannot detect this, because the stored sentence looks perfectly normal.

This library covers both, with pure functions and no model calls.

**At a glance:**

| Input | Decision |
| --- | --- |
| `""` / whitespace | `empty` |
| Shorter than 8 chars | `too_short` |
| Longer than 2000 chars | `too_long` |
| More than 12 non-empty lines | `too_many_lines` |
| Contains a traceback / `WinError` | `error_dump` |
| Only a URL, little else | `link_only` |
| Ends as a short question | `question` |
| Short greeting | `chitchat` |
| Everything else | `ok` |
| "我的妈妈是老师" | `relation_subject` flag |
| "豆豆特别能吃" (豆豆 is a known pet) | `pet_subject` flag |

## Install

```bash
pip install -e .
```

## Quick Start

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

## The Write Gate

The gate is deliberately simple. Each rule answers a question that does not need a model:

- **Process is not memory.** Stack traces and tool output can be re-derived. Store the symptom and the root cause, not the transcript.
- **Volume is a signal.** If a "memory" is longer than a screen, it is probably a transcript.
- **Questions are not facts.** "What time is the meeting tomorrow?" is a request. Remembering it only pollutes retrieval.
- **Greetings are not facts.** "ok", "嗯嗯", "好的好的" carry no information.

`assess_write` returns a `WriteVerdict` with `ok`, `reason`, the rule that fired and the metrics (`chars`, `meaningful_chars`, `lines`, `urls`). Log the reason; a silent drop is indistinguishable from a gate that never ran.

## Subject Attribution

`assess_attribution` flags two shapes:

- **relation**: `X 的 <relation-noun> ...` — the fact belongs to the relation, not to the speaker.
- **pet**: a known pet name followed by a verb or adjective — the fact belongs to the pet.

It does **not** rewrite the text. A rewrite needs your extractor or a model, and a library should not silently change what gets stored. The flag is enough to stop the common failure.

## Fail Open, Loudly

```python
from agent_memory_hygiene import safe_assess_write

verdict = safe_assess_write(text)
if verdict.reason == "fail_open":
    ...  # the gate broke; the write was allowed and a warning was logged
```

A write gate must not block the main flow when the gate itself breaks. But "the gate allowed everything" and "the gate never loaded" look identical in logs, so the wrapper always logs the exception before allowing the write.

## What it does NOT do

- Calls no model.
- Stores no memory and owns no database.
- Connects to no vector store or embedding service.
- Rewrites nothing; it only returns verdicts.

## Where this kit deliberately stops

- **Importance.** It cannot tell whether a fact matters to the user. That needs the caller's domain knowledge or a model.
- **Deduplication.** Near-duplicate detection needs embeddings; this kit is zero-dependency on purpose.
- **Multilingual rules.** The default patterns target Chinese text, which is where the attribution failures were observed. The thresholds are configurable, the phrase lists are not exhaustive.
- **Attribution rewriting.** Flagging is cheap and safe; rewriting needs the extractor.

## Test

```bash
pytest -q
```

## License

MIT
