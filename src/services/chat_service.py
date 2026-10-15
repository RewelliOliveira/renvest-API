from typing import Optional, List, Any
from src.agents.assistant import chat_rag, DEFAULT_SUGGESTIONS
from src.schemas.chat import ChatResponse

MODULE_SUGGESTIONS = {
    "modulo_1": [
        "Como o FGC protege meu dinheiro?",
        "O que é a regra 50-30-20?",
        "Quanto preciso para começar a investir?",
    ]
}

class ChatService:
    @staticmethod
    def process_message(
        message: str,
        module: Optional[str] = "modulo_1",
        history: Optional[List[Any]] = None,
        user_name: Optional[str] = None
    ) -> ChatResponse:
        result = chat_rag(
            message=message,
            module=module or "modulo_1",
            history=history,
            user_name=user_name
        )
        return ChatResponse(**result)

    @staticmethod
    def get_initial_suggestions(module: str = "modulo_1") -> List[str]:
        return MODULE_SUGGESTIONS.get(module, DEFAULT_SUGGESTIONS)
