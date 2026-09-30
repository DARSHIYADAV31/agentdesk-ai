import logging

from app.db.ticket_model import Ticket
from app.db.ticket_repo import set_status
from app.graph.builder import build_graph
from app.graph.state import Deps
from app.logging_setup import log_event

logger = logging.getLogger("pipeline")


def process_ticket(deps: Deps, ticket_id: int) -> dict:
    ticket = deps.db.get(Ticket, ticket_id)
    state = {"ticket_id": ticket_id, "title": ticket.title, "body": ticket.body}
    try:
        result = build_graph(deps).invoke(state)
    except Exception as exc:  # last resort: a ticket must never be left half-processed
        deps.db.rollback()
        set_status(deps.db, ticket_id, "needs_human")
        log_event(logger, logging.ERROR, "pipeline_crashed", ticket_id=ticket_id,
                  error=type(exc).__name__)
        return {"ticket_id": ticket_id, "outcome": "needs_human", "error": type(exc).__name__}
    log_event(logger, logging.INFO, "pipeline_done", ticket_id=ticket_id,
              outcome=result.get("outcome"))
    return result
