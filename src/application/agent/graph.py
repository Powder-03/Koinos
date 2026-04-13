import os
from src.core.llm_factory import get_llm
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
from src.application.agent.state import AgentState
from src.infrastructure.database.connection import DATABASE_URL

# MCP Server URL — points to Service A (FastMCP over SSE)
# Local dev: http://localhost:8001/sse
# Render:    https://koinos-mcp.onrender.com/sse
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8001/sse")

system_prompt = SystemMessage(
    content="You are a dual-mode assistant. Always search the database via tools to "
            "confirm an ID before updating/deleting. If uncertain, ask for clarification. "
            "IMPORTANT: You do NOT need to provide a user_id to any tool — it is handled automatically."
)


async def get_remote_tools():
    """
    Connect to the remote FastMCP server over SSE and load its tools
    as LangChain-compatible tools via langchain-mcp-adapters.
    """
    read_stream, write_stream = await sse_client(MCP_SERVER_URL).__aenter__()  
    session = ClientSession(read_stream, write_stream)
    await session.__aenter__()
    await session.initialize()

    tools = await load_mcp_tools(session)
    return tools, session


async def get_graph():
    """
    Build and return the compiled LangGraph with:
    - Remote MCP tools fetched over SSE from Service A
    - Provider-agnostic LLM with tools bound (configured via LLM_PROVIDER env var)
    - Postgres-backed conversation memory
    """
    # 1. Fetch tools from remote MCP server
    tools_list, mcp_session = await get_remote_tools()

    # 2. Build LLM with tools (provider resolved from .env)
    llm = get_llm()
    llm_with_tools = llm.bind_tools(tools_list)
    tool_node = ToolNode(tools_list)

    # 3. Define the chatbot node
    async def chatbot(state: AgentState):
        messages = state["messages"]
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [system_prompt] + messages
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    # 4. Build the graph
    builder = StateGraph(AgentState)
    builder.add_node("agent", chatbot)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges(
        "agent",
        lambda state: "tools" if state["messages"][-1].tool_calls else END,
    )
    builder.add_edge("tools", "agent")

    # 5. Compile with Postgres memory
    from psycopg_pool import AsyncConnectionPool
    psycopg_url = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

    pool = AsyncConnectionPool(
        conninfo=psycopg_url,
        max_size=20,
    )
    saver = AsyncPostgresSaver(pool)
    await saver.setup()

    return builder.compile(checkpointer=saver)
