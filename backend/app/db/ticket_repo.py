from sqlalchemy.orm import Session

from app.db.action_model import AgentAction
from app.db.ticket_model import Ticket


def set_status(db: Session, ticket_id: int, status: str) -> None:
    db.get(Ticket, ticket_id).status = status
    db.commit()


def save_classification(db: Session, ticket_id: int, category: str, priority: str) -> None:
    ticket = db.get(Ticket, ticket_id)
    ticket.category, ticket.priority = category, priority
    db.commit()


def save_cost(db: Session, ticket_id: int, cost_usd: float) -> None:
    db.get(Ticket, ticket_id).cost_usd = cost_usd
    db.commit()


def record_action(db: Session, ticket_id: int, agent: str, decision: str, reasoning: str) -> None:
    db.add(AgentAction(ticket_id=ticket_id, agent=agent, decision=decision, reasoning=reasoning))
    db.commit()
