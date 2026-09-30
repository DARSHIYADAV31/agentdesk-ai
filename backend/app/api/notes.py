from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.ticket_access import can_write_notes, get_visible_ticket
from app.audit.logger import AuditLogger
from app.db.note_model import TicketNote
from app.db.session import get_db
from app.db.user_model import User
from app.schemas.notes import NoteCreate, NoteOut
from app.security.deps import current_user

router = APIRouter(tags=["notes"])


@router.post("/tickets/{ticket_id}/notes", response_model=NoteOut, status_code=201)
def add_note(ticket_id: int, body: NoteCreate, db: Session = Depends(get_db),
             user: User = Depends(current_user)):
    ticket = get_visible_ticket(db, ticket_id, user)
    if not can_write_notes(ticket, user):
        raise HTTPException(403, "Only the admin or the assignee can add notes")
    audit = AuditLogger(db)
    # Note text is kept out of the audit trail: it may hold sensitive details.
    audit_id = audit.start(ticket_id, user.username, "note:add", f"{len(body.text)} chars")
    note = TicketNote(ticket_id=ticket_id, author=user.username, text=body.text)
    db.add(note)
    db.commit()
    audit.finish(audit_id, "succeeded")
    return note
