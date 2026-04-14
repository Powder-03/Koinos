import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from src.application.agent.graph import get_graph
from src.infrastructure.auth.firebase import verify_firebase_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["Voice Mode"])

# Cache the compiled graph so we don't re-connect to MCP on every request
_cached_graph = None

class VoiceRequest(BaseModel):
    message: str
    # user_id removed — we now trust the Firebase token, not the client body


async def _get_or_build_graph():
    """
    Lazily build and cache the compiled LangGraph.
    The first call connects to the remote MCP server over SSE,
    loads tools, binds them to the LLM, and compiles the graph.
    Subsequent calls reuse the cached graph.
    """
    global _cached_graph
    if _cached_graph is None:
        logger.info("⏳ Building LangGraph — connecting to remote MCP server...")
        try:
            _cached_graph = await get_graph()
            logger.info("✅ LangGraph built successfully with remote MCP tools.")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MCP server: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"AI service unavailable — could not connect to MCP tool server: {str(e)}"
            )
    return _cached_graph


@router.post("/")
async def process_voice_command(
    request: VoiceRequest,
    user_id: str = Depends(verify_firebase_token)
):
    try:
        graph = await _get_or_build_graph()

        # Use the verified Firebase UID as the thread_id for memory
        # AND inject it into state so the LLM passes it to remote MCP tools
        config = {"configurable": {"thread_id": user_id}}

        input_message = HumanMessage(content=request.message)
        result = await graph.ainvoke(
            {"messages": [input_message], "user_id": user_id},
            config,
        )

        ai_response = result["messages"][-1].content

        return {"response": ai_response}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice command error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
