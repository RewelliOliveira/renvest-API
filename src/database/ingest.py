import logging
import os
import re
import glob
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src import config
from src.database.retriever import get_vector_db

logger = logging.getLogger(__name__)

MODULE_FOLDER_PATTERN = re.compile(r"(modulo_\d+)")
DEFAULT_MODULE = "geral"

def extract_metadata_from_markdown(content: str, file_path: str) -> dict:
    folder_name = os.path.basename(os.path.dirname(file_path))
    file_name = os.path.basename(file_path)
    # Pastas no formato "modulo_N_descricao" são indexadas como "modulo_N"
    module_match = MODULE_FOLDER_PATTERN.match(folder_name)
    module_id = module_match.group(1) if module_match else DEFAULT_MODULE

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

    for md_path in md_paths:
        file_name = os.path.basename(md_path)
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if not content:
                continue

            metadata = extract_metadata_from_markdown(content, md_path)
            documents.append(Document(page_content=content, metadata=metadata))
            logger.info("Carregado: %s -> [%s] módulo=%s", file_name, metadata["document"], metadata["module"])
        except Exception:
            logger.exception("Falha ao carregar %s", file_name)

    return documents

def split_chunks(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "]
    )

    chunks = text_splitter.split_documents(documents)
    logger.info("Total de chunks gerados para indexação: %d", len(chunks))
    return chunks

def vectorize_chunks(chunks):
    db = get_vector_db()
    # Limpa os documentos da coleção existente em vez de recriá-la, evitando segmentos órfãos no disco
    existing_ids = db.get(include=[])["ids"]
    if existing_ids:
        db.delete(ids=existing_ids)
    db.add_documents(chunks)
    logger.info("Banco vetorial ChromaDB indexado com sucesso em: %s", config.VECTOR_DB_DIR)

def run_ingestion():
    logger.info("Iniciando processo de ingestão RAG...")
    documents = load_documents()
    if not documents:
        logger.warning("Nenhum documento .md encontrado em data/raw/ para ingestão.")
        return

    chunks = split_chunks(documents)
    vectorize_chunks(chunks)
    logger.info("Ingestão concluída com sucesso!")

if __name__ == "__main__":
    from src.core.logging_config import setup_logging
    setup_logging()
    run_ingestion()
