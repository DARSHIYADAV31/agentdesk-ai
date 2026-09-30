from dataclasses import dataclass


@dataclass(frozen=True)
class ToolSpec:
    name: str
    destructive: bool
    params: tuple
    required: tuple


TOOL_SPECS = {
    spec.name: spec
    for spec in [
        ToolSpec("lookup_ticket", False, ("ticket_id",), ("ticket_id",)),
        ToolSpec("update_ticket", False, ("ticket_id", "status", "resolution"), ("ticket_id", "status")),
        ToolSpec("escalate", False, ("ticket_id", "reason"), ("ticket_id", "reason")),
        ToolSpec("reset_password", True, ("ticket_id", "username"), ("ticket_id", "username")),
        ToolSpec("delete_account", True, ("ticket_id", "username"), ("ticket_id", "username")),
    ]
}


def get_spec(name: str) -> ToolSpec:
    if name not in TOOL_SPECS:
        raise ValueError(f"unknown tool: {name}")
    return TOOL_SPECS[name]
