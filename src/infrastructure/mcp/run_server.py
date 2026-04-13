"""
Service A: Standalone FastMCP Server Entrypoint with Health Check

Wraps the FastMCP SSE app inside a Starlette app to add a /health
endpoint for uptime bots. The /sse and /messages paths are handled
by the MCP SSE transport as usual.

Usage:
    python -m src.infrastructure.mcp.run_server

Deploy on Render with:
    Start Command: python -m src.infrastructure.mcp.run_server
"""
import os
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from src.infrastructure.mcp.server import mcp


async def health_check(request):
    """Lightweight endpoint for uptime bots to keep Service A warm."""
    return JSONResponse({"status": "healthy", "service": "koinos-mcp"})


# Build the combined app:
# 1. /health and / → health check (for uptime bots)
# 2. /sse, /messages → handled by FastMCP's SSE transport
app = Starlette(
    routes=[
        Route("/", health_check),
        Route("/health", health_check),
        Mount("/", app=mcp.sse_app()),
    ]
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    print(f"🚀 Starting FastMCP SSE server on 0.0.0.0:{port}")
    uvicorn.run(
        "src.infrastructure.mcp.run_server:app",
        host="0.0.0.0",
        port=port,
    )
