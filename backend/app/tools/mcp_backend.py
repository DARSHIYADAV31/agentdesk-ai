import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

BACKEND_DIR = Path(__file__).resolve().parents[2]
MCP_TOOLS = {"lookup_ticket", "update_ticket", "escalate"}


class McpBackend:
    """Calls tools on the MCP server over stdio, with a hard timeout."""

    def __init__(self, timeout: float = 20.0, env: dict | None = None):
        self.timeout = timeout
        self.env = {**os.environ, **(env or {})}

    def call(self, name: str, args: dict):
        return asyncio.run(asyncio.wait_for(self._call(name, args), self.timeout))

    async def _call(self, name: str, args: dict):
        params = StdioServerParameters(
            command=sys.executable, args=["-m", "app.mcp_server.server"],
            cwd=str(BACKEND_DIR), env=self.env,
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(name, args)
        if result.is_error:
            raise RuntimeError(f"MCP tool {name} returned an error")
        return result.structured_content or json.loads(result.content[0].text)
