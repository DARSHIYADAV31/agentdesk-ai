from tests.unit.api_helpers import auth

NEW_USER = {"username": "carol", "password": "carol-pass-1"}


def test_register_returns_tokens_that_work(client):
    response = client.post("/auth/register", json=NEW_USER)
    assert response.status_code == 201
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    assert client.get("/tickets", headers=headers).status_code == 200


def test_duplicate_username_is_rejected(client):
    client.post("/auth/register", json=NEW_USER)
    assert client.post("/auth/register", json=NEW_USER).status_code == 409


def test_weak_or_invalid_input_is_rejected(client):
    assert client.post("/auth/register", json={**NEW_USER, "password": "short"}).status_code == 422
    assert client.post("/auth/register", json={**NEW_USER, "username": "a b"}).status_code == 422


def test_cannot_register_as_admin(client):
    body = {**NEW_USER, "role": "admin"}
    assert client.post("/auth/register", json=body).status_code == 422


def test_registered_user_cannot_approve_actions(client):
    tokens = client.post("/auth/register", json=NEW_USER).json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    response = client.post("/approvals/1/decision", json={"approve": True}, headers=headers)
    assert response.status_code == 403
    assert auth(client, "root")  # admin login still works


def test_password_with_spaces_logs_in_exactly_as_registered(client):
    body = {"username": "erin", "password": " spaced pass 1 "}
    assert client.post("/auth/register", json=body).status_code == 201
    assert client.post("/auth/login", json=body).status_code == 200
    trimmed = {**body, "password": "spaced pass 1"}
    assert client.post("/auth/login", json=trimmed).status_code == 401


def test_username_is_trimmed_on_register_and_login(client):
    client.post("/auth/register", json={"username": " frank ", "password": "frank-pass-1"})
    assert client.post("/auth/login", json={"username": "frank", "password": "frank-pass-1"}).status_code == 200
