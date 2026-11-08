"""Fail-open behavior: permissive on errors, but never silent."""

import logging

from agent_memory_hygiene import MemoryHygieneConfig, safe_assess_write


class RecordingLogger(logging.Logger):
    def __init__(self) -> None:
        super().__init__("test")
        self.messages: list[str] = []

    def warning(self, msg: str, *args: object, **kwargs: object) -> None:
        self.messages.append(msg % args)


def test_normal_path_returns_verdict() -> None:
    verdict = safe_assess_write("用户喜欢喝咖啡和茶")
    assert verdict.ok is True
    assert verdict.reason == "ok"


def test_exception_fails_open(monkeypatch) -> None:
    def boom(text, cfg=None):
        raise RuntimeError("gate exploded")

    monkeypatch.setattr("agent_memory_hygiene.fail_open.assess_write", boom)
    verdict = safe_assess_write("用户喜欢喝咖啡和茶")
    assert verdict.ok is True
    assert verdict.reason == "fail_open"
    assert verdict.rule == "exception"


def test_warning_is_logged(monkeypatch) -> None:
    def boom(text, cfg=None):
        raise RuntimeError("gate exploded")

    monkeypatch.setattr("agent_memory_hygiene.fail_open.assess_write", boom)
    recorder = RecordingLogger()
    verdict = safe_assess_write(
        "用户喜欢喝咖啡和茶", MemoryHygieneConfig(), logger=recorder
    )
    assert verdict.reason == "fail_open"
    assert any("failed open" in message for message in recorder.messages)
