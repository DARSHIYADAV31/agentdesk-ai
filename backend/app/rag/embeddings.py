from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import Settings


def build_embeddings(settings: Settings) -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=settings.gemini_api_key,
    )
