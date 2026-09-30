from sqlalchemy import select

from app.db.audit_model import AuditLog
from app.db.ticket_repo import set_status
from tests.unit.test_api_assign import assign, auth, register, setup

FIX = "Replaced the faulty cable and confirmed the connection with the user."


def resolve(client, ticket_id, headers, text=FIX):
    return client.post(f"/tickets/{ticket_id}/resolve", json={"resolution": text}, headers=headers)


def escalated_and_assigned(client, db):
    alice, sam, ticket_id = setup(client)
    assign(client, ticket_id, "sam", auth(client, "root"))
    set_status(db, ticket_id, "escalated")
    return alice, sam, ticket_id


def test_assignee_can_resolve_and_is_recorded(client, db):
    _, sam, ticket_id = escalated_and_assigned(client, db)
    body = resolve(client, ticket_id, sam).json()
    assert (body["status"], body["resolved_by"], body["resolution"]) == ("resolved", "sam", FIX)


def test_admin_can_resolve_a_needs_human_ticket(client, db):
    _, _, ticket_id = setup(client)
    set_status(db, ticket_id, "needs_human")
    body = resolve(client, ticket_id, auth(client, "root")).json()
    assert (body["status"], body["resolved_by"]) == ("resolved", "root")


def test_requester_and_outsiders_cannot_resolve(client, db):
    alice, _, ticket_id = escalated_and_assigned(client, db)
    assert resolve(client, ticket_id, alice).status_code == 403
    assert resolve(client, ticket_id, register(client, "eve")).status_code == 404


def test_only_human_states_can_be_resolved(client, db):
    _, _, ticket_id = setup(client)
    root = auth(client, "root")
    for status in ("new", "pending_approval", "resolved"):
        set_status(db, ticket_id, status)
        assert resolve(client, ticket_id, root).status_code == 409


def test_resolution_message_is_required(client, db):
    _, sam, ticket_id = escalated_and_assigned(client, db)
    assert resolve(client, ticket_id, sam, "   ").status_code == 422


def test_manual_resolve_is_audited_without_text(client, db):
    _, sam, ticket_id = escalated_and_assigned(client, db)
    resolve(client, ticket_id, sam)
    row = db.scalars(select(AuditLog).where(AuditLog.action == "resolve:manual")).one()
    assert (row.actor, row.status) == ("sam", "succeeded") and "cable" not in row.detail
