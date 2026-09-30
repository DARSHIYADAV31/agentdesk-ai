from tests.unit.api_helpers import TICKET, login


def test_bad_login_is_rejected(client):
    response = client.post("/auth/login", json={"username": "ann", "password": "nope"})
    assert response.status_code == 401


def test_refresh_works_and_rejects_access_token(client):
    tokens = login(client, "ann")
    ok = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    bad = client.post("/auth/refresh", json={"refresh_token": tokens["access_token"]})
    assert (ok.status_code, bad.status_code) == (200, 401)


def test_tickets_require_authentication(client):
    assert client.post("/tickets", json=TICKET).status_code == 401
