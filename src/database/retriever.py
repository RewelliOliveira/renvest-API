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

def get_retriever(module: str = None, k: int = 3):
    db = get_vector_db()
    search_kwargs = {"k": k}
    if module:
        search_kwargs["filter"] = {"module": module}
    return db.as_retriever(search_kwargs=search_kwargs)

def query_relevant_documents(query: str, module: str = None, k: int = 3):
    db = get_vector_db()
    search_kwargs = {}
    if module:
        search_kwargs["filter"] = {"module": module}
    return db.similarity_search(query, k=k, **search_kwargs)
