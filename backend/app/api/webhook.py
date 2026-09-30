import hmac

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.api.intake import create_ticket
from app.api.runner import Runner, get_runner
from app.config import get_settings
from app.db.session import get_db
from app.schemas.ticket import TicketCreate

router = APIRouter(prefix="/webhook", tags=["webhook"])


def verify_secret(x_webhook_secret: str = Header(default="")) -> None:
    expected = get_settings().webhook_secret
    # compare_digest avoids leaking the secret through timing; empty secret = disabled.
    if not expected or not hmac.compare_digest(x_webhook_secret, expected):
        raise HTTPException(401, "Invalid webhook secret")


@router.post("/tickets", status_code=202, dependencies=[Depends(verify_secret)])
def intake(payload: TicketCreate, tasks: BackgroundTasks, db: Session = Depends(get_db),
           runner: Runner = Depends(get_runner)):
    ticket = create_ticket(db, payload)
    tasks.add_task(runner.process, ticket.id)
    return {"ticket_id": ticket.id, "status": ticket.status}
