import logging
from dataclasses import dataclass

from app.logging_setup import log_event

logger = logging.getLogger("llm.usage")

# USD per 1M tokens (input, output); approximate, update when pricing changes.
PRICES = {"gemini": (0.30, 2.50), "mistral": (0.20, 0.60)}


@dataclass
class UsageRecord:
    provider: str
    input_tokens: int
    output_tokens: int
    cost_usd: float


def build_usage(provider: str, response) -> UsageRecord:
    meta = getattr(response, "usage_metadata", None) or {}
    tokens_in = meta.get("input_tokens", 0)
    tokens_out = meta.get("output_tokens", 0)
    price_in, price_out = PRICES[provider]
    cost = (tokens_in * price_in + tokens_out * price_out) / 1_000_000
    return UsageRecord(provider, tokens_in, tokens_out, cost)


def log_usage(usage: UsageRecord, ticket_id: str) -> None:
    log_event(
        logger, logging.INFO, "llm_call",
        ticket_id=ticket_id, provider=usage.provider,
        input_tokens=usage.input_tokens, output_tokens=usage.output_tokens,
        cost_usd=round(usage.cost_usd, 6),
    )
