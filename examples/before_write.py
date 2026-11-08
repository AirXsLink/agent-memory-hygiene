"""Example: gate candidate memories before writing them to a store."""

from agent_memory_hygiene import (
    MemoryHygieneConfig,
    assess_attribution,
    assess_write,
)

SAMPLES = [
    "用户喜欢喝咖啡和茶",
    "明天下午的会议是几点？",
    "好的好的好的好的",
    'Traceback (most recent call last):\n  File "app.py", line 3',
    "小雨的妈妈是老师",
    "豆豆特别能吃",
]


def main() -> None:
    cfg = MemoryHygieneConfig(known_pets=("豆豆",))
    for text in SAMPLES:
        verdict = assess_write(text, cfg)
        risk = assess_attribution(text, cfg)
        subject = (
            f" kind={risk.kind} subject={risk.subject}" if risk.shifted else ""
        )
        first_line = text.splitlines()[0]
        print(f"{first_line!r}: ok={verdict.ok} reason={verdict.reason}{subject}")


if __name__ == "__main__":
    main()
