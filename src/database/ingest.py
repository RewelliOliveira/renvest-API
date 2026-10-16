import bisect
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src import config
from src.database.pdf_extractor import ExtractedPage, extract_pdf
from src.database.retriever import get_embeddings
from src.repositories.chunk_repository import ChunkRepository

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf"}
METADATA_FIELDS = ("module", "institution", "url", "doc_type", "published")
INSERT_BATCH_SIZE = 100


def load_manifest(path: Path = config.MANIFEST_PATH) -> List[Dict[str, Any]]:
    """Lê o manifesto do corpus e valida que cada documento aponta para um módulo e um arquivo existentes."""
    with open(path, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f) or {}

    modules = set((manifest.get("modules") or {}).keys())
    entries = []
    for entry in manifest.get("documents") or []:
        file_path = config.RAW_DATA_DIR / entry["file"]
        if entry.get("module") not in modules:
            raise ValueError(f"Documento '{entry['id']}' usa módulo inexistente no manifesto: {entry.get('module')}")
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo do documento '{entry['id']}' não encontrado: {file_path}")
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Formato não suportado para '{entry['id']}': {file_path.suffix}")
        entries.append(entry)
    return entries


def find_unregistered_files(entries: List[Dict[str, Any]]) -> List[str]:
    """Arquivos de data/raw/ ausentes do manifesto, que por isso não serão indexados."""
    registered = {(config.RAW_DATA_DIR / entry["file"]).resolve() for entry in entries}
    return sorted(
        str(path.relative_to(config.RAW_DATA_DIR))
        for path in config.RAW_DATA_DIR.rglob("*")
        if path.is_file() and path.resolve() not in registered
    )


def join_pages(pages: List[ExtractedPage]) -> Tuple[str, List[int], List[int]]:
    """Concatena as páginas para que parágrafos que continuam na página seguinte não sejam cortados,
    guardando o offset de cada página para mapear cada chunk de volta à sua página."""
    parts, offsets, numbers = [], [], []
    position = 0
    for page in pages:
        offsets.append(position)
        numbers.append(page.number)
        parts.append(page.text)
        position += len(page.text) + 2
    return "\n\n".join(parts), offsets, numbers


def page_at(offset: int, page_offsets: List[int], page_numbers: List[int]) -> int:
    return page_numbers[bisect.bisect_right(page_offsets, offset) - 1]


def get_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
        add_start_index=True,
    )


def build_chunks(entry: Dict[str, Any], pages: List[ExtractedPage]) -> List[Document]:
    text, page_offsets, page_numbers = join_pages(pages)
    if not text:
        return []

    base_metadata = {key: str(entry[key]) for key in METADATA_FIELDS if entry.get(key) is not None}
    base_metadata.update(doc_id=entry["id"], document=entry["title"], source=entry["file"])

    chunks = []
    for index, piece in enumerate(get_splitter().create_documents([text])):
        start = piece.metadata["start_index"]
        page_start = page_at(start, page_offsets, page_numbers)
        page_end = page_at(start + len(piece.page_content) - 1, page_offsets, page_numbers)
        section = f"p. {page_start}" if page_start == page_end else f"p. {page_start}-{page_end}"
        chunks.append(Document(
            id=f"{entry['id']}:{index:05d}",
            page_content=piece.page_content,
            metadata={**base_metadata, "page_start": page_start, "page_end": page_end, "section": section},
        ))
    return chunks


def load_chunks(entries: List[Dict[str, Any]]) -> Tuple[List[Document], List[Dict[str, Any]]]:
    all_chunks: List[Document] = []
    report: List[Dict[str, Any]] = []
    for entry in entries:
        result = extract_pdf(config.RAW_DATA_DIR / entry["file"])
        chunks = build_chunks(entry, result.pages)
        all_chunks.extend(chunks)
        report.append({
            "id": entry["id"],
            "module": entry["module"],
            "total_pages": result.total_pages,
            "extracted_pages": len(result.pages),
            "empty_pages": result.empty_pages,
            "characters": sum(len(page.text) for page in result.pages),
            "chunks": len(chunks),
            "removed_margin_lines": result.removed_margin_lines,
        })
        logger.info(
            "%s: %d/%d páginas com texto, %d chunks (módulo=%s)",
            entry["id"], len(result.pages), result.total_pages, len(chunks), entry["module"],
        )
    return all_chunks, report


def vectorize_chunks(chunks: List[Document]) -> None:
    """Grava os chunks no Supabase (upsert pelo ID estável) e remove os que deixaram de existir no corpus."""
    embeddings = get_embeddings()
    for start in range(0, len(chunks), INSERT_BATCH_SIZE):
        batch = chunks[start:start + INSERT_BATCH_SIZE]
        vectors = embeddings.embed_documents([chunk.page_content for chunk in batch])
        ChunkRepository.upsert([
            {
                "id": chunk.id,
                "doc_id": chunk.metadata["doc_id"],
                "module": chunk.metadata["module"],
                "content": chunk.page_content,
                "metadata": chunk.metadata,
                "embedding": vector,
            }
            for chunk, vector in zip(batch, vectors)
        ])
        logger.info("Enviados %d/%d chunks ao Supabase", start + len(batch), len(chunks))

    stale_ids = ChunkRepository.list_ids() - {chunk.id for chunk in chunks}
    if stale_ids:
        ChunkRepository.delete_ids(stale_ids)
    logger.info("Banco vetorial atualizado: %d chunks gravados, %d removidos", len(chunks), len(stale_ids))


def write_report(report: List[Dict[str, Any]], unregistered: List[str], dry_run: bool) -> Path:
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = config.REPORTS_DIR / "ingest_report.json"
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dry_run": dry_run,
        "chunk_size": config.CHUNK_SIZE,
        "chunk_overlap": config.CHUNK_OVERLAP,
        "embedding_model": config.EMBEDDING_MODEL,
        "total_chunks": sum(item["chunks"] for item in report),
        "unregistered_files": unregistered,
        "documents": report,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def run_ingestion(dry_run: bool = False) -> None:
    """Extrai, segmenta e indexa o corpus do manifesto. Com dry_run, gera apenas o relatório (sem embeddings)."""
    logger.info("Iniciando processo de ingestão RAG...")
    entries = load_manifest()
    unregistered = find_unregistered_files(entries)
    for file_name in unregistered:
        logger.warning("Arquivo fora do manifesto (não será indexado): %s", file_name)

    chunks, report = load_chunks(entries)
    if not dry_run:
        vectorize_chunks(chunks)

    report_path = write_report(report, unregistered, dry_run)
    logger.info("Ingestão concluída: %d chunks. Relatório em %s", len(chunks), report_path)


if __name__ == "__main__":
    from src.core.logging_config import setup_logging
    setup_logging()
    run_ingestion()
