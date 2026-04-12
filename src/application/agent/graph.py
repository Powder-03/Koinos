import os
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
# If mcp from fastmcp can export tools to langchain, we get them. For now, importing functions to wrap.
from src.infrastructure.mcp.server import add_expense, search_expenses, update_expense, delete_expense
from src.application.agent.state import AgentState
from src.infrastructure.database.connection import DATABASE_URL
from src.core.config import settings

# Wrap the FastMCP functions natively as LangChain tools, or assume mcp.export() handles it.
# We will use the standalone functions directly as langchain tools for the graph execution here.
from langchain_core.tools import tool

@tool
async def lc_add_expense(amount: float, category: str, expense_date: str, description: str = None) -> str:
    """Log or add a new expense."""
    return await add_expense(amount, category, expense_date, description)

@tool
async def lc_search_expenses(category: str = None, expense_date: str = None, amount: float = None) -> str:
    """Search the database for expenses. Always use this to confirm an expense ID before updating or deleting."""
    return await search_expenses(category, expense_date, amount)

@tool
async def lc_update_expense(expense_id: int, amount: float = None, category: str = None, expense_date: str = None, description: str = None) -> str:
    """Update an existing expense. You MUST know the exact ID."""
    return await update_expense(expense_id, amount, category, expense_date, description)

@tool
async def lc_delete_expense(expense_id: int) -> str:
    """Delete an expense. You MUST know the exact ID."""
    return await delete_expense(expense_id)

tools_list = [lc_add_expense, lc_search_expenses, lc_update_expense, lc_delete_expense]
tool_node = ToolNode(tools_list)

llm = ChatGroq(
    model=settings.llm_model_name, 
    temperature=settings.llm_temperature
)
llm_with_tools = llm.bind_tools(tools_list)

system_prompt = SystemMessage(
    content="You are a dual-mode assistant. Always search the database via tools to "
            "confirm an ID before updating/deleting. If uncertain, ask for clarification."
)

async def chatbot(state: AgentState):
    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [system_prompt] + messages
    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}

# Build Graph
builder = StateGraph(AgentState)
builder.add_node("agent", chatbot)
builder.add_node("tools", tool_node)

builder.add_edge(START, "agent")
builder.add_conditional_edges(
    "agent",
    lambda state: "tools" if state["messages"][-1].tool_calls else END,
)
builder.add_edge("tools", "agent")

# Memory Saver wrapper
async def get_graph():
    # Helper to return compiled graph using a connection pool for memory
    # Requires an asyncpg connection pool to be passed to AsyncPostgresSaver.
    from psycopg_pool import AsyncConnectionPool
    # Extract psycopg-compatible URL (replacing postgresql+asyncpg with postgresql)
    psycopg_url = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
    
    pool = AsyncConnectionPool(
        conninfo=psycopg_url,
        max_size=20,
    )
    saver = AsyncPostgresSaver(pool)
    await saver.setup()
    
    return builder.compile(checkpointer=saver)
