from sqlalchemy.orm import Session

from app.db.ticket_model import Ticket
from app.schemas.ticket import TicketCreate


def create_ticket(db: Session, payload: TicketCreate, owner: str | None = None) -> Ticket:
    ticket = Ticket(title=payload.title, body=payload.body,
                    requester_email=str(payload.requester_email), owner=owner)
    db.add(ticket)
    db.commit()
    return ticket
