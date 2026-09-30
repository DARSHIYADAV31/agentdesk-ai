import logging

from app.db.session import SessionLocal
from app.db.ticket_repo import set_status
from app.graph.factory import build_deps
from app.graph.pipeline import process_ticket
from app.graph.resume import execute_approved
from app.logging_setup import log_event

logger = logging.getLogger("api.runner")


class Runner:
    """Background jobs; each opens its own DB session because requests have ended."""

    def process(self, ticket_id: int) -> None:
        with SessionLocal() as db:
            process_ticket(build_deps(db), ticket_id)

    def execute_approval(self, approval_id: int, ticket_id: int) -> None:
        with SessionLocal() as db:
            try:
                execute_approved(build_deps(db), approval_id)
            except Exception as exc:
                db.rollback()
                set_status(db, ticket_id, "needs_human")
                log_event(logger, logging.ERROR, "approved_action_failed",
                          ticket_id=ticket_id, error=type(exc).__name__)


def get_runner() -> Runner:
    return Runner()
