import logging
from functools import lru_cache
from typing import List, Optional
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from src import config

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=config.EMBEDDING_MODEL,
        api_key=config.OPENAI_API_KEY
    )

@lru_cache(maxsize=1)
def get_vector_db() -> Chroma:
    return Chroma(
        collection_name=config.VECTOR_COLLECTION_NAME,
        persist_directory=str(config.VECTOR_DB_DIR),
        embedding_function=get_embeddings(),
        collection_metadata={"hnsw:space": "cosine"},
    )

def query_relevant_documents(
    query: str,
    module: Optional[str] = None,
    k: int = config.RETRIEVAL_K,
    max_distance: float = config.RETRIEVAL_MAX_DISTANCE
) -> List[Document]:
    search_filter = {"module": module} if module else None
    try:
        results_with_scores = get_vector_db().similarity_search_with_score(query, k=k, filter=search_filter)
    except Exception:
        logger.exception("Falha na busca vetorial; seguindo sem contexto da base")
        return []
    return [doc for doc, distance in results_with_scores if distance <= max_distance]
