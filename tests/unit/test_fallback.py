import pytest

from app.llm.errors import LLMUnavailableError
from app.llm.router import LLMRouter


class FakeModel:
    def __init__(self, fail=False):
        self.fail = fail
        self.calls = 0

    def invoke(self, messages):
        self.calls += 1
        if self.fail:
            raise RuntimeError("boom")
        return type("Resp", (), {"content": "ok", "usage_metadata": {}})()


def make_router(gemini, mistral):
    return LLMRouter(gemini, mistral, attempts=3, base_wait=0)


def test_gemini_success_never_calls_mistral():
    gemini, mistral = FakeModel(), FakeModel()
    make_router(gemini, mistral).invoke(["hi"])
    assert mistral.calls == 0


def test_gemini_failure_falls_back_to_mistral_after_3_attempts():
    gemini, mistral = FakeModel(fail=True), FakeModel()
    response, usage = make_router(gemini, mistral).invoke(["hi"])
    assert gemini.calls == 3
    assert usage.provider == "mistral"


def test_both_failing_raises_unavailable():
    router = make_router(FakeModel(fail=True), FakeModel(fail=True))
    with pytest.raises(LLMUnavailableError):
        router.invoke(["hi"])
