"""Subject attribution: facts about relations and pets are not facts about the user."""

from agent_memory_hygiene import MemoryHygieneConfig, assess_attribution


def test_relation_with_pronoun() -> None:
    risk = assess_attribution("我的妈妈是老师")
    assert risk.shifted is True
    assert risk.kind == "relation"
    assert risk.subject == "我"


def test_relation_with_name() -> None:
    risk = assess_attribution("小雨的妈妈是老师")
    assert risk.shifted is True
    assert risk.kind == "relation"
    assert risk.subject == "小雨"


def test_non_relation_is_not_flagged() -> None:
    assert assess_attribution("我的职业是后端开发").shifted is False


def test_known_pet_is_flagged() -> None:
    cfg = MemoryHygieneConfig(known_pets=("豆豆",))
    risk = assess_attribution("豆豆特别能吃", cfg)
    assert risk.shifted is True
    assert risk.kind == "pet"
    assert risk.subject == "豆豆"


def test_pet_without_known_list_is_not_flagged() -> None:
    assert assess_attribution("豆豆特别能吃").shifted is False


def test_plain_fact_is_not_flagged() -> None:
    assert assess_attribution("用户喜欢喝咖啡和茶").shifted is False


def test_attribution_can_be_disabled() -> None:
    cfg = MemoryHygieneConfig(check_attribution=False, known_pets=("豆豆",))
    assert assess_attribution("豆豆特别能吃", cfg).shifted is False
