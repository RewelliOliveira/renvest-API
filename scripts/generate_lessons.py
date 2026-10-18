"""Gera rascunhos das lições e dos testes finais a partir do corpus indexado (RAG).

Para cada lição, recupera no Supabase trechos dos documentos oficiais da lição e pede ao LLM slides,
sugestões de pergunta e um quiz, cada item ancorado em um trecho citado (documento e página).
O resultado vai para src/content/modules/<modulo>.json e DEVE ser revisado antes de publicar.

Uso (a partir de rag-finance-agent/):
    python scripts/generate_lessons.py                     # gera os módulos que ainda não existem
    python scripts/generate_lessons.py --module modulo_2   # apenas um módulo
    python scripts/generate_lessons.py --force             # sobrescreve conteúdo já revisado
"""
import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain_openai import ChatOpenAI  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from src import config  # noqa: E402
from src.content.curriculum import MODULES_DIR, Module  # noqa: E402
from src.database.retriever import get_embeddings  # noqa: E402
from src.repositories.chunk_repository import ChunkRepository  # noqa: E402

EXCERPTS_PER_QUERY = 4
MAX_EXCERPTS = 8
EXAM_BANK_SIZE = 8
EXAM_QUESTION_COUNT = 5
EXAM_PASS_SCORE = 0.7
OPTION_IDS = "abcd"

CURRICULUM: List[Dict[str, Any]] = [
    {
        "id": "modulo_1",
        "title": "Fundamentos",
        "subtitle": "Orçamento, renda fixa e proteção do seu dinheiro",
        "description": "Organize suas finanças, entenda a renda fixa e saiba como seu dinheiro é protegido.",
        "color": "#f05656",
        "lessons": [
            {
                "title": "Orçamento e controle de gastos",
                "subtitle": "Organize as finanças antes de investir",
                "description": "Como mapear receitas e despesas, sair das dívidas e separar uma parte da renda para o futuro.",
                "docs": ["bcb_caderno_gestao_financas_pessoais", "cvm_livro_top_planejamento_financeiro_pessoal"],
                "queries": ["orçamento pessoal receitas e despesas controle de gastos", "como sair das dívidas e poupar parte da renda"],
            },
            {
                "title": "Renda fixa e reserva de emergência",
                "subtitle": "Selic, CDI, poupança e CDB",
                "description": "O que é renda fixa, como a Selic influencia os rendimentos e onde guardar a reserva de emergência.",
                "docs": ["cvm_livro_top_planejamento_financeiro_pessoal", "bcb_caderno_gestao_financas_pessoais"],
                "queries": ["o que é renda fixa títulos CDB poupança", "taxa Selic e CDI influência nos rendimentos", "reserva de emergência liquidez"],
            },
            {
                "title": "Tesouro Direto",
                "subtitle": "Emprestando dinheiro para o governo",
                "description": "Como funciona a compra de títulos públicos por pessoas físicas e os tipos de título disponíveis.",
                "docs": ["tesouro_direto_regulamento", "cvm_livro_top_planejamento_financeiro_pessoal"],
                "queries": ["o que é o Tesouro Direto e como comprar títulos públicos", "Tesouro Selic, Prefixado e IPCA+"],
            },
            {
                "title": "FGC: a proteção do seu dinheiro",
                "subtitle": "Limites e produtos cobertos",
                "description": "O que é o Fundo Garantidor de Créditos, quanto ele garante e quais investimentos ficam de fora.",
                "docs": ["cmn_resolucao_4222_fgc", "cvm_livro_top_planejamento_financeiro_pessoal"],
                "queries": ["garantia do FGC limite por CPF e instituição", "quais investimentos são cobertos pelo FGC"],
            },
        ],
    },
    {
        "id": "modulo_2",
        "title": "A Bolsa de Valores",
        "subtitle": "Ações, fundos, ETFs e governança na B3",
        "description": "Entenda como funciona a bolsa, os principais produtos e como escolher empresas com boa governança.",
        "color": "#0052d7",
        "lessons": [
            {
                "title": "Bolsa de valores e ações",
                "subtitle": "Tornando-se sócio de uma empresa",
                "description": "O que é a B3, o que representa uma ação e quais direitos ela dá ao acionista.",
                "docs": ["cvm_livro_top_mercado_valores_mobiliarios"],
                "queries": ["o que é uma ação e direitos do acionista", "ações ordinárias e preferenciais dividendos", "o que é a B3 bolsa de valores"],
            },
            {
                "title": "Fundos de investimento e ETFs",
                "subtitle": "Investindo em conjunto",
                "description": "Como funcionam os fundos de investimento e os fundos de índice (ETFs) negociados em bolsa.",
                "docs": ["cvm_caderno_03_fundos_investimento", "cvm_livro_top_mercado_valores_mobiliarios"],
                "queries": ["o que é um fundo de investimento cotas administrador gestor", "fundo de índice ETF negociado em bolsa"],
            },
            {
                "title": "Fundos imobiliários (FII)",
                "subtitle": "Imóveis na bolsa",
                "description": "O que são os fundos imobiliários, como geram rendimentos e quais são seus riscos.",
                "docs": ["cvm_caderno_06_fundos_imobiliarios", "cvm_livro_top_mercado_valores_mobiliarios"],
                "queries": ["o que é um fundo de investimento imobiliário", "rendimentos e riscos dos FII negociação de cotas"],
            },
            {
                "title": "Novo Mercado e diversificação",
                "subtitle": "Governança e redução de risco",
                "description": "O que diferencia o Novo Mercado da B3 e por que diversificar reduz o risco da carteira.",
                "docs": ["b3_regulamento_novo_mercado", "cvm_livro_top_mercado_valores_mobiliarios"],
                "queries": ["Novo Mercado segmento de governança corporativa B3 exigências", "diversificação de investimentos e redução de risco"],
            },
        ],
    },
    {
        "id": "modulo_3",
        "title": "CVM e Regulação",
        "subtitle": "Quem fiscaliza o mercado e como ler as empresas",
        "description": "Conheça a CVM e aprenda a usar os documentos oficiais das empresas para investir com autonomia.",
        "color": "#8b5cf6",
        "lessons": [
            {
                "title": "O que é a CVM",
                "subtitle": "O xerife do mercado de capitais",
                "description": "O papel da Comissão de Valores Mobiliários na regulação e na proteção do investidor.",
                "docs": ["cvm_caderno_01_o_que_e_a_cvm", "cvm_livro_top_direito_mercado_valores_mobiliarios"],
                "queries": ["o que é a CVM e qual seu papel no mercado de capitais", "como a CVM protege o investidor fiscalização"],
            },
            {
                "title": "Companhia aberta",
                "subtitle": "Registro de emissores na CVM",
                "description": "O que significa uma empresa ser companhia aberta e quais obrigações ela assume.",
                "docs": ["cvm_resolucao_80_2022", "cvm_caderno_01_o_que_e_a_cvm", "cvm_livro_top_direito_mercado_valores_mobiliarios"],
                "queries": ["o que é uma companhia aberta registro de emissor na CVM", "categorias A e B de registro de emissor"],
            },
            {
                "title": "Formulário de Referência",
                "subtitle": "O raio-x oficial da empresa",
                "description": "O que é o Formulário de Referência, quem deve apresentá-lo e que informações ele traz.",
                "docs": ["cvm_resolucao_80_2022", "cvm_livro_top_direito_mercado_valores_mobiliarios"],
                "queries": ["o que é o formulário de referência e quem deve apresentar", "informações do formulário de referência fatores de risco administradores"],
            },
            {
                "title": "Fato Relevante",
                "subtitle": "Transparência imediata",
                "description": "O que é um Fato Relevante e em quais situações a empresa é obrigada a divulgá-lo.",
                "docs": ["cvm_resolucao_44_2021"],
                "queries": ["o que é fato relevante e quando deve ser divulgado", "dever de divulgação e sigilo de informações relevantes"],
            },
        ],
    },
]

SYSTEM_PROMPT = """Você é um especialista em educação financeira criando material didático para investidores iniciantes brasileiros.
Use EXCLUSIVAMENTE as informações dos trechos oficiais fornecidos, numerados como [1], [2], ...
Regras:
- Linguagem simples, acolhedora e sem jargão não explicado; o leitor nunca investiu.
- Nunca invente números, prazos, percentuais ou regras que não estejam nos trechos.
- Cada item deve indicar em source_index o número do trecho que o fundamenta.
- Nas questões: exatamente 4 alternativas, apenas UMA correta, alternativas erradas plausíveis e do mesmo tamanho aproximado.
- Não recomende compra de ativos específicos."""


class DraftSlide(BaseModel):
    title: str = Field(description="Título curto do slide (até 40 caracteres)")
    text: str = Field(description="Explicação do mascote Rev, 2 a 3 frases, no máximo 320 caracteres")
    source_index: int


class DraftQuestion(BaseModel):
    question: str
    options: List[str] = Field(description="Exatamente 4 alternativas")
    correct_index: int = Field(description="Índice (0 a 3) da alternativa correta")
    explanation: str = Field(description="Por que a resposta correta está certa, 1 a 2 frases")
    source_index: int


class LessonDraft(BaseModel):
    slides: List[DraftSlide] = Field(description="Exatamente 3 slides, do conceito básico ao mais específico")
    chat_suggestions: List[str] = Field(description="4 perguntas curtas (até 45 caracteres) que o aluno poderia fazer")
    quiz: List[DraftQuestion] = Field(description="Exatamente 3 questões de fixação")


class ExamDraft(BaseModel):
    questions: List[DraftQuestion] = Field(description=f"Exatamente {EXAM_BANK_SIZE} questões, cobrindo todas as lições")


def retrieve_excerpts(module_id: str, docs: List[str], queries: List[str]) -> List[Dict[str, Any]]:
    """Trechos mais relevantes das consultas, restritos aos documentos oficiais da lição."""
    embeddings = get_embeddings()
    excerpts: Dict[str, Dict[str, Any]] = {}
    for query in queries:
        rows = ChunkRepository.match(embeddings.embed_query(query), match_count=40, module=module_id)
        selected = [row for row in rows if row["doc_id"] in docs and row["id"] not in excerpts][:EXCERPTS_PER_QUERY]
        for row in selected:
            excerpts[row["id"]] = row
    return sorted(excerpts.values(), key=lambda row: row["distance"])[:MAX_EXCERPTS]


def format_excerpts(excerpts: List[Dict[str, Any]]) -> str:
    return "\n\n".join(
        f"[{index}] {row['metadata']['document']} ({row['metadata']['section']})\n{row['content']}"
        for index, row in enumerate(excerpts, start=1)
    )


def source_for(excerpts: List[Dict[str, Any]], source_index: int) -> Dict[str, Any]:
    row = excerpts[min(max(source_index, 1), len(excerpts)) - 1]
    meta = row["metadata"]
    return {
        "document": meta["document"],
        "section": meta["section"],
        "institution": meta.get("institution"),
        "url": meta.get("url"),
    }


def build_question(draft: DraftQuestion, question_id: str, excerpts: List[Dict[str, Any]], rng: random.Random) -> Dict[str, Any]:
    options = draft.options[:4]
    correct_text = options[min(max(draft.correct_index, 0), len(options) - 1)]
    rng.shuffle(options)  # o LLM tende a colocar a correta sempre na mesma posição
    option_ids = OPTION_IDS[:len(options)]
    return {
        "id": question_id,
        "question": draft.question,
        "options": [{"id": option_id, "text": text} for option_id, text in zip(option_ids, options)],
        "correct_option": option_ids[options.index(correct_text)],
        "explanation": draft.explanation,
        "source": source_for(excerpts, draft.source_index),
    }


def generate_module(spec: Dict[str, Any], llm: ChatOpenAI) -> Dict[str, Any]:
    module_id = spec["id"]
    rng = random.Random(module_id)
    lessons = []
    exam_excerpts: List[Dict[str, Any]] = []

    for order, lesson_spec in enumerate(spec["lessons"], start=1):
        lesson_id = f"{module_id}_licao_{order}"
        print(f"  {lesson_id}: {lesson_spec['title']}")
        excerpts = retrieve_excerpts(module_id, lesson_spec["docs"], lesson_spec["queries"])
        if not excerpts:
            raise RuntimeError(f"Nenhum trecho encontrado para {lesson_id}; confira a ingestão do corpus")
        exam_excerpts.extend(excerpts[:3])

        draft: LessonDraft = llm.with_structured_output(LessonDraft).invoke([
            ("system", SYSTEM_PROMPT),
            ("human", f"Lição: {lesson_spec['title']} ({lesson_spec['description']})\n\nTrechos oficiais:\n{format_excerpts(excerpts)}"),
        ])
        lessons.append({
            "id": lesson_id,
            "order": order,
            "title": lesson_spec["title"],
            "subtitle": lesson_spec["subtitle"],
            "description": lesson_spec["description"],
            "slides": [
                {"title": slide.title, "text": slide.text, "source": source_for(excerpts, slide.source_index)}
                for slide in draft.slides
            ],
            "chat_suggestions": draft.chat_suggestions[:4],
            "quiz": [
                build_question(question, f"{lesson_id}_q{index}", excerpts, rng)
                for index, question in enumerate(draft.quiz, start=1)
            ],
        })

    print(f"  {module_id}: teste final")
    lesson_titles = ", ".join(lesson["title"] for lesson in lessons)
    exam_draft: ExamDraft = llm.with_structured_output(ExamDraft).invoke([
        ("system", SYSTEM_PROMPT),
        ("human", f"Teste final do módulo '{spec['title']}', cobrindo as lições: {lesson_titles}. "
                  f"Crie questões de aplicação prática (situações do dia a dia do investidor).\n\n"
                  f"Trechos oficiais:\n{format_excerpts(exam_excerpts)}"),
    ])
    return {
        "id": module_id,
        "order": int(module_id.rsplit("_", 1)[1]),
        "title": spec["title"],
        "subtitle": spec["subtitle"],
        "description": spec["description"],
        "color": spec["color"],
        "lessons": lessons,
        "exam": {
            "question_count": EXAM_QUESTION_COUNT,
            "pass_score": EXAM_PASS_SCORE,
            "questions": [
                build_question(question, f"{module_id}_teste_q{index}", exam_excerpts, rng)
                for index, question in enumerate(exam_draft.questions, start=1)
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera rascunhos das lições e testes a partir do corpus RAG.")
    parser.add_argument("--module", help="Gera apenas este módulo (ex: modulo_2)")
    parser.add_argument("--model", default=config.LLM_MODEL, help="Modelo da OpenAI usado na geração")
    parser.add_argument("--force", action="store_true", help="Sobrescreve arquivos existentes (conteúdo revisado)")
    args = parser.parse_args()

    llm = ChatOpenAI(model=args.model, temperature=0.2, api_key=config.OPENAI_API_KEY)
    MODULES_DIR.mkdir(parents=True, exist_ok=True)

    for spec in CURRICULUM:
        if args.module and spec["id"] != args.module:
            continue
        path = MODULES_DIR / f"{spec['id']}.json"
        if path.exists() and not args.force:
            print(f"{path.name} já existe; use --force para sobrescrever o conteúdo revisado")
            continue
        print(f"Gerando {spec['id']} com {args.model}...")
        module = generate_module(spec, llm)
        Module.model_validate(module)
        path.write_text(json.dumps(module, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  salvo em {path}")


if __name__ == "__main__":
    main()
