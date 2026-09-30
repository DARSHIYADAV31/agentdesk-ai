from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding

from app.agents.knowledge import answer_ticket, parse_answer
from app.rag.store import build_store, load_store

DOCS = [Document(page_content="Restart the VPN client", metadata={"source": "vpn.md"})]


class FakeRetriever:
    def __init__(self, docs):
        self.docs = docs

    def invoke(self, query):
        return self.docs


class FakeRouter:
    def __init__(self, content):
        self.content = content

    def invoke(self, messages, ticket_id="-"):
        return type("R", (), {"content": self.content})(), None


def test_cited_answer_can_resolve():
    text = '{"answer":"Restart it","sources":["vpn.md"],"can_resolve":true}'
    result = parse_answer(text, {"vpn.md"})
    assert result.sources == ["vpn.md"] and result.can_resolve


def test_invented_source_is_dropped_and_blocks_resolution():
    text = '{"answer":"x","sources":["made-up.md"],"can_resolve":true}'
    result = parse_answer(text, {"vpn.md"})
    assert result.sources == [] and not result.can_resolve


def test_no_retrieved_docs_returns_no_source():
    result = answer_ticket(FakeRouter(""), FakeRetriever([]), "t", "b")
    assert not result.can_resolve and result.sources == []


def test_answer_ticket_cites_retrieved_source():
    router = FakeRouter('{"answer":"Restart","sources":["vpn.md"],"can_resolve":true}')
    result = answer_ticket(router, FakeRetriever(DOCS), "VPN down", "cannot connect")
    assert result.sources == ["vpn.md"]


def test_faiss_store_roundtrip(tmp_path):
    embeddings = DeterministicFakeEmbedding(size=32)
    build_store("faiss", embeddings, DOCS, tmp_path)
    found = load_store("faiss", embeddings, tmp_path).as_retriever(k=1).invoke("VPN")
    assert found[0].metadata["source"] == "vpn.md"
