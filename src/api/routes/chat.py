from typing import Optional
from fastapi import APIRouter, Depends, Query
from src.schemas.chat import ChatRequest, ChatResponse, SuggestionsResponse
from src.schemas.auth import UserResponse
from src.services.chat_service import ChatService
from src.api.dependencies import get_current_user_optional

router = APIRouter(tags=["chat"])

@router.get("/chat/suggestions", response_model=SuggestionsResponse)
def get_chat_suggestions(
    module: str = Query("modulo_1", description="Identificador do módulo")
):
    """
    Retorna as perguntas sugeridas iniciais para o módulo solicitado.
    """
    suggestions = ChatService.get_initial_suggestions(module=module)
    return SuggestionsResponse(module=module, suggestions=suggestions)

@router.post("/chat", response_model=ChatResponse)
def handle_chat(
    payload: ChatRequest,
    current_user: Optional[UserResponse] = Depends(get_current_user_optional)
):
    """
    Processa a mensagem do usuário via pipeline RAG, retornando a resposta explicativa,
    fonte oficial consultada e sugestões contextuais de continuidade.
    """
    user_name = current_user.name.split()[0] if (current_user and current_user.name) else None
    return ChatService.process_message(
        message=payload.message,
        module=payload.module,
        history=payload.history,
        user_name=user_name
    )
