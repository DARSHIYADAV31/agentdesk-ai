from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.intake import create_ticket
from app.api.runner import Runner, get_runner
from app.api.ticket_access import can_write_notes, get_visible_ticket, scope_query
from app.db.action_model import AgentAction
from app.db.note_model import TicketNote
from app.db.session import get_db
from app.db.ticket_model import Ticket
from app.db.user_model import User
from app.schemas.notes import TicketDetail
from app.schemas.ticket import TicketCreate, TicketOut
from app.security.deps import current_user

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketOut, status_code=202)
def submit(payload: TicketCreate, tasks: BackgroundTasks, db: Session = Depends(get_db),
           user: User = Depends(current_user), runner: Runner = Depends(get_runner)):
    ticket = create_ticket(db, payload, owner=user.username)
    tasks.add_task(runner.process, ticket.id)
    return ticket


@router.get("", response_model=list[TicketOut])
def list_tickets(status: str | None = None, limit: int = Query(50, ge=1, le=200),
                 db: Session = Depends(get_db), user: User = Depends(current_user)):
    query = scope_query(select(Ticket).order_by(Ticket.id.desc()).limit(limit), user)
    if status:
        query = query.where(Ticket.status == status)
    return db.scalars(query).all()


@router.get("/{ticket_id}", response_model=TicketDetail)
def ticket_detail(ticket_id: int, db: Session = Depends(get_db),
                  user: User = Depends(current_user)):
    ticket = get_visible_ticket(db, ticket_id, user)
    actions = db.scalars(select(AgentAction).where(AgentAction.ticket_id == ticket_id)
                         .order_by(AgentAction.id)).all()
    notes = []
    if can_write_notes(ticket, user):  # internal notes are hidden from the requester
        notes = db.scalars(select(TicketNote).where(TicketNote.ticket_id == ticket_id)
                           .order_by(TicketNote.id)).all()
    return TicketDetail(**TicketOut.model_validate(ticket).model_dump(),
                        actions=actions, notes=notes)
