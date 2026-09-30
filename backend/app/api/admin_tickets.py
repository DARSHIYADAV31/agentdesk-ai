from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.intake import create_ticket
from app.api.runner import Runner, get_runner
from app.audit.logger import AuditLogger
from app.db.session import get_db
from app.db.ticket_repo import set_status
from app.db.user_model import User
from app.schemas.admin_ticket import AdminTicketCreate
from app.schemas.ticket import TicketOut
from app.security.deps import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


def require_user(db: Session, username: str | None) -> None:
    if username and db.scalar(select(User).where(User.username == username)) is None:
        raise HTTPException(404, f"User '{username}' not found")


@router.post("/tickets", response_model=TicketOut, status_code=201)
def create_for_user(payload: AdminTicketCreate, tasks: BackgroundTasks,
                    db: Session = Depends(get_db), admin: User = Depends(require_admin),
                    runner: Runner = Depends(get_runner)):
    require_user(db, payload.owner)
    require_user(db, payload.assignee)
    ticket = create_ticket(db, payload, owner=payload.owner or admin.username)
    audit = AuditLogger(db)
    detail = f"owner={ticket.owner} assignee={payload.assignee} skip_ai={payload.skip_ai}"
    audit_id = audit.start(ticket.id, admin.username, "admin:create_ticket", detail)
    ticket.assignee = payload.assignee
    db.commit()
    if payload.skip_ai:
        set_status(db, ticket.id, "escalated")  # waits for the human, so they can resolve it
    else:
        tasks.add_task(runner.process, ticket.id)
    audit.finish(audit_id, "succeeded")
    return ticket
