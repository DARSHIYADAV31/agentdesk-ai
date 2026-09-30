from sqlalchemy import select

from app.db.audit_model import AuditLog
from tests.unit.api_helpers import TICKET, auth


def register(client, name):
    tokens = client.post("/auth/register", json={"username": name, "password": f"{name}-pass-1"}).json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def setup(client):
    """alice submits a ticket; sam is a second user; returns headers and the ticket id."""
    alice, sam = register(client, "alice"), register(client, "sam")
    ticket_id = client.post("/tickets", json=TICKET, headers=alice).json()["id"]
    return alice, sam, ticket_id


def assign(client, ticket_id, assignee, headers):
    return client.post(f"/tickets/{ticket_id}/assign", json={"assignee": assignee}, headers=headers)


def test_only_admin_can_assign(client):
    alice, sam, ticket_id = setup(client)
    assert assign(client, ticket_id, "sam", alice).status_code == 403
    assert assign(client, ticket_id, "sam", sam).status_code == 403


def test_admin_assigns_and_assignee_can_then_see_the_ticket(client):
    alice, sam, ticket_id = setup(client)
    assert client.get(f"/tickets/{ticket_id}", headers=sam).status_code == 404
    response = assign(client, ticket_id, "sam", auth(client, "root"))
    assert response.status_code == 200 and response.json()["assignee"] == "sam"
    assert [t["id"] for t in client.get("/tickets", headers=sam).json()] == [ticket_id]


def test_cannot_assign_to_unknown_user_and_can_unassign(client):
    _, sam, ticket_id = setup(client)
    root = auth(client, "root")
    assert assign(client, ticket_id, "ghost", root).status_code == 404
    assign(client, ticket_id, "sam", root)
    assert assign(client, ticket_id, None, root).json()["assignee"] is None
    assert client.get("/tickets", headers=sam).json() == []


def test_assignment_is_audited(client, db):
    _, _, ticket_id = setup(client)
    assign(client, ticket_id, "sam", auth(client, "root"))
    rows = db.scalars(select(AuditLog).where(AuditLog.action == "assign:sam")).all()
    assert [(r.actor, r.status) for r in rows] == [("root", "succeeded")]


def test_users_list_is_admin_only(client):
    assert client.get("/users", headers=register(client, "alice")).status_code == 403
    names = [u["username"] for u in client.get("/users", headers=auth(client, "root")).json()]
    assert "ann" in names and "root" in names
