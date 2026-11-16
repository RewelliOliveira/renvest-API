"""Monta a planilha cega dos especialistas e a planilha de codificação (PLANO_AVALIACAO.md, Seção 6).

Lê data/eval/eval_set_v2.json (conjunto congelado) e gera:
  data/eval/especialistas_avaliacao_cega.xlsx  -> enviar a cada especialista (32 respostas, R01..R32)
  data/eval/especialistas_codificacao.xlsx     -> só do autor: código -> (pergunta, condição)

Cegamento: as 32 respostas (16 RAG + 16 B1) são embaralhadas com semente fixa, sem duas respostas
da mesma pergunta em sequência. Para que o estilo não revele a condição, aplica-se a AMBAS as condições
a mesma normalização de apresentação, sem alterar conteúdo:
  (1) remove marcação markdown (negrito, títulos, marcadores de lista);
  (2) remove frases iniciais curtas que são só saudação ou autoapresentação ("Oi!", "Sou o Rev...")
      e o prefixo de persona numa frase com conteúdo ("Como sou o Rev, o mascote..., meu foco" -> "Meu foco");
  (3) remove frases finais que são só oferta de ajuda ("Vamos lá?", "...estou aqui para ajudar!").
O texto original e o exibido ficam lado a lado na planilha de codificação. O eval_set_v2.json não é alterado.
Limitação conhecida: a citação de documentos e páginas (frequente no RAG) não é ocultada, porque é
justamente um dos critérios avaliados; o cegamento é, portanto, parcial.

Uso: python scripts/build_blind_sheet.py [--seed 20261116]
"""
import argparse
import json
import random
import re
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "data" / "eval"
SRC = EVAL / "eval_set_v2.json"
OUT_BLIND = EVAL / "especialistas_avaliacao_cega.xlsx"
OUT_CODE = EVAL / "especialistas_codificacao.xlsx"

NIVEIS = {"N1": "N1 – Conceitual", "N2": "N2 – Normativa", "N3": "N3 – Cenário", "N4": "N4 – Armadilha"}
CONDICOES = {"RAG": "resposta_rag", "B1": "resposta_baseline"}

GREETING = re.compile(
    r"(?i)^(oi|olá|ola|opa|e aí|vamos lá)[!.,]?$"
    r"|sou o rev|aqui é o rev|o rev aqui|(mascote|tutor) de finanças|meu superpoder"
    r"|^ótima (pergunta|decisão|escolha)|^que (ótima|boa) pergunta"
)
GREETING_MAX = 60  # só remove frases curtas: uma frase longa com saudação também tem conteúdo
PERSONA = re.compile(r"(?i)^(como |eu )?sou o rev,[^,]*,\s*")  # "Como sou o Rev, o mascote ..., meu foco" -> "Meu foco"
CLOSING = re.compile(r"(?i)^vamos lá\?$|estou aqui para (te )?ajudar!?$|^(posso|quer que eu) .*\?$")


FIRST_SENT = re.compile(r"^\s*([^.!?\n]*[.!?])[ \t]*\n?")
LAST_SENT = re.compile(r"\s*([^.!?\n]*[.!?])\s*$")


def normalize(text: str) -> tuple[str, list[str]]:
    """Normalização de apresentação; não muda o conteúdo das respostas."""
    notes = []
    t = text.strip()
    if "**" in t or re.search(r"(?m)^[ \t]*#+[ \t]", t):
        notes.append("markdown")
    t = t.replace("**", "")
    t = re.sub(r"(?m)^[ \t]*#+[ \t]*", "", t)
    if re.search(r"(?m)^[ \t]*(\d+\.|[-*•])[ \t]+", t):
        notes.append("marcadores de lista")
    t = re.sub(r"(?m)^[ \t]*(\d+\.|[-*•])[ \t]+", "", t)
    # saudações curtas no início
    while True:
        m = FIRST_SENT.match(t)
        if not m or len(m.group(1).strip()) > GREETING_MAX or not GREETING.search(m.group(1).strip()):
            break
        notes.append(f"saudação: {m.group(1).strip()!r}")
        t = t[m.end():].lstrip()
    # prefixo de persona numa frase com conteúdo
    m = PERSONA.match(t)
    if m:
        notes.append(f"apresentação: {m.group(0).strip()!r}")
        t = t[m.end():]
        t = t[:1].upper() + t[1:]
    # ofertas de ajuda no fim
    while True:
        m = LAST_SENT.search(t)
        if not m or not CLOSING.search(m.group(1).strip()):
            break
        notes.append(f"despedida: {m.group(1).strip()!r}")
        t = t[:m.start()].rstrip()
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip(), notes


def shuffle_no_adjacent(rows, seed):
    rng = random.Random(seed)
    for _ in range(10000):
        rng.shuffle(rows)
        if all(rows[i]["id"] != rows[i + 1]["id"] for i in range(len(rows) - 1)):
            return rows
    raise RuntimeError("não foi possível embaralhar sem pares adjacentes")


FONT = "Arial"
H_FONT = Font(name=FONT, bold=True, color="FFFFFF", size=10)
H_FILL = PatternFill("solid", fgColor="1F3A5F")
INPUT = PatternFill("solid", fgColor="FFF7D6")
GRAY = PatternFill("solid", fgColor="EDEDED")
BODY = Font(name=FONT, size=10)
THIN = Side(style="thin", color="C8CDD3")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")


def header(ws, row, cols):
    for j, (name, width) in enumerate(cols, 1):
        c = ws.cell(row, j, name)
        c.font, c.fill, c.border = H_FONT, H_FILL, BORDER
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        ws.column_dimensions[c.column_letter].width = width
    ws.row_dimensions[row].height = 45


CRITERIOS = [
    ("Correção factual", ["Correta", "Parcialmente correta", "Incorreta"],
     "A informação está certa? Considere a resposta de referência e o seu conhecimento. Parcialmente correta = acerta o principal, mas tem erro ou omissão importante."),
    ("Contém afirmação errada ou sem suporte?", ["Sim", "Não"],
     "Há alguma afirmação falsa, inventada ou que não pode ser sustentada (valores, prazos, artigos, nomes de normas)?"),
    ("Qual afirmação? (se Sim)", None, "Copie ou resuma a afirmação problemática."),
    ("As fontes citadas existem e sustentam a resposta?", ["Sim", "Parcialmente", "Não", "Não cita fontes"],
     "Se a resposta cita documento, norma ou página: a fonte existe e diz o que a resposta afirma? Se não cita nenhuma fonte, marque 'Não cita fontes'."),
    ("A regra citada está vigente?", ["Sim", "Não", "Não sei", "Não se aplica"],
     "Se a resposta menciona uma norma ou regra: ela está em vigor hoje? 'Não se aplica' se não menciona norma."),
    ("(só N4) Tratou corretamente a premissa ou o limite da base?", ["Sim", "Parcialmente", "Não"],
     "Só nas perguntas N4 (armadilhas): a resposta corrige a premissa falsa, avisa que o tema está fora da base ou que a norma foi substituída?"),
    ("Comentário (opcional)", None, "Qualquer observação."),
]


def build(seed: int) -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    itens, meta = data["itens"], data["metadados"]

    rows = []
    for it in itens:
        for cond, field in CONDICOES.items():
            shown, notes = normalize(it[field])
            rows.append({"id": it["id"], "nivel": it["nivel"], "pergunta": it["pergunta"],
                         "referencia": it["referencia"], "cond": cond, "original": it[field],
                         "shown": shown, "notes": notes})
    rows = shuffle_no_adjacent(rows, seed)
    for k, r in enumerate(rows, 1):
        r["code"] = f"R{k:02d}"

    # ---------------- planilha cega ----------------
    wb = Workbook()
    ins = wb.active
    ins.title = "Instruções"
    ins.column_dimensions["A"].width = 34
    ins.column_dimensions["B"].width = 110
    lines = [
        ("Avaliação de respostas – Renvest (TCC)", None),
        ("", None),
        ("Objetivo", "Avaliar 32 respostas a 16 perguntas de investidores iniciantes. As respostas vêm de duas versões de um assistente, apresentadas em ordem aleatória e identificadas só por um código (R01 a R32). Avalie cada resposta de forma independente, sem tentar adivinhar de qual versão ela veio."),
        ("Resposta de referência", "Cada linha traz a resposta de referência que você validou na etapa anterior. Ela é um apoio: uma resposta pode ser correta mesmo usando outras palavras ou trazendo informação correta a mais."),
        ("Como preencher", "Preencha as colunas amarelas da aba Avaliação usando as listas. Todas as colunas de escolha são obrigatórias, exceto 'Qual afirmação?' (só se marcar Sim) e 'Comentário'. A coluna das armadilhas só vale para as linhas N4."),
        ("Tempo estimado", "Cerca de 60 minutos."),
        ("", None),
        ("Critérios", None),
    ]
    for name, _, desc in CRITERIOS:
        lines.append((name, desc))
    lines += [("", None), ("Exemplo preenchido (pergunta fora do conjunto avaliado)", None)]
    r = 1
    for a, b in lines:
        ca = ins.cell(r, 1, a)
        ca.font = Font(name=FONT, size=14 if r == 1 else 10, bold=bool(a) and (b is None or r > 2))
        ca.alignment = WRAP
        if b:
            cb = ins.cell(r, 2, b)
            cb.font, cb.alignment = BODY, WRAP
        r += 1
    ex = [
        ("Pergunta", "A poupança tem garantia do FGC?"),
        ("Resposta", "Sim. Os depósitos em poupança são cobertos pelo FGC até R$ 250 mil por CPF por instituição, conforme a Resolução CMN nº 4.222/2013. Por isso, a poupança é considerada um investimento sem nenhum risco."),
        ("Correção factual", "Parcialmente correta"),
        ("Contém afirmação errada ou sem suporte?", "Sim"),
        ("Qual afirmação?", "\"Sem nenhum risco\": a garantia tem limite e a poupança tem outros riscos, como perder para a inflação."),
        ("As fontes citadas existem e sustentam a resposta?", "Parcialmente (a resolução existe e sustenta a cobertura, mas não a ausência de risco)"),
        ("A regra citada está vigente?", "Sim"),
        ("(só N4)", "Não se aplica (não é N4)"),
    ]
    for a, b in ex:
        ins.cell(r, 1, a).font = Font(name=FONT, size=10, italic=True)
        cb = ins.cell(r, 2, b)
        cb.font, cb.alignment = Font(name=FONT, size=10, italic=True), WRAP
        r += 1

    av = wb.create_sheet("Avaliação")
    cols = [("Código", 8), ("Nível", 14), ("Pergunta", 38), ("Resposta avaliada", 70), ("Resposta de referência (validada)", 60)]
    cols += [(n, 16 if opts else 30) for n, opts, _ in CRITERIOS]
    header(av, 1, cols)
    first_crit = 6
    for i, row in enumerate(rows, 2):
        vals = [row["code"], NIVEIS[row["nivel"]], row["pergunta"], row["shown"], row["referencia"]]
        for j, v in enumerate(vals, 1):
            c = av.cell(i, j, v)
            c.font, c.border, c.alignment = BODY, BORDER, WRAP
        for k, (name, opts, _) in enumerate(CRITERIOS):
            c = av.cell(i, first_crit + k)
            c.font, c.border, c.alignment = BODY, BORDER, WRAP
            if name.startswith("(só N4)") and row["nivel"] != "N4":
                c.value, c.fill = "Não se aplica", GRAY
            else:
                c.fill = INPUT
        av.row_dimensions[i].height = 220
    last = len(rows) + 1
    for k, (name, opts, _) in enumerate(CRITERIOS):
        if not opts:
            continue
        col = av.cell(1, first_crit + k).column_letter
        dv = DataValidation(type="list", formula1='"' + ",".join(opts) + '"', allow_blank=True)
        dv.error, dv.errorTitle = "Escolha uma opção da lista.", "Valor inválido"
        av.add_data_validation(dv)
        if name.startswith("(só N4)"):
            for i, row in enumerate(rows, 2):
                if row["nivel"] == "N4":
                    dv.add(f"{col}{i}")
        else:
            dv.add(f"{col}2:{col}{last}")
    av.freeze_panes = "B2"
    wb.active = 1
    wb.save(OUT_BLIND)

    # ---------------- planilha de codificação (só do autor) ----------------
    wc = Workbook()
    cs = wc.active
    cs.title = "Codificação"
    header(cs, 1, [("Código", 8), ("ID", 7), ("Nível", 8), ("Condição", 10), ("Normalização aplicada", 40),
                   ("Resposta original (eval_set_v2.json)", 70), ("Resposta exibida ao especialista", 70)])
    for i, row in enumerate(sorted(rows, key=lambda x: x["code"]), 2):
        vals = [row["code"], row["id"], row["nivel"], row["cond"], "; ".join(row["notes"]) or "—",
                row["original"], row["shown"]]
        for j, v in enumerate(vals, 1):
            c = cs.cell(i, j, v)
            c.font, c.border, c.alignment = BODY, BORDER, WRAP
    cs.freeze_panes = "B2"
    ms = wc.create_sheet("Metadados")
    info = [("Semente do embaralhamento", seed), ("Fonte", "data/eval/eval_set_v2.json"),
            ("Gerado em (conjunto)", meta.get("gerado_em")), ("Commit do conjunto", meta.get("git", {}).get("commit")),
            ("Modelo", meta.get("llm_model")), ("Respostas", len(rows)),
            ("Normalizadas", sum(1 for x in rows if x["notes"])),
            ("Regra de normalização", "Mesma regra para RAG e B1: remove markdown, saudações iniciais e ofertas de ajuda finais; conteúdo inalterado."),
            ("Limitação", "Citação de documentos e páginas não é ocultada (é critério avaliado): cegamento parcial.")]
    for i, (a, b) in enumerate(info, 1):
        ms.cell(i, 1, a).font = Font(name=FONT, size=10, bold=True)
        c = ms.cell(i, 2, b)
        c.font, c.alignment = BODY, WRAP
    ms.column_dimensions["A"].width = 30
    ms.column_dimensions["B"].width = 100
    wc.save(OUT_CODE)

    n_norm = {c: sum(1 for x in rows if x["cond"] == c and x["notes"]) for c in CONDICOES}
    print(f"Planilha cega: {OUT_BLIND.name} ({len(rows)} respostas)")
    print(f"Codificação:   {OUT_CODE.name}")
    print(f"Normalizadas: RAG {n_norm['RAG']}, B1 {n_norm['B1']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20261116)
    build(ap.parse_args().seed)
