import uuid
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from src.application.agent.graph import get_graph

router = APIRouter(prefix="/api/voice", tags=["Voice Mode"])

class VoiceRequest(BaseModel):
    message: str
    user_id: str

@router.post("/")
async def process_voice_command(request: VoiceRequest):
    try:
        graph = await get_graph()
        
        # Use user_id as the thread_id for conversation memory
        config = {"configurable": {"thread_id": request.user_id}}
        
        input_message = HumanMessage(content=request.message)
        result = await graph.ainvoke({"messages": [input_message]}, config)
        
        # Get the AI's latest response
        ai_response = result["messages"][-1].content
        
        return {"response": ai_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
