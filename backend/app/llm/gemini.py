from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import Settings


def build_gemini(settings: Settings) -> ChatGoogleGenerativeAI:
    # max_retries=0: our own retry layer owns all retry behaviour.
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
        timeout=settings.llm_timeout_seconds,
        max_retries=0,
    )
