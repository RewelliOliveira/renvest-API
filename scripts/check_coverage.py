"""Checa se o corpus cobre cada pergunta candidata da avaliação v2 (PLANO_AVALIACAO.md, Seção 3.3).

Para cada pergunta de data/eval/questions_candidates.yaml, busca os top-5 trechos (sem o limiar de
distância, para mostrar também o que ficou de fora) e imprime documento, página, distância e o começo do
texto. Os trechos que o chat realmente usaria (top-k do chat, RETRIEVAL_K, com distância <= RETRIEVAL_MAX_DISTANCE) aparecem marcados com "*".

A checagem automática só olha documento e distância. Se o trecho CONTÉM a informação é você quem confere,
lendo o relatório gerado em data/eval/coverage_v2.md.

Uso (a partir de rag-finance-agent/):
    python scripts/check_coverage.py              # todas as perguntas
    python scripts/check_coverage.py N2.1 N4.2    # só as indicadas
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import config  # noqa: E402
from src.database.retriever import get_embeddings  # noqa: E402
from src.repositories.chunk_repository import ChunkRepository  # noqa: E402

EVAL_DIR = config.DATA_DIR / "eval"
CANDIDATES_PATH = EVAL_DIR / "questions_candidates.yaml"
REPORT_PATH = EVAL_DIR / "coverage_v2.md"
TOP_N = 5
PREVIEW_CHARS = 300


def search(question: Dict[str, Any]) -> List[Dict[str, Any]]:
    embedding = get_embeddings().embed_query(question["pergunta"])
    rows = ChunkRepository.match(embedding, match_count=TOP_N, module=question.get("modulo"))
    hits = []
    for rank, row in enumerate(rows, start=1):
        metadata = row.get("metadata") or {}
        distance = row["distance"]
        hits.append({
            "rank": rank,
            "doc_id": metadata.get("doc_id") or row.get("doc_id"),
            "pagina": metadata.get("section", "?"),
            "distancia": distance,
            "usado_no_chat": rank <= config.RETRIEVAL_K and distance <= config.RETRIEVAL_MAX_DISTANCE,
            "texto": " ".join(row["content"].split()),
        })
    return hits


def verdict(question: Dict[str, Any], hits: List[Dict[str, Any]]) -> str:
    expected = set(question.get("documentos_esperados") or [])
    within = [h for h in hits if h["distancia"] <= config.RETRIEVAL_MAX_DISTANCE]
    used = [h for h in hits if h["usado_no_chat"]]

    if question["comportamento_esperado"] == "declarar_fora_da_base":
        if not used:
            return "OK: nenhum trecho passaria para o chat"
        return f"ATENÇÃO: {len(used)} trecho(s) passariam para o chat; confira se são pertinentes"

    if any(h["doc_id"] in expected for h in used):
        return f"PROVÁVEL: documento esperado no top-{config.RETRIEVAL_K} do chat; confira o texto"
    if any(h["doc_id"] in expected for h in within):
        return f"PARCIAL: documento esperado só no top-{TOP_N} (fora do top-{config.RETRIEVAL_K} do chat)"
    return "FALHOU: documento esperado não aparece com distância <= limiar; trocar ou reformular"


def render(question: Dict[str, Any], hits: List[Dict[str, Any]], result: str) -> str:
    modulo = question.get("modulo") or "sem filtro"
    esperados = ", ".join(question.get("documentos_esperados") or []) or "nenhum (ausência intencional)"
    lines = [
        f"## {question['id']} ({question['nivel']}, {modulo})",
        "",
        f"**Pergunta:** {question['pergunta']}",
        "",
        f"**Esperado:** {question['comportamento_esperado']} · documentos: {esperados}",
    ]
    if question.get("nota"):
        lines.append(f"\n**Nota:** {question['nota']}")
    lines += ["", f"**Resultado automático:** {result}", "", "**Conferência manual:** [ ] contém a informação  ", "", "| # | Documento | Página | Distância | Chat |", "| :-: | :-- | :-- | :-: | :-: |"]
    for h in hits:
        mark = "*" if h["usado_no_chat"] else ""
        flag = " ✓" if h["doc_id"] in (question.get("documentos_esperados") or []) else ""
        lines.append(f"| {h['rank']} | {h['doc_id']}{flag} | {h['pagina']} | {h['distancia']:.3f} | {mark} |")
    lines.append("")
    for h in hits:
        lines.append(f"> **{h['rank']}.** {h['texto'][:PREVIEW_CHARS]}…\n")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Checa a cobertura do corpus para as perguntas candidatas v2.")
    parser.add_argument("ids", nargs="*", help="IDs das perguntas (padrão: todas)")
    args = parser.parse_args()

    questions = yaml.safe_load(CANDIDATES_PATH.read_text(encoding="utf-8"))
    if args.ids:
        questions = [q for q in questions if q["id"] in set(args.ids)]
        if not questions:
            sys.exit(f"Nenhuma pergunta encontrada para: {', '.join(args.ids)}")

    sections, summary = [], []
    for question in questions:
        hits = search(question)
        result = verdict(question, hits)
        summary.append((question["id"], result))
        sections.append(render(question, hits, result))
        print(f"{question['id']:<5} {result}")
        for h in hits:
            mark = "*" if h["usado_no_chat"] else " "
            print(f"   {mark}{h['rank']} {h['distancia']:.3f}  {h['doc_id']} ({h['pagina']})")

    header = [
        "# Checagem de cobertura – avaliação v2",
        "",
        f"Gerado em {datetime.now():%d/%m/%Y %H:%M} · top-{TOP_N} · k do chat = {config.RETRIEVAL_K} · "
        f"limiar = {config.RETRIEVAL_MAX_DISTANCE} · embedding = {config.EMBEDDING_MODEL}",
        "",
        "`*` = trecho que o chat usaria (top-k dentro do limiar) · `✓` = documento esperado",
        "",
        "| ID | Resultado automático |",
        "| :-- | :-- |",
        *[f"| {qid} | {result} |" for qid, result in summary],
        "",
    ]
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(header + sections), encoding="utf-8")
    print(f"\nRelatório: {REPORT_PATH}")


if __name__ == "__main__":
    main()
