from tests.unit.api_helpers import TICKET, auth


def register(client, name):
    tokens = client.post("/auth/register", json={"username": name, "password": f"{name}-pass-1"}).json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def submit(client, headers):
    return client.post("/tickets", json=TICKET, headers=headers).json()["id"]


def test_user_sees_only_own_tickets(client):
    alice, bob = register(client, "alice"), register(client, "bobby")
    alice_ticket = submit(client, alice)
    assert [t["id"] for t in client.get("/tickets", headers=alice).json()] == [alice_ticket]
    assert client.get("/tickets", headers=bob).json() == []


def test_other_users_ticket_detail_is_404(client):
    alice, bob = register(client, "alice"), register(client, "bobby")
    ticket_id = submit(client, alice)
    assert client.get(f"/tickets/{ticket_id}", headers=alice).status_code == 200
    assert client.get(f"/tickets/{ticket_id}", headers=bob).status_code == 404


def test_admin_sees_everyone_and_owner_is_recorded(client):
    alice = register(client, "alice")
    submit(client, alice)
    tickets = client.get("/tickets", headers=auth(client, "root")).json()
    assert "alice" in [t["owner"] for t in tickets]
    assert len(tickets) >= 2  # alice's plus the fixture ticket with no owner


def test_system_and_webhook_tickets_are_admin_only(client):
    client.post("/webhook/tickets", json=TICKET, headers={"X-Webhook-Secret": "hook-secret"})
    alice = register(client, "alice")
    assert client.get("/tickets", headers=alice).json() == []
    assert len(client.get("/tickets", headers=auth(client, "root")).json()) >= 2


def test_audit_trail_is_scoped_to_own_tickets(client, db):
    from app.audit.logger import AuditLogger
    alice, bob = register(client, "alice"), register(client, "bobby")
    ticket_id = submit(client, alice)
    AuditLogger(db).start(ticket_id, "pipeline", "node:classify")
    assert len(client.get("/audit", headers=alice).json()) == 1
    assert client.get("/audit", headers=bob).json() == []
    assert len(client.get("/audit", headers=auth(client, "root")).json()) >= 1


def test_non_admin_cannot_list_approvals(client):
    assert client.get("/approvals", headers=register(client, "alice")).status_code == 403
    assert client.get("/approvals", headers=auth(client, "root")).status_code == 200


def test_me_returns_username_and_role(client):
    assert client.get("/auth/me", headers=auth(client, "root")).json() == {"username": "root", "role": "admin"}
    assert client.get("/auth/me", headers=register(client, "alice")).json()["role"] == "agent"
