import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import fitz  # PyMuPDF

# Faixas da página (proporção da altura) tratadas como cabeçalho e rodapé
HEADER_ZONE = 0.18
FOOTER_ZONE = 0.90
# Bloco de margem só é removido se repetir em ao menos 5% das páginas (mínimo 3)
REPEAT_RATIO = 0.05
MIN_REPEAT_PAGES = 3
# Abaixo disso a página é tratada como sem texto (capas, imagens)
MIN_PAGE_CHARS = 30

HYPHEN_BREAK = re.compile(r"(\w)-\n(?=[a-zà-ÿ])")
WORD_HYPHEN_END = re.compile(r"\w-$")
SPACES = re.compile(r"[ \t\u00a0]+")
DIGITS = re.compile(r"\d+")
PAGE_NUMBER_ONLY = re.compile(r"^\W*#\W*$")


@dataclass
class ExtractedPage:
    number: int  # 1-based
    text: str


@dataclass
class ExtractionResult:
    pages: List[ExtractedPage]
    total_pages: int
    empty_pages: List[int] = field(default_factory=list)
    removed_margin_lines: List[str] = field(default_factory=list)


def _margin_key(text: str) -> str:
    """Números viram curinga para que "Página 3 de 37" e "Página 4 de 37" contem como repetição."""
    return DIGITS.sub("#", SPACES.sub(" ", text).strip().lower())


def clean_block(text: str) -> str:
    """Reconstrói o parágrafo de um bloco, desfazendo hifenização e quebras de linha no meio da frase."""
    text = unicodedata.normalize("NFKC", text).replace("\u00ad", "")
    text = HYPHEN_BREAK.sub(r"\1", text)
    paragraph = ""
    for line in (SPACES.sub(" ", line).strip() for line in text.splitlines()):
        if not line:
            continue
        # Hífen antes de maiúscula não é hifenização (ex: "Central-\nBCB"): mantém, sem espaço
        separator = "" if not paragraph or WORD_HYPHEN_END.search(paragraph) else " "
        paragraph += separator + line
    return paragraph


def extract_pdf(path: Path) -> ExtractionResult:
    with fitz.open(path) as pdf:
        raw_pages = []
        for page in pdf:
            height = page.rect.height or 1
            blocks = []
            for x0, y0, x1, y1, text, *_rest, block_type in page.get_text("blocks", sort=True):
                if block_type != 0 or not text.strip():
                    continue
                in_margin = y1 / height <= HEADER_ZONE or y0 / height >= FOOTER_ZONE
                blocks.append((text, in_margin))
            raw_pages.append(blocks)

    total_pages = len(raw_pages)
    margin_counts = Counter(
        key
        for blocks in raw_pages
        for key in {_margin_key(text) for text, in_margin in blocks if in_margin}
    )
    min_repeats = max(MIN_REPEAT_PAGES, int(total_pages * REPEAT_RATIO))
    repeated = {key for key, count in margin_counts.items() if count >= min_repeats}

    pages: List[ExtractedPage] = []
    empty_pages: List[int] = []
    for number, blocks in enumerate(raw_pages, start=1):
        paragraphs = []
        for text, in_margin in blocks:
            key = _margin_key(text)
            if in_margin and (key in repeated or PAGE_NUMBER_ONLY.match(key)):
                continue
            paragraph = clean_block(text)
            if paragraph:
                paragraphs.append(paragraph)
        page_text = "\n\n".join(paragraphs)
        if len(page_text) < MIN_PAGE_CHARS:
            empty_pages.append(number)
            continue
        pages.append(ExtractedPage(number=number, text=page_text))

    return ExtractionResult(
        pages=pages,
        total_pages=total_pages,
        empty_pages=empty_pages,
        removed_margin_lines=sorted(repeated),
    )
