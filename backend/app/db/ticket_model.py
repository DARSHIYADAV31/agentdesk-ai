from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    requester_email: Mapped[str] = mapped_column(String(254))
    # Username of the submitter; None for webhook/system tickets (admin-only visibility).
    owner: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    # Username of the person the admin assigned this ticket to.
    assignee: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="new")
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Username of the human who resolved it manually; None when the AI resolved it.
    resolved_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cost_usd: Mapped[float] = mapped_column(default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
