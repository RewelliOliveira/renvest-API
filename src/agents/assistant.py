from typing import List, Optional, Any, Union
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src import config
from src.agents.prompts import REV_SYSTEM_PROMPT
from src.database.retriever import query_relevant_documents

DEFAULT_SUGGESTIONS = [
    "Como o FGC protege meu dinheiro?",
    "O que é a regra 50-30-20?",
    "Quanto preciso para começar?",
]

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
        text = item.strip().strip('"\'`').lstrip("-•* 0123456789.)").strip()
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

def chat_rag(
    message: str,
    module: str = "modulo_1",
    history: Optional[List[Any]] = None,
    user_name: Optional[str] = None
) -> dict:
    docs = query_relevant_documents(message, module=module, k=3, max_distance=0.95)
    
    if not docs and history:
        past_user_queries = []
        for h in history:
            role = getattr(h, "role", None) if hasattr(h, "role") else (h.get("role") if isinstance(h, dict) else None)
            content = getattr(h, "content", "") if hasattr(h, "content") else (h.get("content", "") if isinstance(h, dict) else "")
            if role == "user" and content:
                past_user_queries.append(content)

        if past_user_queries:
            combined_query = f"{past_user_queries[-1]} {message}"
            docs = query_relevant_documents(combined_query, module=module, k=3, max_distance=0.95)
    
    context_text = ""
    primary_source = None

    if docs:
        context_parts = [doc.page_content for doc in docs]
        context_text = "\n\n---\n\n".join(context_parts)
        
        top_meta = docs[0].metadata
        url_found = top_meta.get("url")
        if not url_found:
            for doc in docs:
                candidate = doc.metadata.get("url")
                if candidate:
                    url_found = candidate
                    break
        if not url_found:
            url_found = "https://www.bcb.gov.br"

        primary_source = {
            "document": top_meta.get("document", top_meta.get("source", "Documento Oficial")),
            "section": top_meta.get("section", "Conceitos Fundamentais"),
            "institution": top_meta.get("institution", "Órgão Regulador"),
            "url": url_found
        }

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        openai_api_key=config.OPENAI_API_KEY
    )

    user_info = f"\nNome do usuário: {user_name}." if user_name else ""

    if context_text:
        context_instruction = f"Contexto Oficial da Base:\n{context_text}{user_info}"
    else:
        context_instruction = (
            f"Aviso de Contexto: Nenhum documento da base de finanças atingiu relevância direta para esta pergunta.{user_info} "
            "Se houver histórico de conversa prévio, use-o para esclarecer ou dar continuidade à dúvida do usuário. "
            "Se for saudação ou dúvida geral de finanças, acolha e ajude como Rev. "
            "Se for sobre tema fora do nicho financeiro (ex: animes, esportes, culinária), "
            "aplique o guardrail de recusa amigável sem citar fontes."
        )

    prompt_messages = [("system", REV_SYSTEM_PROMPT + "\n\n" + context_instruction)]
    
    if history:
        for turn in history[-6:]:
            role = getattr(turn, "role", None) if hasattr(turn, "role") else (turn.get("role") if isinstance(turn, dict) else None)
            content = getattr(turn, "content", "") if hasattr(turn, "content") else (turn.get("content", "") if isinstance(turn, dict) else "")
            if content:
                msg_role = "human" if role == "user" else "ai"
                prompt_messages.append((msg_role, content))
                
    prompt_messages.append(("human", "{question}"))

    prompt = ChatPromptTemplate.from_messages(prompt_messages)

    reply_content = ""
    generated_suggestions: List[str] = []

    try:
        structured_llm = llm.with_structured_output(RevAssistantOutput)
        chain = prompt | structured_llm
        output: RevAssistantOutput = chain.invoke({"question": message})
        
        reply_content = output.reply
        generated_suggestions = sanitize_suggestions(output.suggestions)
    except Exception as e:
        # Fallback seguro caso o structured output falhe
        try:
            standard_chain = prompt | llm
            raw_response = standard_chain.invoke({"question": message})
            reply_content = raw_response.content if hasattr(raw_response, "content") else str(raw_response)
            generated_suggestions = list(DEFAULT_SUGGESTIONS)
        except Exception as inner_err:
            reply_content = f"Olá! Tive uma pequena instabilidade para responder: {str(inner_err)}"
            generated_suggestions = list(DEFAULT_SUGGESTIONS)

    return {
        "reply": reply_content,
        "source": primary_source,
        "suggestions": generated_suggestions
    }
