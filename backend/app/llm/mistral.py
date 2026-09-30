from langchain_mistralai import ChatMistralAI

from app.config import Settings


def build_mistral(settings: Settings) -> ChatMistralAI:
    return ChatMistralAI(
        model=settings.mistral_model,
        api_key=settings.mistral_api_key,
        timeout=settings.llm_timeout_seconds,
        max_retries=1,
    )
