from app.agents.classifier import classify, parse_classification


class FakeRouter:
    def __init__(self, content):
        self.content = content

    def invoke(self, messages, ticket_id="-"):
        return type("R", (), {"content": self.content})(), None


def test_valid_json_is_parsed():
    result = parse_classification('{"category":"network","priority":"high","reasoning":"wifi"}')
    assert (result.category, result.priority) == ("network", "high")


def test_code_fenced_json_is_parsed():
    text = '```json\n{"category":"billing","priority":"low","reasoning":"x"}\n```'
    assert parse_classification(text).category == "billing"


def test_unknown_category_falls_back_to_other():
    result = parse_classification('{"category":"weather","priority":"high"}')
    assert (result.category, result.priority) == ("other", "medium")


def test_garbage_output_falls_back():
    assert parse_classification("I cannot help").category == "other"


def test_classify_uses_router_output():
    router = FakeRouter('{"category":"access","priority":"critical","reasoning":"locked"}')
    assert classify(router, "Locked out", "cannot log in").priority == "critical"
