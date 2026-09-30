import logging
from collections import defaultdict

from app.logging_setup import log_event

logger = logging.getLogger("llm.cost")


class CostTracker:
    """Accumulates token usage and cost per ticket."""

    def __init__(self):
        self.totals = defaultdict(lambda: {"calls": 0, "tokens": 0, "cost_usd": 0.0})

    def add(self, ticket_id: str, usage) -> None:
        total = self.totals[ticket_id]
        total["calls"] += 1
        total["tokens"] += usage.input_tokens + usage.output_tokens
        total["cost_usd"] += usage.cost_usd

    def summarize(self, ticket_id: str) -> dict:
        summary = dict(self.totals[ticket_id])
        log_event(logger, logging.INFO, "ticket_cost_summary", ticket_id=ticket_id, **summary)
        return summary
