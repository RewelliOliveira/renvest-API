import os
import re
import glob
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from src import config

def extract_metadata_from_markdown(content: str, file_path: str) -> dict:
    folder_name = os.path.basename(os.path.dirname(file_path))
    file_name = os.path.basename(file_path)
    module_id = "modulo_1" if "modulo_1" in folder_name else folder_name

    meta = {
        "source": file_name,
        "module": module_id,
        "topic": file_name.replace(".md", ""),
        "document": "Documento Oficial",
        "section": "Conceitos Fundamentais",
        "institution": "Órgão Regulador",
        "url": "https://www.bcb.gov.br"
    }

    url_match = re.search(r"https?://[^\s\)\>]+", content)
    if url_match:
        meta["url"] = url_match.group(0).strip()

    for line in content.splitlines():
        line_strip = line.strip()
        if line_strip.startswith("# "):
            meta["topic"] = line_strip.replace("# ", "").strip()
        elif "Documento Oficial:" in line_strip:
            meta["document"] = line_strip.split("Documento Oficial:", 1)[1].replace("*", "").strip()
        elif "Seção:" in line_strip or "Secao:" in line_strip:
            meta["section"] = line_strip.split(":", 1)[1].replace("*", "").strip()
        elif "Instituição:" in line_strip or "Instituições:" in line_strip or "Instituicao:" in line_strip:
            meta["institution"] = line_strip.split(":", 1)[1].replace("*", "").strip()

    return meta

def load_documents():
    documents = []
    md_paths = glob.glob(os.path.join(config.RAW_DATA_DIR, "**", "*.md"), recursive=True)
    
    if not md_paths:
        md_paths = glob.glob(os.path.join(config.RAW_DATA_DIR, "*.md"))
        
    for md_path in md_paths:
        file_name = os.path.basename(md_path)
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                
            if not content:
                continue
                
            metadata = extract_metadata_from_markdown(content, md_path)
            doc_obj = Document(
                page_content=content,
                metadata=metadata
            )
            documents.append(doc_obj)
            print(f"[OK] Carregado: {file_name} -> [{metadata['document']}] (URL: {metadata['url']})")
        except Exception as e:
            print(f"[ERRO] Falha ao carregar {file_name}: {e}")
            
    return documents

def split_chunks(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "]
    )

    chunks = text_splitter.split_documents(documents)
    print(f"Total de chunks gerados para indexacao: {len(chunks)}")
    return chunks

def vectorize_chunks(chunks):
    embeddings = OpenAIEmbeddings(
        model=config.EMBEDDING_MODEL,
        openai_api_key=config.OPENAI_API_KEY
    )
    
    # Limpa dados anteriores para garantir que chunks obsoletos nao persistam
    try:
        existing_db = Chroma(
            persist_directory=str(config.VECTOR_DB_DIR),
            embedding_function=embeddings
        )
        existing_db.delete_collection()
    except Exception:
        pass

    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(config.VECTOR_DB_DIR)
    )
    print(f"[OK] Banco vetorial ChromaDB indexado com sucesso em: {config.VECTOR_DB_DIR}")

def run_ingestion():
    print("Iniciando processo de ingestao RAG...")
    documents = load_documents()
    if not documents:
        print("Nenhum documento .md encontrado em data/raw/ para ingestao.")
        return
        
    chunks = split_chunks(documents)
    vectorize_chunks(chunks)
    print("Ingestao concluida com sucesso!")

if __name__ == "__main__":
    run_ingestion()
