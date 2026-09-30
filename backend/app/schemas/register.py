from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Username = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3,
                                            max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")]


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: Username
    # Never strip or alter passwords: login must see exactly what sign-up stored.
    password: str = Field(min_length=8, max_length=128)
