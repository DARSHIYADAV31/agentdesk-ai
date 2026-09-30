import json

from sqlalchemy.orm import Session

from app.db.approval_model import ApprovalRequest
from app.tools.errors import ApprovalRequired


def create_request(db: Session, ticket_id: int, tool: str, args: dict) -> ApprovalRequest:
    request = ApprovalRequest(ticket_id=ticket_id, tool=tool, args_json=json.dumps(args))
    db.add(request)
    db.commit()
    return request


def decide(db: Session, approval_id: int, approve: bool, user: str) -> ApprovalRequest:
    request = db.get(ApprovalRequest, approval_id)
    if request is None or request.status != "pending":
        raise ValueError("approval request is not pending")
    request.status = "approved" if approve else "rejected"
    request.decided_by = user
    db.commit()
    return request


def consume(db: Session, ticket_id: int, tool: str, args: dict, approval_id) -> None:
    """Allow a destructive call only with a matching, approved, unused request."""
    if approval_id is None:
        raise ApprovalRequired(create_request(db, ticket_id, tool, args).id)
    request = db.get(ApprovalRequest, approval_id)
    matches = request and (request.ticket_id, request.tool) == (ticket_id, tool)
    if not matches or request.status != "approved" or json.loads(request.args_json) != args:
        raise ApprovalRequired(approval_id)
    request.status = "used"  # single use
    db.commit()
