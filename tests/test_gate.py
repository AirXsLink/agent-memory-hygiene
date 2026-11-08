"""Write gate: every rule, plus the statements it must not reject."""

from agent_memory_hygiene import MemoryHygieneConfig, assess_write, should_write


def test_empty_is_empty() -> None:
    assert assess_write("").reason == "empty"
    assert should_write("") is False


def test_whitespace_is_empty() -> None:
    assert assess_write("   \n\t").reason == "empty"


def test_too_short_is_rejected() -> None:
    assert assess_write("嗯嗯").reason == "too_short"


def test_exactly_min_chars_passes() -> None:
    assert should_write("用户喜欢喝咖啡和茶") is True


def test_too_long_is_rejected() -> None:
    assert assess_write("字" * 2001).reason == "too_long"


def test_too_many_lines_is_rejected() -> None:
    text = "\n".join(f"第 {i} 行的内容" for i in range(13))
    assert assess_write(text).reason == "too_many_lines"


def test_traceback_is_rejected() -> None:
    text = 'Traceback (most recent call last):\n  File "app.py", line 3, in <module>'
    assert assess_write(text).reason == "error_dump"


def test_winerror_is_rejected() -> None:
    assert assess_write("OSError: WinError 10054 连接被重置").reason == "error_dump"


def test_link_only_is_rejected() -> None:
    assert assess_write("https://example.com/a/b/c").reason == "link_only"


def test_url_with_content_passes() -> None:
    text = "数据库迁移的完整说明文档在这里 https://example.com/a"
    assert should_write(text) is True


def test_question_mark_is_rejected() -> None:
    assert assess_write("明天下午的会议是几点？").reason == "question"


def test_question_particle_is_rejected() -> None:
    assert assess_write("你今天中午吃饭了吗").reason == "question"


def test_statement_ending_with_ne_passes() -> None:
    # "呢" alone is not a question marker; this is a statement.
    assert should_write("本鱼一直都在这里呢") is True


def test_chitchat_is_rejected() -> None:
    assert assess_write("好的好的好的好的").reason == "chitchat"


def test_normal_fact_passes() -> None:
    assert should_write("用户养了一只橘猫叫年糕") is True


def test_verdict_reports_metrics() -> None:
    verdict = assess_write("用户喜欢喝咖啡和茶")
    assert verdict.ok is True
    assert verdict.metrics["chars"] == 9
    assert verdict.metrics["lines"] == 1
    assert verdict.metrics["urls"] == 0


def test_min_chars_is_configurable() -> None:
    cfg = MemoryHygieneConfig(min_chars=4)
    assert assess_write("用户喜欢", cfg).ok is True
