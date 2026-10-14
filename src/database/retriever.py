from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from src import config

def get_vector_db():
    embeddings = OpenAIEmbeddings(
        model=config.EMBEDDING_MODEL,
        openai_api_key=config.OPENAI_API_KEY
    )
    return Chroma(
        persist_directory=str(config.VECTOR_DB_DIR),
        embedding_function=embeddings
    )

def query_relevant_documents(query: str, module: str = None, k: int = 3, max_distance: float = 0.95):
    db = get_vector_db()
    search_kwargs = {}
    if module:
        search_kwargs["filter"] = {"module": module}
        
    try:
        results_with_scores = db.similarity_search_with_score(query, k=k, **search_kwargs)
        return [doc for doc, distance in results_with_scores if distance <= max_distance]
    except Exception:
        return db.similarity_search(query, k=k, **search_kwargs)
