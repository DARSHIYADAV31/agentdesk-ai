import logging

from pydantic import ValidationError

from app.agents.parsing import extract_json
from app.agents.prompts import CLASSIFY_SYSTEM
from app.logging_setup import log_event
from app.schemas.classification import Classification

logger = logging.getLogger("agent.classifier")


def build_messages(title: str, body: str) -> list:
    return [("system", CLASSIFY_SYSTEM), ("human", f"Title: {title}\n\n{body}")]


def parse_classification(text: str) -> Classification:
    try:
        return Classification(**extract_json(text))
    except (ValueError, ValidationError):
        return Classification.fallback()


def classify(router, title: str, body: str, ticket_id: str = "-") -> Classification:
    # LLMUnavailableError is deliberately not caught: the pipeline escalates it.
    response, _ = router.invoke(build_messages(title, body), ticket_id)
    result = parse_classification(str(response.content))
    log_event(logger, logging.INFO, "classified", ticket_id=ticket_id,
              category=result.category, priority=result.priority,
              reasoning=result.reasoning)
    return result
