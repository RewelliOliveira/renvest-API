"""Gera o conjunto de avaliação congelado (assistente × B1) com as 16 perguntas de data/eval/questions_v2.yaml.

Para cada pergunta, grava a resposta do assistente (mesmo prompt do chat, sem histórico e sem nome de usuário),
os k trechos recuperados com fonte e distância, e a resposta da condição B1 (mesmo modelo e temperatura, só a
persona do Rev, sem trechos recuperados e sem as regras de ancoragem), além das latências e do uso de tokens
das duas condições. Cada item leva também a resposta de referência, usada pelas métricas do RAGAS.

Rode UMA única vez, a partir da versão marcada com a tag de congelamento, e não edite nem regenere respostas
individuais: elas são o dado da avaliação. O script recusa rodar com referências ainda não validadas pelos
especialistas ou com alterações não commitadas, salvo com --allow-unvalidated / --allow-dirty.

Uso (a partir de rag-finance-agent/):
    python scripts/generate_eval_set.py              # gera data/eval/eval_set_v2.json
    python scripts/generate_eval_set.py --dry-run    # só a primeira pergunta, imprime sem gravar
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

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import config  # noqa: E402
from src.agents.assistant import build_context_instruction, format_context, generate, retrieve  # noqa: E402
from src.agents.prompts import REV_PERSONA_PROMPT  # noqa: E402
from src.tools.bcb_tools import get_selic_rate, mentions_selic  # noqa: E402

EVAL_DIR = config.DATA_DIR / "eval"
QUESTIONS_PATH = EVAL_DIR / "questions_v2.yaml"
OUTPUT_PATH = EVAL_DIR / "eval_set_v2.json"

# Condição B1 (Seção 4.7.1 do TCC): sem trechos e sem regras de ancoragem, só a instrução de citar fontes quando possível
BASELINE_INSTRUCTION = (
    "Responda para um investidor iniciante e, quando possível, cite as fontes oficiais que sustentam sua resposta."
)


def load_questions() -> List[Dict[str, Any]]:
    questions = yaml.safe_load(QUESTIONS_PATH.read_text(encoding="utf-8"))
    return [
        {
            "id": q["id"],
            "nivel": q["nivel"],
            "modulo": q.get("modulo"),
            "pergunta": q["pergunta"],
            "comportamento_esperado": q["comportamento_esperado"],
            "referencia": q.get("referencia"),
            "fontes_referencia": q.get("fontes_referencia", []),
            "validado": bool(q.get("validado")),
        }
        for q in questions
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
        # Se o chat exibiria as fontes ao usuário (resposta classificada como baseada nos trechos)
        "usou_base": bool(docs) and result.get("used_base_sources", True),
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
    parser.add_argument("--dry-run", action="store_true", help="Roda só a primeira pergunta e imprime o resultado sem gravar")
    parser.add_argument("--force", action="store_true", help="Sobrescreve um conjunto já gerado")
    parser.add_argument("--allow-unvalidated", action="store_true", help="Roda mesmo com referências não validadas")
    parser.add_argument("--allow-dirty", action="store_true", help="Roda mesmo com alterações não commitadas")
    args = parser.parse_args()

    if not args.dry_run and OUTPUT_PATH.exists() and not args.force:
        sys.exit(f"{OUTPUT_PATH} já existe. O conjunto é congelado; use --force só em caso de bug técnico e registre o motivo.")

    all_questions = load_questions()
    if not args.dry_run:
        pending = [q["id"] for q in all_questions if not q["validado"]]
        if pending and not args.allow_unvalidated:
            sys.exit(f"Referências ainda não validadas pelos especialistas: {', '.join(pending)}.")
        if git_state()["dirty"] and not args.allow_dirty:
            sys.exit("Há alterações não commitadas: o conjunto deve sair da versão marcada com a tag de congelamento.")

    questions = all_questions[:1] if args.dry_run else all_questions
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
