import logging

from pydantic import ValidationError

from app.agents.parsing import extract_json
from app.agents.prompts import KB_SYSTEM
from app.logging_setup import log_event
from app.schemas.kb_answer import KBAnswer

logger = logging.getLogger("agent.knowledge")


def format_context(docs) -> str:
    return "\n\n".join(f"[{d.metadata['source']}]\n{d.page_content}" for d in docs)


def parse_answer(text: str, allowed: set[str]) -> KBAnswer:
    try:
        result = KBAnswer(**extract_json(text))
    except (ValueError, ValidationError):
        return KBAnswer.no_source()
    # Drop citations the model invented; an uncited answer cannot auto-resolve.
    result.sources = [s for s in result.sources if s in allowed]
    result.can_resolve = result.can_resolve and bool(result.sources)
    return result


def answer_ticket(router, retriever, title: str, body: str, ticket_id: str = "-") -> KBAnswer:
    docs = retriever.invoke(f"{title}\n{body}")
    if not docs:
        return KBAnswer.no_source()
    messages = [("system", KB_SYSTEM),
                ("human", f"Context:\n{format_context(docs)}\n\nTicket: {title}\n{body}")]
    response, _ = router.invoke(messages, ticket_id)
    result = parse_answer(str(response.content), {d.metadata["source"] for d in docs})
    log_event(logger, logging.INFO, "kb_answer", ticket_id=ticket_id,
              sources=result.sources, can_resolve=result.can_resolve)
    return result
