from pydantic import Field, model_validator

from app.schemas.ticket import TicketCreate


class AdminTicketCreate(TicketCreate):
    owner: str | None = Field(default=None, max_length=50)  # employee it is for; None = the admin
    assignee: str | None = Field(default=None, max_length=50)
    skip_ai: bool = False  # hand straight to the assignee instead of letting the AI try first

    @model_validator(mode="after")
    def skip_needs_assignee(self):
        if self.skip_ai and not self.assignee:
            raise ValueError("skip_ai requires an assignee")
        return self
