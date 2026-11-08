"""Subject attribution: whose fact is this?

LLM extraction often assigns a fact to the wrong subject. Two shapes recur in
production:

1. **relation** - "小雨的妈妈是老师" or "我的妈妈是老师". The fact belongs to
   the relation, not to the speaker. Storing "the user is a teacher" is wrong.
2. **pet** - "豆豆特别能吃". If the speaker has a pet named "豆豆", the fact
   belongs to the pet, not to the speaker.

The heuristics only *flag* the risk; they never rewrite the text. A rewrite
needs the caller's extractor or a model, and a library should not silently
change what gets stored. Flagging is enough to stop the common failure: a
fact silently attached to the wrong person.
"""

import re
from dataclasses import dataclass
from typing import Optional

from .config import MemoryHygieneConfig

#: Nouns that introduce a relation subject after "X 的".
RELATION_NOUNS: tuple[str, ...] = (
    "妈妈",
    "爸爸",
    "父母",
    "母亲",
    "父亲",
    "老婆",
    "老公",
    "妻子",
    "丈夫",
    "儿子",
    "女儿",
    "孩子",
    "哥哥",
    "姐姐",
    "弟弟",
    "妹妹",
    "朋友",
    "同事",
    "老板",
    "老师",
    "同学",
    "室友",
)

_RELATION_RE = re.compile(
    r"^(?P<subject>(?:我|用户|本人|[\u4e00-\u9fff]{2,4}))"
    r"的(?P<relation>" + "|".join(RELATION_NOUNS) + r")"
)

#: Characters that commonly follow a pet name when the sentence is about the
#: pet rather than about the speaker.
_PET_FOLLOW_CHARS = frozenset("很特也能会在是有喜欢叫爱吃得")


@dataclass
class AttributionRisk:
    """The result of checking whether a fact is attached to the wrong subject.

    ``reason`` is ``"ok"`` when no risk was found; otherwise it is
    ``"relation_subject"`` or ``"pet_subject"``.
    """

    shifted: bool
    kind: Optional[str]
    subject: Optional[str]
    reason: str


def _relation_subject(text: str) -> Optional[str]:
    match = _RELATION_RE.match(text)
    if not match:
        return None
    return match.group(0).replace("的" + match.group("relation"), "")


def _pet_subject(text: str, cfg: MemoryHygieneConfig) -> Optional[str]:
    for pet in cfg.known_pets:
        if not pet or not text.startswith(pet):
            continue
        remainder = text[len(pet) :]
        if remainder and remainder[0] in _PET_FOLLOW_CHARS:
            return pet
    return None


def assess_attribution(
    text: Optional[str], cfg: Optional[MemoryHygieneConfig] = None
) -> AttributionRisk:
    """Return whether ``text`` looks like a fact about someone else.

    This is a flag, not a correction: a ``True`` means the caller should keep
    the relation/pet in the stored fact instead of collapsing it onto the user.
    """
    cfg = cfg or MemoryHygieneConfig()
    if not cfg.check_attribution or not text:
        return AttributionRisk(False, None, None, "ok")

    relation = _relation_subject(text)
    if relation:
        return AttributionRisk(True, "relation", relation, "relation_subject")

    pet = _pet_subject(text, cfg)
    if pet:
        return AttributionRisk(True, "pet", pet, "pet_subject")

    return AttributionRisk(False, None, None, "ok")
