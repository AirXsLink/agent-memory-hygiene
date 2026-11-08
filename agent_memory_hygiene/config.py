"""Configuration for write-time memory hygiene."""

from dataclasses import dataclass


@dataclass
class MemoryHygieneConfig:
    """Thresholds for deciding whether a piece of text is worth storing.

    Defaults come from a production chat bot: ``min_chars`` blocks greetings
    such as "ok" and "嗯嗯", ``max_chars`` / ``max_lines`` block pasted logs,
    and ``question_max_chars`` keeps short questions out of the memory store.
    """

    #: Shorter texts are treated as noise (greetings, acknowledgements).
    min_chars: int = 8
    #: Longer texts are almost always tool output or pasted logs.
    max_chars: int = 2000
    #: Non-empty lines; a conclusion should fit on a screen.
    max_lines: int = 12
    #: Questions longer than this are not classified as questions.
    question_max_chars: int = 80
    #: Texts shorter than this are checked against the chitchat pattern.
    chitchat_max_chars: int = 16
    #: A URL-only text is dropped when less than this much content remains.
    link_min_remaining_chars: int = 12
    #: Names that should be attributed to a pet, not to the user.
    known_pets: tuple[str, ...] = ()
    #: Whether ``assess_attribution`` is applied by the caller. Kept as a flag
    #: so an adapter can disable the heuristic without changing call sites.
    check_attribution: bool = True
