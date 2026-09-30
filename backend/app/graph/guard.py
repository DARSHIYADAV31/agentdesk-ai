import logging

from app.audit.logger import AuditLogger
from app.graph.state import Deps
from app.logging_setup import log_event

logger = logging.getLogger("graph.guard")


def guarded(deps: Deps, name: str, node):
    """Audit each node before it runs and turn any failure into state['error']."""

    def wrapper(state):
        ticket_id = state["ticket_id"]
        audit = AuditLogger(deps.db)
        audit_id = audit.start(ticket_id, "pipeline", f"node:{name}")
        try:
            update = node(state)
        except Exception as exc:
            deps.db.rollback()  # a failed DB call leaves the session unusable
            audit.finish(audit_id, "failed", type(exc).__name__)
            log_event(logger, logging.ERROR, "node_failed", ticket_id=ticket_id,
                      node=name, error=type(exc).__name__)
            return {"error": type(exc).__name__}
        audit.finish(audit_id, "succeeded")
        return update

    return wrapper
