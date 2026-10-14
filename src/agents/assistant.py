import logging
from functools import lru_cache
from typing import List, Optional, Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from src import config
from src.agents.prompts import REV_SYSTEM_PROMPT
from src.database.retriever import query_relevant_documents
from src.tools.bcb_tools import get_selic_rate, mentions_selic

logger = logging.getLogger(__name__)

FALLBACK_REPLY = (
    "Opa! Tive uma instabilidade momentânea para responder. "
    "Pode tentar enviar sua pergunta de novo em instantes?"
)

DEFAULT_SUGGESTIONS = [
    "Como o FGC protege meu dinheiro?",
    "O que é a regra 50-30-20?",
    "Quanto preciso para começar?",
]

DEFAULT_SOURCE_URL = "https://www.bcb.gov.br"
HISTORY_WINDOW = 6

class RevAssistantOutput(BaseModel):
    reply: str = Field(description="Resposta acolhedora, explicativa e motivadora do Rev.")
    suggestions: List[str] = Field(
        default_factory=list,
        description="2 a 3 perguntas curtas de continuação (máximo 50 a 60 caracteres cada) diretamente conectadas ao tema discutido."
    )

def sanitize_suggestions(raw_suggestions: Optional[List[Any]]) -> List[str]:
    """
    Limpa, formata e aplica o limiter rigoroso (máx 60 caracteres)
    nas sugestões geradas pela IA.
    """
    cleaned: List[str] = []
    for item in raw_suggestions or []:
        if not isinstance(item, str):
            continue
        text = item.strip().lstrip("-•* 0123456789.)").strip().strip('"\'`').strip()
        if not text:
            continue
        if len(text) > 60:
            text = text[:57].rstrip() + "..."
        if text not in cleaned:
            cleaned.append(text)
        if len(cleaned) == 3:
            break

    if not cleaned:
        cleaned = list(DEFAULT_SUGGESTIONS)
    return cleaned

@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=config.LLM_MODEL,
        temperature=config.LLM_TEMPERATURE,
        api_key=config.OPENAI_API_KEY
    )

def _turn_field(turn: Any, field: str) -> Optional[str]:
    """Lê role/content tanto de dicts quanto de modelos Pydantic do histórico."""
    if isinstance(turn, dict):
        return turn.get(field)
    return getattr(turn, field, None)

def _last_user_message(history: List[Any]) -> Optional[str]:
    for turn in reversed(history):
        content = _turn_field(turn, "content")
        if _turn_field(turn, "role") == "user" and content:
            return content
    return None

def _build_source(docs: List[Any]) -> dict:
    top_meta = docs[0].metadata
    url = next((doc.metadata.get("url") for doc in docs if doc.metadata.get("url")), DEFAULT_SOURCE_URL)
    return {
        "document": top_meta.get("document", top_meta.get("source", "Documento Oficial")),
        "section": top_meta.get("section", "Conceitos Fundamentais"),
        "institution": top_meta.get("institution", "Órgão Regulador"),
        "url": url,
    }

def _build_context_instruction(context_text: str, user_name: Optional[str], live_data: Optional[str]) -> str:
    user_info = f"\nNome do usuário: {user_name}." if user_name else ""
    live_info = f"\nDado em tempo real: {live_data}" if live_data else ""

    if context_text:
        return f"Contexto Oficial da Base:\n{context_text}{live_info}{user_info}"
    return (
        f"Aviso de Contexto: Nenhum documento da base de finanças atingiu relevância direta para esta pergunta.{live_info}{user_info} "
        "Se houver histórico de conversa prévio, use-o para esclarecer ou dar continuidade à dúvida do usuário. "
        "Se for saudação ou dúvida geral de finanças, acolha e ajude como Rev. "
        "Se for sobre tema fora do nicho financeiro (ex: animes, esportes, culinária), "
        "aplique o guardrail de recusa amigável sem citar fontes."
    )

def chat_rag(
    message: str,
    module: str = "modulo_1",
    history: Optional[List[Any]] = None,
    user_name: Optional[str] = None
) -> dict:
    history = history or []
    docs = query_relevant_documents(message, module=module, k=3, max_distance=0.95)

    # Perguntas de continuação ("e o CDB?") costumam depender da pergunta anterior
    if not docs:
        previous_question = _last_user_message(history)
        if previous_question:
            docs = query_relevant_documents(f"{previous_question} {message}", module=module, k=3, max_distance=0.95)

    context_text = "\n\n---\n\n".join(doc.page_content for doc in docs)
    primary_source = _build_source(docs) if docs else None
    live_data = get_selic_rate() if mentions_selic(message) else None

    # Conteúdo dinâmico entra como mensagem literal (não template) para que chaves {} no texto não quebrem o prompt
    prompt_messages: List[Any] = [
        SystemMessage(content=REV_SYSTEM_PROMPT + "\n\n" + _build_context_instruction(context_text, user_name, live_data))
    ]
    for turn in history[-HISTORY_WINDOW:]:
        content = _turn_field(turn, "content")
        if content:
            message_cls = HumanMessage if _turn_field(turn, "role") == "user" else AIMessage
            prompt_messages.append(message_cls(content=content))
    prompt_messages.append(("human", "{question}"))

    prompt = ChatPromptTemplate.from_messages(prompt_messages)
    llm = get_llm()

    try:
        output = (prompt | llm.with_structured_output(RevAssistantOutput)).invoke({"question": message})
        reply_content = output.reply
        generated_suggestions = sanitize_suggestions(output.suggestions)
    except Exception:
        logger.warning("Structured output falhou; usando resposta em texto livre", exc_info=True)
        generated_suggestions = list(DEFAULT_SUGGESTIONS)
        try:
            raw_response = (prompt | llm).invoke({"question": message})
            reply_content = raw_response.content if hasattr(raw_response, "content") else str(raw_response)
        except Exception:
            logger.exception("Falha ao gerar resposta do LLM")
            reply_content = FALLBACK_REPLY

    return {
        "reply": reply_content,
        "source": primary_source,
        "suggestions": generated_suggestions
    }
