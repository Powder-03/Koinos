"""
Service A: Standalone FastMCP Server Entrypoint

Runs the FastMCP server over SSE transport for remote tool access.
Render dynamically assigns $PORT, so we read it from the environment.

Usage:
    python -m src.infrastructure.mcp.run_server

Deploy on Render with:
    Start Command: python -m src.infrastructure.mcp.run_server
"""
import os
from src.infrastructure.mcp.server import mcp

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    print(f"🚀 Starting FastMCP SSE server on 0.0.0.0:{port}")
    mcp.run(transport="sse", host="0.0.0.0", port=port)
