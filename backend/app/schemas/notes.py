from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.ticket import ActionOut, TicketOut


class AssignRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    assignee: str | None = Field(default=None, max_length=50)  # None = unassign


class NoteCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    text: str = Field(min_length=1, max_length=2000)


class ResolveRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    resolution: str = Field(min_length=1, max_length=2000)


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author: str
    text: str
    created_at: datetime


class TicketDetail(TicketOut):
    actions: list[ActionOut]
    notes: list[NoteOut] = []
