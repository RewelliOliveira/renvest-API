"""Avaliação automatizada do conjunto congelado com RAGAS (PLANO_AVALIACAO.md, Seção 5; TCC, Seção 4.7.2).

Lê data/eval/eval_set_v2.json e calcula, por pergunta e por condição:
  RAG: Faithfulness, ResponseRelevancy, LLMContextPrecisionWithReference, LLMContextRecall, FactualCorrectness
  B1 : ResponseRelevancy, FactualCorrectness   (sem contexto recuperado)
Juiz: gpt-4o, temperatura 0 (diferente do gerador gpt-4o-mini). Embeddings: text-embedding-3-small.
Prompts das métricas adaptados para o português e guardados em data/eval/ragas_prompts_pt/ para reuso.
A N4.2 (fora da base de propósito) fica de fora: é avaliada só pelos especialistas e pelo comportamento esperado.

Saídas (data/eval/):
  ragas_v2.csv          formato longo: execucao, id, nivel, condicao, metrica, valor
  ragas_v2_resumo.csv   média e desvio-padrão por nível × condição × métrica (média das execuções por pergunta)
  ragas_v2_meta.json    versões, juiz, data, execuções, falhas (NaN) e diferença entre execuções

Uso (no ambiente separado, ver requirements-eval.txt):
  python scripts/run_ragas.py --limit 2 --runs 1     # teste rápido -> ragas_v2_teste.*
  python scripts/run_ragas.py                        # avaliação completa, 2 execuções
"""
from __future__ import annotations

import argparse
import asyncio
import json
import math
import platform
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "data" / "eval"
SRC = EVAL / "eval_set_v2.json"
PROMPTS_DIR = EVAL / "ragas_prompts_pt"
EXCLUDE_DEFAULT = ("N4.2",)

RAG_METRICS = ("Faithfulness", "ResponseRelevancy", "LLMContextPrecisionWithReference", "LLMContextRecall", "FactualCorrectness")
B1_METRICS = ("ResponseRelevancy", "FactualCorrectness")


# ---------------------------------------------------------------- dados (sem dependência do ragas)
def load_eval_set(path: Path = SRC) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_rows(itens: list[dict], exclude=EXCLUDE_DEFAULT, limit: int | None = None) -> dict[str, list[dict]]:
    """Monta as amostras por condição. RAG leva os trechos recuperados; B1 não tem contexto."""
    sel = [it for it in itens if it["id"] not in set(exclude)]
    if limit:
        sel = sel[:limit]
    rag, b1 = [], []
    for it in sel:
        contexts = list(it.get("contextos") or [])
        if it.get("dado_tempo_real"):
            contexts.append(str(it["dado_tempo_real"]))
        base = {"id": it["id"], "nivel": it["nivel"], "user_input": it["pergunta"], "reference": it["referencia"]}
        rag.append({**base, "response": it["resposta_rag"], "retrieved_contexts": contexts})
        b1.append({**base, "response": it["resposta_baseline"], "retrieved_contexts": None})
    return {"RAG": rag, "B1": b1}


def summarize(long_rows: list[dict]) -> tuple[list[dict], dict]:
    """Média por pergunta entre execuções; depois média e DP por nível × condição × métrica (e 'Todos')."""
    per_q: dict[tuple, list[float]] = {}
    for r in long_rows:
        if r["valor"] is None or (isinstance(r["valor"], float) and math.isnan(r["valor"])):
            continue
        per_q.setdefault((r["condicao"], r["metrica"], r["nivel"], r["id"]), []).append(r["valor"])
    q_mean = {k: statistics.fmean(v) for k, v in per_q.items()}
    groups: dict[tuple, list[float]] = {}
    for (cond, met, nivel, _qid), v in q_mean.items():
        groups.setdefault((cond, met, nivel), []).append(v)
        groups.setdefault((cond, met, "Todos"), []).append(v)
    resumo = []
    for (cond, met, nivel), vals in sorted(groups.items()):
        resumo.append({"condicao": cond, "metrica": met, "nivel": nivel, "n": len(vals),
                       "media": round(statistics.fmean(vals), 4),
                       "dp": round(statistics.stdev(vals), 4) if len(vals) > 1 else 0.0})
    # estabilidade: diferença absoluta média entre execuções, por métrica
    estab = {}
    for (cond, met, _n, _q), v in per_q.items():
        if len(v) > 1:
            estab.setdefault(f"{cond}/{met}", []).append(max(v) - min(v))
    estab = {k: round(statistics.fmean(v), 4) for k, v in estab.items()}
    return resumo, estab


# ---------------------------------------------------------------- ragas
def make_metrics(names, llm, emb):
    from ragas.metrics import (FactualCorrectness, Faithfulness, LLMContextPrecisionWithReference,
                               LLMContextRecall, ResponseRelevancy)
    cls = {"Faithfulness": Faithfulness, "ResponseRelevancy": ResponseRelevancy,
           "LLMContextPrecisionWithReference": LLMContextPrecisionWithReference,
           "LLMContextRecall": LLMContextRecall, "FactualCorrectness": FactualCorrectness}
    out = {}
    for n in names:
        m = cls[n]()
        m.llm = llm
        if n == "ResponseRelevancy":
            m.embeddings = emb
        out[n] = m
    return out


async def adapt_prompts(metrics: dict, llm, enabled: bool) -> dict:
    status = {}
    for name, m in metrics.items():
        if not enabled:
            status[name] = "inglês (adaptação desligada)"
            continue
        d = PROMPTS_DIR / name
        try:
            if d.exists() and any(d.iterdir()):
                m.load_prompts(str(d), language="portuguese")
                status[name] = "português (reaproveitado)"
                continue
            adapted = await m.adapt_prompts(language="portuguese", llm=llm)
            m.set_prompts(**adapted)
            d.mkdir(parents=True, exist_ok=True)
            m.save_prompts(str(d))
            status[name] = "português (adaptado agora)"
        except Exception as e:  # noqa: BLE001
            status[name] = f"inglês (falha na adaptação: {type(e).__name__}: {e})"
            print(f"Aviso: prompts de {name} ficaram em inglês: {e}", file=sys.stderr)
    return status


def run_once(rows: list[dict], metrics: dict, run_config) -> list[dict]:
    from ragas import evaluate
    from ragas.dataset_schema import EvaluationDataset, SingleTurnSample

    samples = []
    for r in rows:
        kw = {"user_input": r["user_input"], "response": r["response"], "reference": r["reference"]}
        if r["retrieved_contexts"] is not None:
            kw["retrieved_contexts"] = r["retrieved_contexts"]
        samples.append(SingleTurnSample(**kw))
    res = evaluate(dataset=EvaluationDataset(samples=samples), metrics=list(metrics.values()),
                   run_config=run_config, raise_exceptions=False, show_progress=True)
    df = res.to_pandas()
    out = []
    for i, r in enumerate(rows):
        for name, m in metrics.items():
            col = m.name if m.name in df.columns else next(c for c in df.columns if c.startswith(m.name.split("(")[0]))
            v = df.iloc[i][col]
            out.append({"id": r["id"], "nivel": r["nivel"], "metrica": name,
                        "valor": None if v is None or (isinstance(v, float) and math.isnan(v)) else float(v)})
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=int, default=2, help="número de execuções (padrão: 2)")
    ap.add_argument("--judge", default="gpt-4o", help="modelo juiz (padrão: gpt-4o)")
    ap.add_argument("--embeddings", default="text-embedding-3-small")
    ap.add_argument("--limit", type=int, help="só as N primeiras perguntas (teste rápido; grava ragas_v2_teste.*)")
    ap.add_argument("--no-adapt", action="store_true", help="não adaptar os prompts para o português")
    ap.add_argument("--force", action="store_true", help="sobrescreve resultados completos já gravados")
    args = ap.parse_args()

    suffix = "_teste" if args.limit else ""
    out_csv, out_res, out_meta = (EVAL / f"ragas_v2{suffix}.csv", EVAL / f"ragas_v2{suffix}_resumo.csv",
                                  EVAL / f"ragas_v2{suffix}_meta.json")
    if out_csv.exists() and not args.limit and not args.force:
        sys.exit(f"{out_csv.name} já existe. Use --force para refazer e registre o motivo.")

    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    import pandas as pd
    import ragas
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from ragas.llms import LangchainLLMWrapper
    from ragas.run_config import RunConfig

    data = load_eval_set()
    rows = build_rows(data["itens"], limit=args.limit)
    llm = LangchainLLMWrapper(ChatOpenAI(model=args.judge, temperature=0))
    emb = LangchainEmbeddingsWrapper(OpenAIEmbeddings(model=args.embeddings))
    run_config = RunConfig(timeout=180, max_retries=10, max_wait=60, max_workers=4)

    metric_sets = {"RAG": make_metrics(RAG_METRICS, llm, emb), "B1": make_metrics(B1_METRICS, llm, emb)}
    prompt_status = {}
    for cond, ms in metric_sets.items():
        prompt_status[cond] = asyncio.run(adapt_prompts(ms, llm, not args.no_adapt))

    long_rows = []
    for run in range(1, args.runs + 1):
        for cond, ms in metric_sets.items():
            print(f"\nExecução {run}/{args.runs} · {cond} · {len(rows[cond])} perguntas · {len(ms)} métricas")
            for r in run_once(rows[cond], ms, run_config):
                long_rows.append({"execucao": run, "condicao": cond, **r})

    pd.DataFrame(long_rows, columns=["execucao", "id", "nivel", "condicao", "metrica", "valor"]).to_csv(
        out_csv, index=False, encoding="utf-8")
    resumo, estab = summarize(long_rows)
    pd.DataFrame(resumo).to_csv(out_res, index=False, encoding="utf-8")
    falhas = [f'{r["execucao"]}/{r["condicao"]}/{r["id"]}/{r["metrica"]}' for r in long_rows if r["valor"] is None]
    meta = {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "ragas_version": ragas.__version__,
        "python": sys.version.split()[0], "plataforma": platform.platform(),
        "juiz": args.judge, "juiz_temperatura": 0, "embeddings": args.embeddings,
        "execucoes": args.runs, "excluidas": list(EXCLUDE_DEFAULT),
        "perguntas": len(rows["RAG"]), "limit": args.limit,
        "conjunto": {"arquivo": SRC.name, **{k: data["metadados"].get(k) for k in ("gerado_em", "git", "llm_model")}},
        "prompts": prompt_status,
        "falhas_nan": falhas,
        "diferenca_media_entre_execucoes": estab,
    }
    out_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\nResumo (todas as perguntas):")
    for r in resumo:
        if r["nivel"] == "Todos":
            print(f'  {r["condicao"]:<3} {r["metrica"]:<34} {r["media"]:.3f} ± {r["dp"]:.3f} (n = {r["n"]})')
    print(f"\nFalhas (NaN): {len(falhas)}")
    print(f"Gravado: {out_csv.name}, {out_res.name}, {out_meta.name}")


if __name__ == "__main__":
    main()
