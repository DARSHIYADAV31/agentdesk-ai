"""Load demo tickets without calling any LLM: python -m app.db.seed_demo"""
import json

from sqlalchemy import select

from app.db import models  # noqa: F401
from app.db.action_model import AgentAction
from app.db.approval_model import ApprovalRequest
from app.db.audit_model import AuditLog
from app.db.base import Base
from app.db.seed_data import DOMAIN, TICKETS
from app.db.session import SessionLocal, engine
from app.db.ticket_model import Ticket
from app.db.user_model import User


def add_trail(db, ticket: Ticket, source: str | None) -> None:
    kb = f"sources={[source] if source else []}"
    steps = [("classifier", f"{ticket.category}/{ticket.priority}", "classified"),
             ("knowledge", kb, f"can_resolve={ticket.status == 'resolved'}")]
    for agent, decision, reasoning in steps:
        db.add(AgentAction(ticket_id=ticket.id, agent=agent, decision=decision, reasoning=reasoning))
        db.add(AuditLog(ticket_id=ticket.id, actor="pipeline", action=f"node:{agent}", status="succeeded"))


def add_outcome(db, ticket: Ticket) -> None:
    tool = {"resolved": "update_ticket", "escalated": "escalate",
            "pending_approval": "reset_password"}.get(ticket.status)
    if tool is None:
        return
    db.add(AgentAction(ticket_id=ticket.id, agent="action", decision=tool, reasoning="model tool call"))
    outcome = "blocked" if tool == "reset_password" else "succeeded"
    db.add(AuditLog(ticket_id=ticket.id, actor="action_agent", action=f"tool:{tool}", status=outcome))
    if tool == "reset_password":
        args = json.dumps({"ticket_id": ticket.id, "username": "bob.smith"})
        db.add(ApprovalRequest(ticket_id=ticket.id, tool=tool, args_json=args))


def main() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.scalar(select(Ticket).where(Ticket.requester_email.like(f"%@{DOMAIN}"))):
            print("Demo data already present")
            return
        usernames = set(db.scalars(select(User.username)))
        for i, (title, body, cat, pri, status, res, cost, source, owner) in enumerate(TICKETS):
            ticket = Ticket(title=title, body=body, requester_email=f"user{i}@{DOMAIN}",
                            category=cat, priority=pri, status=status, resolution=res, cost_usd=cost,
                            owner=owner if owner in usernames else None)
            db.add(ticket)
            db.flush()
            if status != "new":
                add_trail(db, ticket, source)
                add_outcome(db, ticket)
        db.commit()
        print(f"Seeded {len(TICKETS)} demo tickets")


if __name__ == "__main__":
    main()
