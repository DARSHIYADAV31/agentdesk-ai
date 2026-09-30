import os

os.environ.setdefault("JWT_SECRET", "test-secret-test-secret-test-secret-32b")
os.environ.setdefault("WEBHOOK_SECRET", "hook-secret")
os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import models  # noqa: F401  (registers tables)
from app.db.base import Base
from app.db.ticket_model import Ticket


@pytest.fixture
def db():
    engine = create_engine("sqlite://", poolclass=StaticPool,
                           connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    session.add(Ticket(id=1, title="t", body="b", requester_email="a@b.com"))
    session.commit()
    yield session
    session.close()
