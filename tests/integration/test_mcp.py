from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import models  # noqa: F401
from app.db.base import Base
from app.db.ticket_model import Ticket
from app.tools.mcp_backend import McpBackend


def test_lookup_and_update_through_real_mcp_server(tmp_path):
    url = f"sqlite:///{tmp_path / 'mcp.db'}"
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as db:
        db.add(Ticket(id=7, title="t", body="b", requester_email="a@b.com"))
        db.commit()
    backend = McpBackend(timeout=60, env={"DATABASE_URL": url})
    assert backend.call("lookup_ticket", {"ticket_id": 7})["status"] == "new"
    backend.call("update_ticket", {"ticket_id": 7, "status": "resolved"})
    assert backend.call("lookup_ticket", {"ticket_id": 7})["status"] == "resolved"
