from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.logger import AuditLogger
from app.db.session import get_db
from app.db.ticket_model import Ticket
from app.db.user_model import User
from app.schemas.notes import AssignRequest
from app.schemas.ticket import TicketOut
from app.security.deps import require_admin

router = APIRouter(tags=["assignment"])


@router.post("/tickets/{ticket_id}/assign", response_model=TicketOut)
def assign(ticket_id: int, body: AssignRequest, db: Session = Depends(get_db),
           admin: User = Depends(require_admin)):
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(404, "Ticket not found")
    if body.assignee and db.scalar(select(User).where(User.username == body.assignee)) is None:
        raise HTTPException(404, "User not found")
    audit = AuditLogger(db)
    audit_id = audit.start(ticket_id, admin.username, f"assign:{body.assignee or 'nobody'}")
    ticket.assignee = body.assignee
    db.commit()
    audit.finish(audit_id, "succeeded")
    return ticket


@router.get("/users")
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    users = db.scalars(select(User).order_by(User.username)).all()
    return [{"username": u.username, "role": u.role} for u in users]
