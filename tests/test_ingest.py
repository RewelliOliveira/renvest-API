import fitz
import pytest

from src import config
from src.database import ingest
from src.database.pdf_extractor import ExtractedPage, clean_block, extract_pdf

HEADER = "COMISSÃO DE VALORES MOBILIÁRIOS"


def make_pdf(path, bodies):
    """Gera um PDF com cabeçalho repetido, número de página no rodapé e o corpo informado em cada página."""
    pdf = fitz.open()
    for number, body in enumerate(bodies, start=1):
        page = pdf.new_page()
        page.insert_text((72, 40), HEADER)
        if body:
            page.insert_text((72, 300), body)
        page.insert_text((290, 820), str(number))
    pdf.save(path)
    pdf.close()


def test_clean_block_joins_hyphenation_and_line_breaks():
    assert clean_block("ao re-\ngulamento ou aos\natos normativos") == "ao regulamento ou aos atos normativos"
    assert clean_block("Banco Central-\nBCB") == "Banco Central-BCB"


def test_extract_pdf_removes_repeated_headers_and_page_numbers(tmp_path):
    path = tmp_path / "doc.pdf"
    make_pdf(path, [f"Art. {n}. Texto do artigo numero {n} da norma." for n in range(1, 5)] + [""])

    result = extract_pdf(path)

    assert result.total_pages == 5
    assert result.empty_pages == [5]
    assert [page.number for page in result.pages] == [1, 2, 3, 4]
    assert result.pages[0].text == "Art. 1. Texto do artigo numero 1 da norma."
    assert all(HEADER not in page.text for page in result.pages)


def test_build_chunks_tracks_pages_and_stable_ids(monkeypatch):
    monkeypatch.setattr(config, "CHUNK_SIZE", 60)
    monkeypatch.setattr(config, "CHUNK_OVERLAP", 0)
    entry = {
        "id": "cvm_res_44",
        "file": "modulo_3_cvm/res44.pdf",
        "title": "Resolução CVM nº 44",
        "institution": "CVM",
        "url": "https://www.gov.br/cvm",
        "module": "modulo_3",
        "doc_type": "normativo",
    }
    pages = [
        ExtractedPage(number=2, text="Primeiro parágrafo da página dois com texto suficiente."),
        ExtractedPage(number=3, text="Segundo parágrafo, agora na página três do documento."),
    ]

    chunks = ingest.build_chunks(entry, pages)

    assert [chunk.id for chunk in chunks] == ["cvm_res_44:00000", "cvm_res_44:00001"]
    assert [chunk.metadata["section"] for chunk in chunks] == ["p. 2", "p. 3"]
    assert chunks[0].metadata["document"] == "Resolução CVM nº 44"
    assert chunks[0].metadata["module"] == "modulo_3"
    assert "published" not in chunks[0].metadata


def test_load_manifest_rejects_unknown_module(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "RAW_DATA_DIR", tmp_path)
    make_pdf(tmp_path / "a.pdf", ["Texto"])
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text(
        "modules: {modulo_1: {folder: x, title: y}}\n"
        "documents:\n  - {id: a, file: a.pdf, title: A, module: modulo_9}\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="modulo_9"):
        ingest.load_manifest(manifest)


def test_project_manifest_points_to_existing_files():
    entries = ingest.load_manifest()
    assert entries
    assert ingest.find_unregistered_files(entries) == []
