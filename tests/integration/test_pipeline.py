from sqlalchemy import select

from app.db.approval_model import ApprovalRequest
from app.db.audit_model import AuditLog
from app.db.ticket_model import Ticket
from app.graph.pipeline import process_ticket
from app.graph.resume import execute_approved
from app.tools.approvals import decide
from tests.integration.fakes import CLASSIFY, KB, make_deps, reply

RESOLVE = ("update_ticket", {"ticket_id": 1, "status": "resolved"})


def test_simple_ticket_is_auto_resolved(db):
    deps = make_deps(db, [reply(CLASSIFY), reply(KB), reply(tool=RESOLVE)])
    result = process_ticket(deps, 1)
    ticket = db.get(Ticket, 1)
    assert result["outcome"] == "resolved" and ticket.status == "resolved"
    assert ticket.category == "network" and ticket.cost_usd > 0
    statuses = [row.status for row in db.scalars(select(AuditLog))]
    assert "started" not in statuses  # every started row was closed out


def test_destructive_action_waits_for_approval_then_runs(db):
    reset = reply(tool=("reset_password", {"ticket_id": 1, "username": "bob"}))
    deps = make_deps(db, [reply(CLASSIFY), reply(KB), reset])
    approval_id = process_ticket(deps, 1)["approval_id"]
    assert db.get(Ticket, 1).status == "pending_approval"
    decide(db, approval_id, True, "admin")
    execute_approved(deps, approval_id)
    assert db.get(Ticket, 1).status == "resolved"
    assert db.get(ApprovalRequest, approval_id).status == "used"


def test_model_outage_marks_ticket_needs_human(db):
    result = process_ticket(make_deps(db, []), 1)
    assert result["outcome"] == "needs_human"
    assert db.get(Ticket, 1).status == "needs_human"


def test_gemini_failure_uses_mistral_end_to_end(db):
    deps = make_deps(db, [], [reply(CLASSIFY), reply(KB), reply(tool=RESOLVE)])
    assert process_ticket(deps, 1)["outcome"] == "resolved"
