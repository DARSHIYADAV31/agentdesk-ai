from dataclasses import dataclass
from typing import Any, TypedDict


class PipelineState(TypedDict, total=False):
    ticket_id: int
    title: str
    body: str
    category: str
    priority: str
    kb: dict
    approval_id: int
    outcome: str
    error: str


@dataclass
class Deps:
    router: Any
    retriever: Any
    db: Any
    backend: Any
