import os
from pathlib import Path

from app.config import get_settings
from app.rag.embeddings import build_embeddings
from app.rag.loader import load_documents
from app.rag.store import build_store

KB_DIR = Path(__file__).resolve().parents[2] / "knowledge_base"


def main() -> None:
    settings = get_settings()
    kind = os.getenv("VECTOR_STORE", "faiss")
    docs = load_documents(KB_DIR)
    build_store(kind, build_embeddings(settings), docs)
    print(f"Indexed {len(docs)} chunks into {kind}")


if __name__ == "__main__":
    main()
