import pytest
from fastapi.testclient import TestClient

from app.api.runner import get_runner
from app.db.session import get_db
from app.db.user_model import User
from app.main import create_app
from app.security.passwords import hash_password
from tests.unit.api_helpers import FakeRunner


@pytest.fixture
def runner():
    return FakeRunner()


@pytest.fixture
def client(db, runner):
    db.add(User(username="ann", password_hash=hash_password("pw-ann"), role="agent"))
    db.add(User(username="root", password_hash=hash_password("pw-root"), role="admin"))
    db.commit()
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_runner] = lambda: runner
    return TestClient(app)
