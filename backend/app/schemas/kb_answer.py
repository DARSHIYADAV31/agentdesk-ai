from pydantic import BaseModel, Field


class KBAnswer(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    can_resolve: bool = False

    @classmethod
    def no_source(cls) -> "KBAnswer":
        return cls(answer="No relevant knowledge-base article found.", can_resolve=False)
