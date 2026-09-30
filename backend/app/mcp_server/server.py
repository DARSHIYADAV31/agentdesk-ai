from mcp.server.mcpserver import MCPServer

from app.db.session import SessionLocal
from app.tools import local_tools

# Destructive tools are deliberately NOT exposed here: they run only behind the approval gate.
mcp = MCPServer("agentdesk")


@mcp.tool()
def lookup_ticket(ticket_id: int) -> dict:
    """Look up a ticket's status, category and priority."""
    with SessionLocal() as db:
        return local_tools.lookup_ticket(db, ticket_id)


@mcp.tool()
def update_ticket(ticket_id: int, status: str, resolution: str = "") -> dict:
    """Update a ticket's status and resolution note."""
    with SessionLocal() as db:
        return local_tools.update_ticket(db, ticket_id, status, resolution)


@mcp.tool()
def escalate(ticket_id: int, reason: str) -> dict:
    """Escalate a ticket to a human agent."""
    with SessionLocal() as db:
        return local_tools.escalate(db, ticket_id, reason)


if __name__ == "__main__":
    mcp.run()  # stdio transport; stdout is the protocol channel, so never print here
