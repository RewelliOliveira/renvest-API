import logging
import time
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
    reply: str = Field(description="Resposta acolhedora, explicativa e motivadora do Rev, indicando a fonte de cada informação.")
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

def _source_entry(metadata: dict) -> dict:
    return {
        "document": metadata.get("document", metadata.get("source", "Documento Oficial")),
        "section": metadata.get("section", "Conceitos Fundamentais"),
        "institution": metadata.get("institution", "Órgão Regulador"),
        "url": metadata.get("url") or DEFAULT_SOURCE_URL,
    }

def build_sources(docs: List[Any]) -> List[dict]:
    """Uma fonte por documento e página, na ordem de relevância, cada uma com a URL do próprio documento."""
    sources: List[dict] = []
    for doc in docs:
        entry = _source_entry(doc.metadata)
        if not any(s["document"] == entry["document"] and s["section"] == entry["section"] for s in sources):
            sources.append(entry)
    return sources

def format_context(docs: List[Any]) -> str:
    """Prefixa cada trecho com documento, instituição e página para o LLM poder citar a origem."""
    blocks = []
    for doc in docs:
        entry = _source_entry(doc.metadata)
        blocks.append(f"[Fonte: {entry['document']} – {entry['institution']}, {entry['section']}]\n{doc.page_content}")
    return "\n\n---\n\n".join(blocks)

def build_context_instruction(context_text: str, user_name: Optional[str], live_data: Optional[str]) -> str:
    user_info = f"\nNome do usuário: {user_name}." if user_name else ""
    live_info = f"\nDado em tempo real: {live_data}" if live_data else ""

    if context_text:
        return (
            f"Contexto Oficial da Base:\n{context_text}{live_info}{user_info}\n\n"
            "Lembrete: use somente as informações dos trechos acima (e do dado em tempo real, se houver), "
            "citando no texto o documento e a página de onde cada informação veio. "
            "Não acrescente produtos, números ou regras que não apareçam nos trechos."
        )
    return (
        f"Aviso de Contexto: Nenhum documento da base de finanças atingiu relevância direta para esta pergunta.{live_info}{user_info} "
        "Se houver histórico de conversa prévio, use-o para esclarecer ou dar continuidade à dúvida do usuário. "
        "Se for saudação ou dúvida geral de finanças, acolha e ajude como Rev. "
        "Se for sobre tema fora do nicho financeiro (ex: animes, esportes, culinária), "
        "aplique o guardrail de recusa amigável sem citar fontes."
    )

def retrieve(message: str, module: Optional[str] = None, history: Optional[List[Any]] = None) -> List[Any]:
    docs = query_relevant_documents(message, module=module)

    # Perguntas de continuação ("e o CDB?") costumam depender da pergunta anterior
    if not docs:
        previous_question = _last_user_message(history or [])
        if previous_question:
            docs = query_relevant_documents(f"{previous_question} {message}", module=module)
    return docs

def _token_usage(message: Any) -> dict:
    usage = getattr(message, "usage_metadata", None) or {}
    return {"tokens_in": usage.get("input_tokens"), "tokens_out": usage.get("output_tokens")}

def generate(
    message: str,
    instruction: str,
    history: Optional[List[Any]] = None,
    system_prompt: str = REV_SYSTEM_PROMPT
) -> dict:
    """Gera a resposta do Rev com o prompt de sistema + instrução de contexto, devolvendo também o uso de tokens."""
    # Conteúdo dinâmico entra como mensagem literal (não template) para que chaves {} no texto não quebrem o prompt
    prompt_messages: List[Any] = [SystemMessage(content=system_prompt + "\n\n" + instruction)]
    for turn in (history or [])[-HISTORY_WINDOW:]:
        content = _turn_field(turn, "content")
        if content:
            message_cls = HumanMessage if _turn_field(turn, "role") == "user" else AIMessage
            prompt_messages.append(message_cls(content=content))
    prompt_messages.append(("human", "{question}"))

    prompt = ChatPromptTemplate.from_messages(prompt_messages)
    llm = get_llm()

    try:
        output = (prompt | llm.with_structured_output(RevAssistantOutput, include_raw=True)).invoke({"question": message})
        parsed = output["parsed"]
        if parsed is None:
            raise ValueError(output.get("parsing_error") or "Structured output vazio")
        return {
            "reply": parsed.reply,
            "suggestions": sanitize_suggestions(parsed.suggestions),
            **_token_usage(output["raw"]),
        }
    except Exception:
        logger.warning("Structured output falhou; usando resposta em texto livre", exc_info=True)

    try:
        raw_response = (prompt | llm).invoke({"question": message})
        reply_content = raw_response.content if hasattr(raw_response, "content") else str(raw_response)
        usage = _token_usage(raw_response)
    except Exception:
        logger.exception("Falha ao gerar resposta do LLM")
        reply_content = FALLBACK_REPLY
        usage = _token_usage(None)
    return {"reply": reply_content, "suggestions": list(DEFAULT_SUGGESTIONS), **usage}

def chat_rag(
    message: str,
    module: Optional[str] = None,
    history: Optional[List[Any]] = None,
    user_name: Optional[str] = None
) -> dict:
    started = time.perf_counter()
    docs = retrieve(message, module=module, history=history)
    retrieval_ms = (time.perf_counter() - started) * 1000

    live_data = get_selic_rate() if mentions_selic(message) else None
    instruction = build_context_instruction(format_context(docs), user_name, live_data)

    started = time.perf_counter()
    result = generate(message, instruction, history=history)
    generation_ms = (time.perf_counter() - started) * 1000

    logger.info(
        "chat_rag module=%s docs=%d retrieval_ms=%.0f generation_ms=%.0f tokens_in=%s tokens_out=%s",
        module, len(docs), retrieval_ms, generation_ms, result["tokens_in"], result["tokens_out"]
    )

    sources = build_sources(docs)
    return {
        "reply": result["reply"],
        "source": sources[0] if sources else None,
        "sources": sources,
        "suggestions": result["suggestions"]
    }
