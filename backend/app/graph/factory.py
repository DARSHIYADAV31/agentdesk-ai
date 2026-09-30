from app.config import get_settings
from app.graph.state import Deps
from app.llm.gemini import build_gemini
from app.llm.mistral import build_mistral
from app.llm.router import LLMRouter
from app.rag.embeddings import build_embeddings
from app.rag.store import load_store
from app.tools.composite_backend import CompositeBackend
from app.tools.local_backend import LocalBackend
from app.tools.mcp_backend import McpBackend


def build_deps(db, vector_store: str = "faiss") -> Deps:
    settings = get_settings()
    router = LLMRouter(build_gemini(settings), build_mistral(settings),
                       attempts=settings.llm_max_attempts)
    retriever = load_store(vector_store, build_embeddings(settings)).as_retriever(
        search_kwargs={"k": 3})
    backend = CompositeBackend(McpBackend(settings.mcp_timeout_seconds), LocalBackend(db))
    return Deps(router, retriever, db, backend)
