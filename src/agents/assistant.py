from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src import config
from src.agents.prompts import REV_SYSTEM_PROMPT
from src.database.retriever import query_relevant_documents

from typing import List, Optional

def chat_rag(message: str, module: str = "modulo_1", history: Optional[List[dict]] = None) -> dict:
    """Processa a mensagem do usuário via RAG e retorna a resposta formatada
    com a fonte oficial correspondente para o frontend, mantendo histórico de conversa
    e aplicando guardrails de nicho.
    """
    # 1. Recupera documentos relevantes para a mensagem atual
    docs = query_relevant_documents(message, module=module, k=3, max_distance=0.95)
    
    # Se a mensagem atual for curta ou de acompanhamento ("e com quanto?", "você não respondeu"),
    # tenta contextualizar a busca usando a última dúvida financeira do histórico
    if not docs and history:
        past_user_queries = [
            h.get("content", "") for h in history 
            if h.get("role") == "user" and h.get("content")
        ]
        if past_user_queries:
            combined_query = f"{past_user_queries[-1]} {message}"
            docs = query_relevant_documents(combined_query, module=module, k=3, max_distance=0.95)
    
    context_text = ""
    primary_source = None

    if docs:
        context_parts = []
        for doc in docs:
            context_parts.append(doc.page_content)
        context_text = "\n\n---\n\n".join(context_parts)
        
        top_meta = docs[0].metadata
        
        # Encontra URL valida entre os chunks recuperados
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
        temperature=0.2,
        openai_api_key=config.OPENAI_API_KEY
    )

    if context_text:
        context_instruction = f"Contexto Oficial da Base:\n{context_text}"
    else:
        context_instruction = (
            "Aviso de Contexto: Nenhum documento da base de finanças atingiu relevância direta para esta pergunta. "
            "Se houver histórico de conversa prévio, use-o para esclarecer ou dar continuidade à dúvida do usuário. "
            "Se for saudação ou dúvida geral de finanças, acolha e ajude como Rev. "
            "Se for sobre tema fora do nicho financeiro (ex: animes, esportes, culinária), "
            "aplique o guardrail de recusa amigável sem citar fontes."
        )

    # Monta a cadeia de mensagens incluindo o histórico recente
    prompt_messages = [("system", REV_SYSTEM_PROMPT + "\n\n" + context_instruction)]
    if history:
        for turn in history[-6:]:
            role = "human" if turn.get("role") == "user" else "ai"
            content = turn.get("content", "")
            if content:
                prompt_messages.append((role, content))
                
    prompt_messages.append(("human", "{question}"))

    prompt = ChatPromptTemplate.from_messages(prompt_messages)
    chain = prompt | llm
    
    try:
        response = chain.invoke({"question": message})
        reply_content = response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        reply_content = f"Desculpe, tive um probleminha para processar sua mensagem: {str(e)}"

    return {
        "reply": reply_content,
        "source": primary_source
    }
