import logging

from app.llm.cost_tracker import CostTracker
from app.llm.errors import LLMUnavailableError
from app.llm.retry import call_with_retry
from app.llm.usage import build_usage, log_usage
from app.logging_setup import log_event

logger = logging.getLogger("llm.router")


class LLMRouter:
    """Gemini first; Mistral only after Gemini exhausts its retries."""

    def __init__(self, primary, fallback, attempts: int = 3, base_wait: float = 1.0):
        self.models = [("gemini", primary), ("mistral", fallback)]
        self.attempts = attempts
        self.base_wait = base_wait
        self.tracker = CostTracker()

    def invoke(self, messages, ticket_id: str = "-", tools=None):
        for provider, model in self.models:
            try:
                response = self._call(model, messages, tools)
            except Exception as exc:
                log_event(logger, logging.WARNING, "llm_failed", ticket_id=ticket_id,
                          provider=provider, error=type(exc).__name__)
                continue
            usage = build_usage(provider, response)
            log_usage(usage, ticket_id)
            self.tracker.add(ticket_id, usage)
            return response, usage
        raise LLMUnavailableError("Both Gemini and Mistral failed")

    def _call(self, model, messages, tools):
        bound = model.bind_tools(tools) if tools else model
        return call_with_retry(lambda: bound.invoke(messages), self.attempts, self.base_wait)
