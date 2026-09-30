from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.vectorstores import FAISS

INDEX_DIR = Path("vector_index")


def build_store(kind: str, embeddings, docs, index_dir: Path = INDEX_DIR):
    if kind == "chroma":
        return Chroma.from_documents(docs, embeddings, persist_directory=str(index_dir / "chroma"))
    store = FAISS.from_documents(docs, embeddings)
    store.save_local(str(index_dir / "faiss"))
    return store


def load_store(kind: str, embeddings, index_dir: Path = INDEX_DIR):
    if kind == "chroma":
        return Chroma(embedding_function=embeddings, persist_directory=str(index_dir / "chroma"))
    # Index is written by our own ingest step, so deserialization is safe.
    return FAISS.load_local(str(index_dir / "faiss"), embeddings,
                            allow_dangerous_deserialization=True)
