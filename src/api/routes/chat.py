from fastapi import APIRouter
from src.schemas.chat import ChatRequest, ChatResponse
from src.services.chat_service import ChatService

router = APIRouter(tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
def handle_chat(payload: ChatRequest):
    return ChatService.process_message(
        message=payload.message,
        module=payload.module,
        history=payload.history
    )
