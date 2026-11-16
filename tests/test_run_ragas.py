"""Testes do preparo de dados do run_ragas.py (não chamam o RAGAS nem a OpenAI)."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("run_ragas", ROOT / "scripts" / "run_ragas.py")
run_ragas = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_ragas)


def _itens():
    return [
        {"id": "N1.1", "nivel": "N1", "pergunta": "p1", "referencia": "r1", "resposta_rag": "a", "resposta_baseline": "b",
         "contextos": ["c1", "c2"], "dado_tempo_real": None},
        {"id": "N4.2", "nivel": "N4", "pergunta": "p2", "referencia": "r2", "resposta_rag": "a", "resposta_baseline": "b",
         "contextos": ["c"], "dado_tempo_real": None},
        {"id": "N2.1", "nivel": "N2", "pergunta": "p3", "referencia": "r3", "resposta_rag": "a", "resposta_baseline": "b",
         "contextos": [], "dado_tempo_real": "Selic: 15%"},
    ]


def test_build_rows_excludes_n42_and_separates_conditions():
    rows = run_ragas.build_rows(_itens())
    assert [r["id"] for r in rows["RAG"]] == ["N1.1", "N2.1"]
    assert rows["RAG"][0]["retrieved_contexts"] == ["c1", "c2"]
    assert rows["RAG"][1]["retrieved_contexts"] == ["Selic: 15%"]
    assert all(r["retrieved_contexts"] is None for r in rows["B1"])
    assert rows["B1"][0]["response"] == "b" and rows["RAG"][0]["response"] == "a"


def test_build_rows_limit():
    assert len(run_ragas.build_rows(_itens(), limit=1)["RAG"]) == 1


def test_summarize_means_runs_then_questions():
    long = [
        {"execucao": 1, "condicao": "RAG", "id": "N1.1", "nivel": "N1", "metrica": "Faithfulness", "valor": 0.8},
        {"execucao": 2, "condicao": "RAG", "id": "N1.1", "nivel": "N1", "metrica": "Faithfulness", "valor": 1.0},
        {"execucao": 1, "condicao": "RAG", "id": "N2.1", "nivel": "N2", "metrica": "Faithfulness", "valor": 0.5},
        {"execucao": 2, "condicao": "RAG", "id": "N2.1", "nivel": "N2", "metrica": "Faithfulness", "valor": None},
    ]
    resumo, estab = run_ragas.summarize(long)
    todos = next(r for r in resumo if r["nivel"] == "Todos")
    assert todos["n"] == 2 and abs(todos["media"] - 0.7) < 1e-9
    assert abs(estab["RAG/Faithfulness"] - 0.2) < 1e-9


def test_real_eval_set_shape():
    data = run_ragas.load_eval_set()
    rows = run_ragas.build_rows(data["itens"])
    assert len(rows["RAG"]) == len(rows["B1"]) == 15
    assert all(r["retrieved_contexts"] for r in rows["RAG"])
