import json
from types import SimpleNamespace

from langchain_core.documents import Document

from app.graph.state import Deps
from app.llm.router import LLMRouter
from app.tools.local_backend import LocalBackend

CLASSIFY = json.dumps({"category": "network", "priority": "high", "reasoning": "vpn"})
KB = json.dumps({"answer": "Restart", "sources": ["vpn.md"], "can_resolve": True})


def reply(content="", tool=None):
    calls = [{"name": tool[0], "args": tool[1], "id": "1"}] if tool else []
    usage = {"input_tokens": 10, "output_tokens": 5}
    return SimpleNamespace(content=content, tool_calls=calls, usage_metadata=usage)


class ScriptedModel:
    def __init__(self, replies):
        self.replies = list(replies)

    def bind_tools(self, tools):
        return self

    def invoke(self, messages):
        if not self.replies:
            raise RuntimeError("model down")
        return self.replies.pop(0)


class Retriever:
    def invoke(self, query):
        return [Document(page_content="Restart the VPN", metadata={"source": "vpn.md"})]


def make_deps(db, gemini_replies, mistral_replies=()):
    router = LLMRouter(ScriptedModel(gemini_replies), ScriptedModel(mistral_replies),
                       attempts=1, base_wait=0)
    return Deps(router, Retriever(), db, LocalBackend(db))
