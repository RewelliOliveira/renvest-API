import logging
from functools import lru_cache
from typing import List, Optional
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from src import config
from src.repositories.chunk_repository import ChunkRepository

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=config.EMBEDDING_MODEL,
        api_key=config.OPENAI_API_KEY
    )

def query_relevant_documents(
    query: str,
    module: Optional[str] = None,
    k: int = config.RETRIEVAL_K,
    max_distance: float = config.RETRIEVAL_MAX_DISTANCE
) -> List[Document]:
    try:
        embedding = get_embeddings().embed_query(query)
        rows = ChunkRepository.match(embedding, match_count=k, module=module)
    except Exception:
        logger.exception("Falha na busca vetorial; seguindo sem contexto da base")
        return []
    return [
        Document(id=row["id"], page_content=row["content"], metadata={**row["metadata"], "distance": row["distance"]})
        for row in rows
        if row["distance"] <= max_distance
    ]
