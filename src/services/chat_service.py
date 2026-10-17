from typing import Optional, List, Any
from src.agents.assistant import chat_rag, DEFAULT_SUGGESTIONS
from src.content.curriculum import get_module
from src.schemas.chat import ChatResponse

MAX_INITIAL_SUGGESTIONS = 4

class ChatService:
    @staticmethod
    def process_message(
        message: str,
        module: Optional[str] = None,
        history: Optional[List[Any]] = None,
        user_name: Optional[str] = None
    ) -> ChatResponse:
        result = chat_rag(
            message=message,
            module=module,
            history=history,
            user_name=user_name
        )
        return ChatResponse(**result)

    @staticmethod
    def get_initial_suggestions(module: str = "modulo_1") -> List[str]:
        """Primeira pergunta sugerida de cada lição do módulo, para cobrir os temas da trilha."""
        current = get_module(module)
        if not current:
            return list(DEFAULT_SUGGESTIONS)
        suggestions = [lesson.chat_suggestions[0] for lesson in current.lessons if lesson.chat_suggestions]
        return suggestions[:MAX_INITIAL_SUGGESTIONS] or list(DEFAULT_SUGGESTIONS)
