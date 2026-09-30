from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.runner import Runner, get_runner
from app.audit.logger import AuditLogger
from app.db.approval_model import ApprovalRequest
from app.db.session import get_db
from app.db.ticket_repo import set_status
from app.db.user_model import User
from app.schemas.approval import ApprovalOut, Decision
from app.security.deps import require_admin
from app.tools.approvals import decide

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("", response_model=list[ApprovalOut], dependencies=[Depends(require_admin)])
def list_approvals(status: str | None = "pending", db: Session = Depends(get_db)):
    query = select(ApprovalRequest).order_by(ApprovalRequest.id.desc())
    if status:
        query = query.where(ApprovalRequest.status == status)
    return db.scalars(query).all()


@router.post("/{approval_id}/decision", response_model=ApprovalOut)
def decide_approval(approval_id: int, body: Decision, tasks: BackgroundTasks,
                    db: Session = Depends(get_db), user: User = Depends(require_admin),
                    runner: Runner = Depends(get_runner)):
    request = db.get(ApprovalRequest, approval_id)
    if request is None:
        raise HTTPException(404, "Approval request not found")
    audit = AuditLogger(db)
    label = "approve" if body.approve else "reject"
    audit_id = audit.start(request.ticket_id, user.username, f"approval:{label}:{request.tool}")
    try:
        request = decide(db, approval_id, body.approve, user.username)
    except ValueError:
        audit.finish(audit_id, "failed", "not pending")
        raise HTTPException(409, "Approval request is not pending")
    audit.finish(audit_id, "succeeded")
    if body.approve:
        tasks.add_task(runner.execute_approval, approval_id, request.ticket_id)
    else:
        set_status(db, request.ticket_id, "escalated")
    return request
