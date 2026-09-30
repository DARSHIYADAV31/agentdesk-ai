from sqlalchemy.orm import Session

from app.db.ticket_model import Ticket


def _get_ticket(db: Session, ticket_id: int) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise ValueError("ticket not found")
    return ticket


def lookup_ticket(db: Session, ticket_id: int) -> dict:
    ticket = _get_ticket(db, ticket_id)
    return {"id": ticket.id, "status": ticket.status, "category": ticket.category,
            "priority": ticket.priority}


def update_ticket(db: Session, ticket_id: int, status: str, resolution: str = "") -> dict:
    ticket = _get_ticket(db, ticket_id)
    ticket.status, ticket.resolution = status, resolution
    db.commit()
    return {"id": ticket_id, "status": status}


def escalate(db: Session, ticket_id: int, reason: str) -> dict:
    return update_ticket(db, ticket_id, "escalated", reason)


def reset_password(db: Session, ticket_id: int, username: str) -> dict:
    # Simulated: a real deployment would call the identity provider here.
    return {"ticket_id": ticket_id, "result": "password reset issued"}


def delete_account(db: Session, ticket_id: int, username: str) -> dict:
    return {"ticket_id": ticket_id, "result": "account deleted"}
