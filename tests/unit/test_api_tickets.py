from tests.unit.api_helpers import TICKET, auth


def test_submit_validates_input(client):
    bad = {**TICKET, "requester_email": "not-an-email", "title": "x"}
    assert client.post("/tickets", json=bad, headers=auth(client)).status_code == 422


def test_submit_creates_ticket_and_starts_pipeline(client, runner):
    response = client.post("/tickets", json=TICKET, headers=auth(client))
    assert response.status_code == 202 and runner.processed == [response.json()["id"]]


def test_webhook_needs_correct_secret(client, runner):
    assert client.post("/webhook/tickets", json=TICKET).status_code == 401
    headers = {"X-Webhook-Secret": "hook-secret"}
    good = client.post("/webhook/tickets", json=TICKET, headers=headers)
    assert good.status_code == 202 and runner.processed
