from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.ticket_access import can_write_notes, get_visible_ticket
from app.audit.logger import AuditLogger
from app.db.session import get_db
from app.db.user_model import User
from app.schemas.notes import ResolveRequest
from app.schemas.ticket import TicketOut
from app.security.deps import current_user

router = APIRouter(tags=["resolve"])

# Only tickets already waiting for a human: "new" is still being processed by the AI,
# and "pending_approval" has an open approval request that could still be executed.
HUMAN_STATES = {"escalated", "needs_human"}


@router.post("/tickets/{ticket_id}/resolve", response_model=TicketOut)
def resolve(ticket_id: int, body: ResolveRequest, db: Session = Depends(get_db),
            user: User = Depends(current_user)):
    ticket = get_visible_ticket(db, ticket_id, user)
    if not can_write_notes(ticket, user):
        raise HTTPException(403, "Only the admin or the assignee can resolve a ticket")
    if ticket.status not in HUMAN_STATES:
        raise HTTPException(409, f"A ticket that is '{ticket.status}' cannot be resolved manually")
    audit = AuditLogger(db)
    audit_id = audit.start(ticket_id, user.username, "resolve:manual", f"{len(body.resolution)} chars")
    ticket.status, ticket.resolution, ticket.resolved_by = "resolved", body.resolution, user.username
    db.commit()
    audit.finish(audit_id, "succeeded")
    return ticket
