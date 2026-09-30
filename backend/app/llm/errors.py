class LLMUnavailableError(Exception):
    """Raised when both the primary and fallback models fail."""
