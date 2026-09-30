from sqlalchemy.orm import Session

from app.tools import local_tools


class LocalBackend:
    """Runs tools in-process; the MCP backend exposes the same call() method."""

    def __init__(self, db: Session):
        self.db = db

    def call(self, name: str, args: dict):
        return getattr(local_tools, name)(self.db, **args)
