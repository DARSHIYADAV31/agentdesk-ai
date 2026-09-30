import json

from app.db.approval_model import ApprovalRequest
from app.graph.state import Deps
from app.tools.approval_gate import run_tool
from app.tools.errors import ApprovalRequired


def execute_approved(deps: Deps, approval_id: int) -> None:
    """Run a human-approved destructive action, then close the ticket."""
    request = deps.db.get(ApprovalRequest, approval_id)
    if request is None or request.status != "approved":
        raise ApprovalRequired(approval_id)
    args = json.loads(request.args_json)
    run_tool(deps.db, deps.backend, request.ticket_id, request.tool, args, approval_id)
    note = f"{request.tool} executed after human approval"
    close = {"ticket_id": request.ticket_id, "status": "resolved", "resolution": note}
    run_tool(deps.db, deps.backend, request.ticket_id, "update_ticket", close)
