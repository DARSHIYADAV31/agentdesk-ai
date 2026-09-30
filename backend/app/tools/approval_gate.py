import logging

from sqlalchemy.orm import Session

from app.audit.logger import AuditLogger
from app.logging_setup import log_event
from app.tools.approvals import consume
from app.tools.errors import ApprovalRequired, ToolExecutionError
from app.tools.registry import get_spec

logger = logging.getLogger("tools.gate")


def run_tool(db: Session, backend, ticket_id: int, name: str, args: dict, approval_id=None):
    spec = get_spec(name)
    audit = AuditLogger(db)
    # Argument names only: values may hold user data.
    audit_id = audit.start(ticket_id, "action_agent", f"tool:{name}", f"args={sorted(args)}")
    try:
        if spec.destructive:
            consume(db, ticket_id, name, args, approval_id)
        result = backend.call(name, args)
    except ApprovalRequired:
        audit.finish(audit_id, "blocked", "awaiting human approval")
        log_event(logger, logging.WARNING, "tool_blocked", ticket_id=ticket_id, tool=name)
        raise
    except Exception as exc:
        audit.finish(audit_id, "failed", type(exc).__name__)
        log_event(logger, logging.ERROR, "tool_failed", ticket_id=ticket_id, tool=name)
        raise ToolExecutionError(f"{name} failed") from exc
    audit.finish(audit_id, "succeeded")
    log_event(logger, logging.INFO, "tool_succeeded", ticket_id=ticket_id, tool=name)
    return result
