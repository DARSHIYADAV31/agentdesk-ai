import logging

from sqlalchemy.orm import Session

from app.db.audit_model import AuditLog
from app.logging_setup import log_event

logger = logging.getLogger("audit")


class AuditLogger:
    """Writes the audit row BEFORE an action runs, then updates its outcome."""

    def __init__(self, db: Session):
        self.db = db

    def start(self, ticket_id, actor: str, action: str, detail: str = "") -> int:
        row = AuditLog(ticket_id=ticket_id, actor=actor, action=action,
                       status="started", detail=detail)
        self.db.add(row)
        self.db.commit()
        log_event(logger, logging.INFO, "audit_started", ticket_id=ticket_id, action=action)
        return row.id

    def finish(self, audit_id: int, status: str, detail: str = "") -> None:
        row = self.db.get(AuditLog, audit_id)
        row.status = status
        row.detail = detail or row.detail
        self.db.commit()
        log_event(logger, logging.INFO, "audit_finished", audit_id=audit_id, status=status)
