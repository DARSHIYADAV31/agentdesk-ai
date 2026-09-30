from app.tools.approvals import create_request
from tests.unit.api_helpers import auth


def decision(client, request_id, approve, user):
    return client.post(f"/approvals/{request_id}/decision", json={"approve": approve},
                       headers=auth(client, user))


def test_only_admin_can_decide_approvals(client):
    assert decision(client, 1, True, "ann").status_code == 403


def test_admin_rejection_escalates_ticket(client, db):
    request = create_request(db, 1, "reset_password", {"username": "bob"})
    assert decision(client, request.id, False, "root").json()["status"] == "rejected"
    assert client.get("/tickets/1", headers=auth(client, "root")).json()["status"] == "escalated"


def test_admin_approval_schedules_execution(client, db, runner):
    request = create_request(db, 1, "reset_password", {"username": "bob"})
    decision(client, request.id, True, "root")
    assert runner.approved == [request.id]
