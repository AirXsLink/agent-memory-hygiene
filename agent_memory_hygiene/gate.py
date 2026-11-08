"""Write gate: decide what deserves to enter a long-term memory store.

Every function is pure: no model calls, no I/O. The gate encodes four
observations from a production agent:

1. **Process is not memory.** Tool output, stack traces and pasted links are
   re-derivable; storing them turns the store into a log.
2. **Volume is a signal.** A "memory" longer than a screen is usually a
   transcript, and a transcript is not a conclusion.
3. **Questions are not facts.** "What time is it tomorrow?" is a request, not
   something to remember.
4. **A write gate must fail open, but loudly.** If the gate itself breaks, the
   caller should still be able to write; the failure must be logged, because
   "the gate allowed everything" and "the gate never loaded" look identical.

The gate returns a :class:`WriteVerdict` with the reason and the metrics that
produced it, so a rejection can be logged instead of silently dropped.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Optional

from .config import MemoryHygieneConfig

_ERROR_RE = re.compile(
    r"Traceback \(most recent call last\)"
    r"|File \"[^\"]+\", line \d+"
    r"|\bat [\w.$]+:\d+:\d+"
    r"|^\s*Error[:：]"
    r"|Exception[:：]"
    r"|WinError \d+",
    re.MULTILINE,
)
_URL_RE = re.compile(r"https?://\S+")
_CHITCHAT_RE = re.compile(
    r"^[\s，。！？、~～…哈嗯哦啊呀吧呢了的是好好行可以收到明白okOK表情图片]*$"
)
_QUESTION_ENDINGS = ("？", "?")
_QUESTION_PHRASES = (
    "是什么",
    "是谁",
    "在哪里",
    "在哪儿",
    "几点",
    "怎么办",
    "多少钱",
    "哪一个",
    "哪个",
)


@dataclass
class WriteVerdict:
    """The result of assessing one candidate memory.

    ``rule`` names the specific check that fired, which is what a log line
    needs; ``reason`` is the stable category an adapter can switch on.
    """

    ok: bool
    reason: str
    rule: str
    metrics: dict[str, Any] = field(default_factory=dict)


def _metrics(text: str) -> dict[str, Any]:
    lines = [line for line in text.splitlines() if line.strip()]
    return {
        "chars": len(text),
        "meaningful_chars": sum(1 for char in text if char.isalnum()),
        "lines": len(lines),
        "urls": len(_URL_RE.findall(text)),
    }


def _is_question(text: str, cfg: MemoryHygieneConfig) -> bool:
    if len(text) > cfg.question_max_chars:
        return False
    if text.endswith(_QUESTION_ENDINGS):
        return True
    # "吗" is an unambiguous question particle in Chinese.
    if text.endswith("吗"):
        return True
    # Bare interrogatives ("谁", "呢") are deliberately not enough: they also
    # end statements such as "本鱼在呢".
    return any(text.endswith(phrase) for phrase in _QUESTION_PHRASES)


def assess_write(
    text: Optional[str], cfg: Optional[MemoryHygieneConfig] = None
) -> WriteVerdict:
    """Assess one candidate memory and return the verdict plus its evidence."""
    cfg = cfg or MemoryHygieneConfig()
    raw = text or ""
    stripped = raw.strip()
    metrics = _metrics(stripped)

    if not stripped:
        return WriteVerdict(False, "empty", "empty", metrics)

    if len(stripped) < cfg.min_chars:
        return WriteVerdict(False, "too_short", "min_chars", metrics)

    if len(stripped) > cfg.max_chars:
        return WriteVerdict(False, "too_long", "max_chars", metrics)

    if metrics["lines"] > cfg.max_lines:
        return WriteVerdict(False, "too_many_lines", "max_lines", metrics)

    if _ERROR_RE.search(stripped):
        return WriteVerdict(False, "error_dump", "error_pattern", metrics)

    if _URL_RE.search(stripped):
        remainder = _URL_RE.sub("", stripped).strip(" \t\r\n，。、")
        if len(remainder) < cfg.link_min_remaining_chars:
            return WriteVerdict(False, "link_only", "url_only", metrics)

    if _is_question(stripped, cfg):
        return WriteVerdict(False, "question", "question_ending", metrics)

    if len(stripped) < cfg.chitchat_max_chars and _CHITCHAT_RE.match(stripped):
        return WriteVerdict(False, "chitchat", "chitchat_pattern", metrics)

    return WriteVerdict(True, "ok", "ok", metrics)


def should_write(
    text: Optional[str], cfg: Optional[MemoryHygieneConfig] = None
) -> bool:
    """Convenience wrapper: True when the text passes every write rule."""
    return assess_write(text, cfg).ok
