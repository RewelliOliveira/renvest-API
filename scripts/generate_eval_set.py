"""Gera o conjunto de avaliação congelado (RAG × baseline) com as 12 perguntas do Apêndice A do TCC.

Para cada pergunta, grava a resposta do RAG (mesmo prompt do chat, sem histórico e sem nome de usuário),
os k trechos recuperados com fonte e distância, e a resposta baseline (mesmo modelo e temperatura, só a
persona do Rev, sem contexto recuperado), além das latências e do uso de tokens das duas condições.

Rode UMA única vez na Fase 1 e não edite nem regenere respostas individuais: elas são o dado da avaliação.

Uso (a partir de rag-finance-agent/):
    python scripts/generate_eval_set.py              # gera data/eval/eval_set_v1.json
    python scripts/generate_eval_set.py --dry-run    # só C1.1, imprime sem gravar
    python scripts/generate_eval_set.py --force      # sobrescreve um conjunto já gerado (registre o motivo)
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import config  # noqa: E402
from src.agents.assistant import build_context_instruction, format_context, generate, retrieve  # noqa: E402
from src.agents.prompts import REV_PERSONA_PROMPT  # noqa: E402
from src.tools.bcb_tools import get_selic_rate, mentions_selic  # noqa: E402

EVAL_DIR = config.DATA_DIR / "eval"
OUTPUT_PATH = EVAL_DIR / "eval_set_v1.json"

BASELINE_INSTRUCTION = (
    "Responda para um investidor iniciante e cite as fontes oficiais que sustentam sua resposta. "
    "É obrigatório indicar no texto a fonte de cada informação, no formato (Fonte: documento – instituição, página)."
)

QUESTIONS: List[Dict[str, str]] = [
    {"id": "C1.1", "categoria": "1", "modulo": "modulo_1",
     "pergunta": "O que é renda fixa e quais são os principais produtos dessa categoria disponíveis no mercado brasileiro?"},
    {"id": "C1.2", "categoria": "1", "modulo": "modulo_1",
     "pergunta": "O que é a taxa Selic e como ela influencia os rendimentos de investimentos em renda fixa?"},
    {"id": "C1.3", "categoria": "1", "modulo": "modulo_2",
     "pergunta": "O que é um ETF e como ele se diferencia de um fundo de investimento convencional?"},
    {"id": "C1.4", "categoria": "1", "modulo": "modulo_1",
     "pergunta": "O que é Tesouro Direto e como funciona a compra de títulos públicos por pessoas físicas?"},
    {"id": "C1.5", "categoria": "1", "modulo": "modulo_2",
     "pergunta": "O que é um Fundo Imobiliário (FII) e quais são suas principais características?"},
    {"id": "C1.6", "categoria": "1", "modulo": "modulo_1",
     "pergunta": "O que significa o FGC (Fundo Garantidor de Créditos) e quais produtos ele cobre?"},
    {"id": "C1.7", "categoria": "1", "modulo": "modulo_2",
     "pergunta": "O que é diversificação de portfólio e por que ela é importante para o investidor iniciante?"},
    {"id": "C2.1", "categoria": "2", "modulo": "modulo_3",
     "pergunta": "O que é a CVM e qual é o seu papel no mercado de capitais brasileiro?"},
    {"id": "C2.2", "categoria": "2", "modulo": "modulo_3",
     "pergunta": "O que é um Formulário de Referência e quais empresas são obrigadas a apresentá-lo?"},
    {"id": "C2.3", "categoria": "2", "modulo": "modulo_3",
     "pergunta": "O que significa uma companhia ser classificada como “aberta” segundo a regulamentação da CVM?"},
    {"id": "C2.4", "categoria": "2", "modulo": "modulo_3",
     "pergunta": "O que é um Fato Relevante e em quais situações uma empresa listada na B3 deve divulgá-lo?"},
    {"id": "C2.5", "categoria": "2", "modulo": "modulo_2",
     "pergunta": "O que é o Novo Mercado da B3 e o que diferencia esse segmento dos demais?"},
]


def elapsed_ms(started: float) -> float:
    return round((time.perf_counter() - started) * 1000, 1)


def git_state() -> Dict[str, Any]:
    def run(*args: str) -> Optional[str]:
        try:
            return subprocess.run(["git", *args], cwd=config.PROJECT_ROOT, capture_output=True, text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            return None

    status = run("status", "--porcelain")
    return {"commit": run("rev-parse", "HEAD"), "branch": run("rev-parse", "--abbrev-ref", "HEAD"), "dirty": bool(status)}


def run_rag(question: Dict[str, str]) -> Dict[str, Any]:
    started = time.perf_counter()
    docs = retrieve(question["pergunta"], module=question["modulo"])
    retrieval_ms = elapsed_ms(started)

    live_data = get_selic_rate() if mentions_selic(question["pergunta"]) else None
    instruction = build_context_instruction(format_context(docs), None, live_data)

    started = time.perf_counter()
    result = generate(question["pergunta"], instruction)
    generation_ms = elapsed_ms(started)

    trechos = [
        {
            "chunk_id": doc.id,
            "texto": doc.page_content,
            "documento": doc.metadata.get("document"),
            "instituicao": doc.metadata.get("institution"),
            "pagina": doc.metadata.get("section"),
            "url": doc.metadata.get("url"),
            "distancia": doc.metadata.get("distance"),
        }
        for doc in docs
    ]
    return {
        "resposta_rag": result["reply"],
        "contextos": [t["texto"] for t in trechos] + ([live_data] if live_data else []),
        "fontes": trechos,
        "distancias": [t["distancia"] for t in trechos],
        "dado_tempo_real": live_data,
        "rag_metricas": {
            "latencia_busca_ms": retrieval_ms,
            "latencia_geracao_ms": generation_ms,
            "latencia_total_ms": round(retrieval_ms + generation_ms, 1),
            "tokens_in": result["tokens_in"],
            "tokens_out": result["tokens_out"],
        },
    }


def run_baseline(question: Dict[str, str]) -> Dict[str, Any]:
    started = time.perf_counter()
    result = generate(question["pergunta"], BASELINE_INSTRUCTION, system_prompt=REV_PERSONA_PROMPT)
    generation_ms = elapsed_ms(started)
    return {
        "resposta_baseline": result["reply"],
        "baseline_metricas": {
            "latencia_geracao_ms": generation_ms,
            "tokens_in": result["tokens_in"],
            "tokens_out": result["tokens_out"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera o conjunto de avaliação congelado (RAG × baseline).")
    parser.add_argument("--dry-run", action="store_true", help="Roda só a C1.1 e imprime o resultado sem gravar")
    parser.add_argument("--force", action="store_true", help="Sobrescreve um conjunto já gerado")
    args = parser.parse_args()

    if not args.dry_run and OUTPUT_PATH.exists() and not args.force:
        sys.exit(f"{OUTPUT_PATH} já existe. O conjunto é congelado; use --force só em caso de bug técnico e registre o motivo.")

    questions = QUESTIONS[:1] if args.dry_run else QUESTIONS
    # Aquece os clientes (OpenAI, Supabase) para a 1ª pergunta não carregar o custo de inicialização
    retrieve("aquecimento", module=questions[0]["modulo"])
    items = []
    for question in questions:
        print(f"[{question['id']}] {question['pergunta']}")
        items.append({**question, **run_rag(question), **run_baseline(question)})

    payload = {
        "metadados": {
            "gerado_em": datetime.now(timezone.utc).isoformat(),
            "git": git_state(),
            "llm_model": config.LLM_MODEL,
            "llm_temperature": config.LLM_TEMPERATURE,
            "embedding_model": config.EMBEDDING_MODEL,
            "retrieval_k": config.RETRIEVAL_K,
            "retrieval_max_distance": config.RETRIEVAL_MAX_DISTANCE,
            "chunk_size": config.CHUNK_SIZE,
            "chunk_overlap": config.CHUNK_OVERLAP,
            "baseline_instruction": BASELINE_INSTRUCTION,
        },
        "itens": items,
    }

    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Conjunto gravado em {OUTPUT_PATH} ({len(items)} perguntas)")


if __name__ == "__main__":
    main()
