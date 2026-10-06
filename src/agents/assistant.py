from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src import config
from src.agents.prompts import REV_SYSTEM_PROMPT
from src.database.retriever import query_relevant_documents

def chat_rag(message: str, module: str = "modulo_1") -> dict:
    """Processa a mensagem do usuário via RAG e retorna a resposta formatada
    com a fonte oficial correspondente para o frontend.
    """
    docs = query_relevant_documents(message, module=module, k=3)
    
    context_text = ""
    primary_source = {
        "document": "Bora Investir B3 / Banco Central do Brasil",
        "section": "Diretrizes de Educação Financeira para Iniciantes",
        "institution": "BCB / B3",
        "url": "https://borainvestir.b3.com.br"
    }

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
            "document": top_meta.get("document", top_meta.get("source", "Oficial")),
            "section": top_meta.get("section", "Conceitos Fundamentais"),
            "institution": top_meta.get("institution", "Órgão Regulador"),
            "url": url_found
        }

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        openai_api_key=config.OPENAI_API_KEY
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", REV_SYSTEM_PROMPT + "\n\nContexto Oficial da Base:\n{context}"),
        ("human", "{question}")
    ])

    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "context": context_text if context_text else "Utilize as diretrizes oficiais de finanças do SFN.",
            "question": message
        })
        reply_content = response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        reply_content = f"Desculpe, tive um probleminha para consultar a base oficial: {str(e)}"

    return {
        "reply": reply_content,
        "source": primary_source
    }
