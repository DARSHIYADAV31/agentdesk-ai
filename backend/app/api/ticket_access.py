from fastapi import HTTPException
from sqlalchemy import or_

from app.db.ticket_model import Ticket
from app.db.user_model import User


def scope_query(query, user: User):
    """Admins see every ticket; others see tickets they submitted or are assigned to."""
    if user.role == "admin":
        return query
    return query.where(or_(Ticket.owner == user.username, Ticket.assignee == user.username))


def can_view(ticket: Ticket, user: User) -> bool:
    return user.role == "admin" or user.username in (ticket.owner, ticket.assignee)


def can_write_notes(ticket: Ticket, user: User) -> bool:
    """Notes are internal: only the admin and the assignee, never the requester."""
    return user.role == "admin" or ticket.assignee == user.username


def get_visible_ticket(db, ticket_id: int, user: User) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    # 404 (not 403) so users cannot probe which ticket ids exist.
    if ticket is None or not can_view(ticket, user):
        raise HTTPException(404, "Ticket not found")
    return ticket
