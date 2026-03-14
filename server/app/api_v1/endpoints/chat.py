from fastapi import APIRouter
from typing import List, Optional
from pydantic import BaseModel
from app.engine.llm_service import llm_service

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    sources: List[str] = []


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    response, sources = llm_service.chat_with_retrieval(request.message)
    
    return ChatResponse(
        message=response,
        sources=sources
    )
