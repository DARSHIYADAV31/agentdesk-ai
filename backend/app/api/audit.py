from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.audit_model import AuditLog
from app.db.session import get_db
from app.db.ticket_model import Ticket
from app.db.user_model import User
from app.security.deps import current_user

router = APIRouter(prefix="/audit", tags=["audit"])


class AuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int | None
    actor: str
    action: str
    status: str
    detail: str
    created_at: datetime


@router.get("", response_model=list[AuditOut])
def list_audit(ticket_id: int | None = None, limit: int = Query(100, ge=1, le=500),
               db: Session = Depends(get_db), user: User = Depends(current_user)):
    query = select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)
    if user.role != "admin":  # non-admins see the trail of their own or assigned tickets only
        own = select(Ticket.id).where(or_(Ticket.owner == user.username,
                                          Ticket.assignee == user.username))
        query = query.where(AuditLog.ticket_id.in_(own))
    if ticket_id is not None:
        query = query.where(AuditLog.ticket_id == ticket_id)
    return db.scalars(query).all()
