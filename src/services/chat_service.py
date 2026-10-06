from typing import Optional, List, Dict
from src.agents.assistant import chat_rag
from src.schemas.chat import ChatResponse

class ChatService:
    @staticmethod
    def process_message(
        message: str,
        module: Optional[str] = "modulo_1",
        history: Optional[List[Dict[str, str]]] = None
    ) -> ChatResponse:
        result = chat_rag(
            message=message,
            module=module or "modulo_1",
            history=history
        )
        return ChatResponse(**result)
