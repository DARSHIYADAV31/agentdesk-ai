from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TicketCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str = Field(min_length=5, max_length=200)
    body: str = Field(min_length=10, max_length=5000)
    requester_email: EmailStr


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    requester_email: str
    owner: str | None
    assignee: str | None
    category: str | None
    priority: str | None
    status: str
    resolution: str | None
    resolved_by: str | None
    cost_usd: float
    created_at: datetime


class ActionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    agent: str
    decision: str
    reasoning: str
    created_at: datetime
