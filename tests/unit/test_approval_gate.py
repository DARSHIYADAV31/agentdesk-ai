import pytest
from sqlalchemy import select

from app.db.audit_model import AuditLog
from app.tools.approval_gate import run_tool
from app.tools.approvals import decide
from app.tools.errors import ApprovalRequired

ARGS = {"username": "bob"}


class SpyBackend:
    def __init__(self, db):
        self.db, self.calls, self.audit_at_call = db, [], []

    def call(self, name, args):
        self.calls.append(name)
        self.audit_at_call.append([r.status for r in self.db.scalars(select(AuditLog))])
        return "done"


def request_approval(db, backend, tool="reset_password"):
    with pytest.raises(ApprovalRequired) as pending:
        run_tool(db, backend, 1, tool, ARGS)
    return pending.value.approval_id


def test_destructive_without_approval_never_executes(db):
    backend = SpyBackend(db)
    request_approval(db, backend)
    assert backend.calls == []


def test_rejected_approval_does_not_execute(db):
    backend = SpyBackend(db)
    approval_id = request_approval(db, backend, "delete_account")
    decide(db, approval_id, False, "admin")
    with pytest.raises(ApprovalRequired):
        run_tool(db, backend, 1, "delete_account", ARGS, approval_id)
    assert backend.calls == []


def test_approved_request_executes_once_only(db):
    backend = SpyBackend(db)
    approval_id = request_approval(db, backend)
    decide(db, approval_id, True, "admin")
    assert run_tool(db, backend, 1, "reset_password", ARGS, approval_id) == "done"
    with pytest.raises(ApprovalRequired):
        run_tool(db, backend, 1, "reset_password", ARGS, approval_id)


def test_approval_for_other_arguments_is_rejected(db):
    backend = SpyBackend(db)
    approval_id = request_approval(db, backend)
    decide(db, approval_id, True, "admin")
    with pytest.raises(ApprovalRequired):
        run_tool(db, backend, 1, "reset_password", {"username": "eve"}, approval_id)


def test_audit_row_exists_before_tool_executes(db):
    backend = SpyBackend(db)
    run_tool(db, backend, 1, "lookup_ticket", {"ticket_id": 1})
    assert backend.audit_at_call[0] == ["started"]
