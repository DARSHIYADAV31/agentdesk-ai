from pydantic import BaseModel


class LookupTicket(BaseModel):
    """Look up the current status of a ticket."""

    ticket_id: int


class UpdateTicket(BaseModel):
    """Mark a ticket resolved. Use status 'resolved' only if the knowledge base fully solves it."""

    ticket_id: int
    status: str
    resolution: str = ""


class Escalate(BaseModel):
    """Hand the ticket to a human agent, with a short reason."""

    ticket_id: int
    reason: str


class ResetPassword(BaseModel):
    """Reset a user's password. Destructive: needs human approval."""

    ticket_id: int
    username: str


class DeleteAccount(BaseModel):
    """Delete a user account. Destructive: needs human approval."""

    ticket_id: int
    username: str


def _tool(name: str, model: type[BaseModel]) -> dict:
    return {"name": name, "description": model.__doc__, "parameters": model.model_json_schema()}


TOOL_SCHEMAS = [
    _tool("lookup_ticket", LookupTicket),
    _tool("update_ticket", UpdateTicket),
    _tool("escalate", Escalate),
    _tool("reset_password", ResetPassword),
    _tool("delete_account", DeleteAccount),
]
