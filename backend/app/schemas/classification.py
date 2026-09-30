from typing import Literal

from pydantic import BaseModel, Field

Category = Literal["hardware", "software", "network", "access", "account", "billing", "other"]
Priority = Literal["low", "medium", "high", "critical"]


class Classification(BaseModel):
    category: Category
    priority: Priority
    reasoning: str = Field(default="", max_length=500)

    @classmethod
    def fallback(cls) -> "Classification":
        return cls(category="other", priority="medium", reasoning="unparseable model output")
