from sqlalchemy import select

from app.db.audit_model import AuditLog
from tests.unit.api_helpers import TICKET, auth
from tests.unit.test_api_assign import register
from tests.unit.test_api_resolve import resolve


def create(client, headers, **extra):
    return client.post("/admin/tickets", json={**TICKET, **extra}, headers=headers)


def users(client):
    return register(client, "alice"), register(client, "sam")


def test_only_admin_can_use_the_admin_form(client):
    alice, _ = users(client)
    assert create(client, alice).status_code == 403


def test_ticket_for_employee_assigned_and_sent_straight_to_human(client, runner):
    alice, sam = users(client)
    response = create(client, auth(client, "root"), owner="alice", assignee="sam", skip_ai=True)
    body = response.json()
    assert response.status_code == 201
    assert (body["owner"], body["assignee"], body["status"]) == ("alice", "sam", "escalated")
    assert runner.processed == []  # the AI never ran
    assert [t["id"] for t in client.get("/tickets", headers=alice).json()] == [body["id"]]
    assert [t["id"] for t in client.get("/tickets", headers=sam).json()] == [body["id"]]
    assert resolve(client, body["id"], sam).status_code == 200  # assignee can close it


def test_without_skip_the_ai_still_processes_it(client, runner):
    users(client)
    body = create(client, auth(client, "root"), owner="alice", assignee="sam").json()
    assert runner.processed == [body["id"]] and body["status"] == "new"


def test_owner_defaults_to_the_admin(client):
    assert create(client, auth(client, "root")).json()["owner"] == "root"


def test_unknown_users_and_skip_without_assignee_are_rejected(client):
    users(client)
    root = auth(client, "root")
    assert create(client, root, owner="ghost").status_code == 404
    assert create(client, root, assignee="ghost").status_code == 404
    assert create(client, root, skip_ai=True).status_code == 422


def test_admin_creation_is_audited(client, db):
    users(client)
    create(client, auth(client, "root"), owner="alice", assignee="sam")
    row = db.scalars(select(AuditLog).where(AuditLog.action == "admin:create_ticket")).one()
    assert (row.actor, row.status) == ("root", "succeeded")
