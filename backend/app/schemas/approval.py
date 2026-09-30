import json
from datetime import datetime

from pydantic import BaseModel, ConfigDict, computed_field


class ApprovalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    tool: str
    args_json: str
    status: str
    decided_by: str | None
    created_at: datetime

    @computed_field
    @property
    def args(self) -> dict:
        return json.loads(self.args_json)


class Decision(BaseModel):
    approve: bool
