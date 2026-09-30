from app.tools.mcp_backend import MCP_TOOLS


class CompositeBackend:
    """MCP for the tools it exposes; in-process for the approval-gated destructive ones."""

    def __init__(self, mcp_backend, local_backend):
        self.mcp = mcp_backend
        self.local = local_backend

    def call(self, name: str, args: dict):
        backend = self.mcp if name in MCP_TOOLS else self.local
        return backend.call(name, args)
