# 🧭 Matriz Pedagógica e Fontes de Dados dos Módulos (Renvest)

Este documento define a estrutura temática, os conceitos obrigatórios, as fontes de dados oficiais (links institucionais e regulatórios) e o guia de ingestão para o pipeline RAG dos 3 módulos iniciais de aprendizagem do **Renvest**.

---

## 🗺️ Visão Geral da Trilha de Aprendizagem

```
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                      TRILHA DO INVESTIDOR INICIANTE                         │
 └─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ MÓDULO 1: 💡 Ordem de Operações e Fundamentos                               │
 │ • Controle de Gastos (Regra 50-30-20)                                       │
 │ • Fim das Dívidas Caras (Cartão rotativo e cheque especial)                 │
 │ • Construção da Reserva de Emergência (Liquidez e segurança)                │
 └─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ MÓDULO 2: 📊 Os Pilares dos Investimentos                                   │
 │ • Liquidez (Resgate imediato vs prazos de carência D+N)                     │
 │ • Risco (Volatilidade, calote de crédito e oscilação de mercado)            │
 │ • Retorno (Rentabilidade nominal vs real descontada a inflação)             │
 │ • O Trade-off / Tríade dos Investimentos (A impossibilidade do ganho fácil) │
 └─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ MÓDULO 3: 🗓️ Grandes Classes de Ativos & Diversificação                     │
 │ • Renda Fixa & Proteção do FGC (Tesouro Direto, CDB, LCI, LCA)              │
 │ • Renda Variável & Bolsa (Ações na B3, Fundos Imobiliários e longo prazo)   │
 │ • Princípio da Diversificação (Alocação entre classes e redução de risco)   │
 └─────────────────────────────────────────────────────────────────────────────┘
```

---

## 💡 MÓDULO 1: Ordem de Operações e Fundamentos

### 🎯 Objetivo do Módulo
Garantir que o aluno não pule etapas fundamentais antes de colocar seu primeiro real em risco. Nenhum investimento rende mais do que o custo de uma dívida cara, e nenhum investidor dorme tranquilo sem uma reserva de liquidez.

---

### 📖 Conteúdo Programático

#### 1. 🔎 Controle de Gastos e Orçamento Pessoal
* **O que o agente ensina:** A necessidade de mapear receitas e despesas. Apresentação da **Regra 50-30-20** como balizador prático:
  * **50% para necessidades essenciais:** Moradia, alimentação, contas básicas, saúde e transporte.
  * **30% para desejos pessoais:** Lazer, assinaturas, passeios e estilo de vida.
  * **20% para o futuro financeiro:** Quitação prioritária de débitos e formação de patrimônio.
* **Mensagem-chave:** *Investir não é sobre quanto sobra no fim do mês; é sobre separar primeiro a parte do seu futuro antes de gastar o resto.*

#### 2. ⚠️ Fim das Dívidas Caras (Prioridade Zero)
* **O que o agente ensina:** A matemática implacável dos juros compostos contra o cidadão.
  * As taxas do rotativo do cartão de crédito e do cheque especial superam facilmente 300% a 400% ao ano, enquanto a renda fixa rende historicamente entre 10% e 15% ao ano.
  * Investir tendo dívidas com juros altos é matematicamente equivalente a tentar encher um balde furado.
* **Mensagem-chave:** *Quitar uma dívida de 300% ao ano é o melhor "investimento" com retorno garantido que qualquer pessoa pode fazer.*

#### 3. 🛡️ Reserva de Emergência
* **O que o agente ensina:** A blindagem psicológica e financeira.
  * **Tamanho recomendado:** Entre 3 e 6 meses do custo de vida mensal (para assalariados CLT estáveis) ou 6 a 12 meses (para autônomos e freelancers).
  * **Características inegociáveis:** Máxima segurança (risco de crédito quase nulo) e altíssima liquidez (resgate imediato em D+0 ou D+1).
  * **Onde guardar:** Tesouro Selic, CDBs com liquidez diária de bancos consolidados e contas remuneradas com garantia do FGC.

---

### 🔗 Fontes de Dados e Links Institucionais (Módulo 1)

| Tópico | Instituição | Fonte Oficial / Link Direto | Trecho para Ingestão no RAG |
| :--- | :--- | :--- | :--- |
| **Controle de Gastos & Orçamento** | **Banco Central do Brasil (BCB)** | [Portal de Cidadania Financeira - Gestão de Finanças Pessoais](https://www.bcb.gov.br/cidadaniafinanceira) | Módulo sobre diagnóstico financeiro, orçamento e equilíbrio de despesas. |
| **Dívidas Caras & Juros Rotativos** | **Banco Central do Brasil (BCB)** | [Estatísticas de Crédito e Juros do SFN - BCB](https://www.bcb.gov.br/estatisticas/estatisticasbancarias) | Dados oficiais de taxas de juros médias do rotativo do cartão vs taxa Selic. |
| **Ordem de Operações do Investidor** | **B3 (Bolsa de Valores)** | [Bora Investir B3 - Como começar a investir: dicas para iniciantes](https://borainvestir.b3.com.br/objetivos-financeiros/investir-melhor/como-comecar-a-investir-veja-dicas-para-iniciantes/) | A ordem oficial recomendada pela B3: quitar dívidas -> criar reserva -> investir para objetivos. |
| **Reserva de Emergência** | **Tesouro Nacional / B3** | [Guia Oficial do Tesouro Selic](https://www.tesourodireto.com.br/titulos/tipos-de-tesouro.htm) | Por que o Tesouro Selic é o ativo oficial recomendado para reserva de emergência (liquidez diária e risco soberano). |
| **Regra Prática 50-30-20** | **ENEF (Estratégia Nacional de Educação Financeira)** | [Diretrizes de Educação Financeira para Cidadãos (Gov.br)](https://www.gov.br/conef/pt-br) | Distribuição percentual do orçamento entre despesas fixas, variáveis e poupança. |

---

## 📊 MÓDULO 2: Os Pilares dos Investimentos

### 🎯 Objetivo do Módulo
Capacitar o iniciante a avaliar qualquer produto do mercado através da **Tríade dos Investimentos** (Liquidez, Risco e Retorno), desarmando promessas falsas de "alto retorno com risco zero e resgate imediato".

---

### 📖 Conteúdo Programático

#### 1. 🔄 Liquidez: O Tempo do Seu Dinheiro
* **O que o agente ensina:** A velocidade e a facilidade com que um ativo pode ser transformado em dinheiro na sua conta corrente sem perda significativa de valor.
  * **Liquidez Diária (D+0 ou D+1):** O dinheiro cai no mesmo dia ou no dia útil seguinte (ex: Tesouro Selic, poupança, fundos DI).
  * **Liquidez a Prazo / Carência:** O dinheiro fica travado até uma data futura (ex: CDB de 2 anos, LCI fechada).
  * **Liquidez de Mercado na B3:** A facilidade de encontrar compradores para ações e FIIs no pregão (volume financeiro negociado).

#### 2. 📉 Risco: A Incerteza do Futuro
* **O que o agente ensina:** Risco não é apenas "perder tudo"; é a probabilidade de o resultado real ser diferente do esperado.
  * **Risco de Crédito (Calote):** A instituição que pegou seu dinheiro não honrar o pagamento (mitigado pelo FGC em bancos e pelo Tesouro Nacional em títulos públicos).
  * **Risco de Mercado (Volatilidade):** A oscilação diária de preços causada por eventos econômicos e políticos (ações na Bolsa, marcação a mercado).
  * **Risco de Liquidez:** Precisar do dinheiro e não conseguir resgatar ou ter que vender com grande desconto.

#### 3. 📈 Retorno: A Recompensa do Capital
* **O que o agente ensina:** Como avaliar o ganho real de uma aplicação.
  * **Retorno Nominal vs Retorno Real:** Um rendimento de 10% com inflação de 8% representa ganho real de apenas ~2%. O foco deve sempre estar em superar a inflação (IPCA).
  * **Custo de Oportunidade:** Comparação com a taxa básica de juros (Selic / 100% do CDI). Qualquer investimento de maior risco precisa justificar pagar mais do que a taxa livre de risco.

#### 4. ⚖️ O Trade-off Inegociável (A Tríade dos Investimentos)
* **O que o agente ensina:** Não existe investimento perfeito. Em finanças, é matematicamente impossível maximizar os três pilares ao mesmo tempo:
  * Alta Liquidez + Baixo Risco = **Retorno Moderado/Baixo** (ex: Tesouro Selic).
  * Baixo Risco + Alto Retorno = **Baixa Liquidez** (ex: CDB de longo prazo travado).
  * Alto Retorno + Alta Liquidez = **Alto Risco / Volatilidade** (ex: Day trade, ações).
* **Mensagem-chave:** *Se alguém lhe oferecer "lucro alto, risco zero e resgate imediato", você está diante de uma fraude ou golpe financeiro.*

---

### 🔗 Fontes de Dados e Links Institucionais (Módulo 2)

| Tópico | Instituição | Fonte Oficial / Link Direto | Trecho para Ingestão no RAG |
| :--- | :--- | :--- | :--- |
| **Conceito de Risco, Retorno e Liquidez** | **CVM (Comissão de Valores Mobiliários)** | [Portal do Investidor CVM - Conceitos Básicos de Investimento](https://www.gov.br/investidor/pt-br/educacional/publicacoes-educacionais) | Caderno temático sobre a relação risco x retorno e liquidez no mercado de capitais. |
| **Perfil do Investidor & Suitability** | **CVM** | [Resolução CVM nº 30 (Suitability)](https://conteudo.cvm.gov.br/legislacao/resolucoes/resol030.html) | A exigência de verificar a adequação do produto ao horizonte de tempo e tolerância a perdas do investidor. |
| **Prevenção a Golpes de "Retorno Sem Risco"** | **CVM Educacional** | [Guia CVM de Prevenção a Fraudes e Golpes](https://www.gov.br/investidor/pt-br/educacional/guias-e-folhetos) | Identificação de promessas fraudulentas baseadas na falsa tríade de risco zero com alto retorno. |
| **Risco de Mercado e Volatilidade** | **ANBIMA** | [ANBIMA - Conceitos Essenciais do Mercado de Capitais](https://www.anbima.com.br/pt_br/informar/conceitos-de-renda-fixa.htm) | Risco de taxa de juros, marcação a mercado e oscilação de ativos. |
| **Funcionamento de Liquidez e Negociação** | **B3 (Bolsa de Valores)** | [Bora Investir B3 - Guia de Risco e Retorno](https://borainvestir.b3.com.br/educacao/o-que-e-risco-e-retorno/) | Como equilibrar prazos e volatilidade na formação de uma carteira para iniciantes. |

---

## 🗓️ MÓDULO 3: Grandes Classes de Ativos & Diversificação

### 🎯 Objetivo do Módulo
Apresentar o cardápio real de opções de investimentos no Brasil (Renda Fixa pública e privada, e Renda Variável na B3), ensinando como a **diversificação** é o único "almoço grátis" do mercado financeiro.

---

### 📖 Conteúdo Programático

#### 1. 📝 Renda Fixa: Emprestar Dinheiro com Previsibilidade
* **O que o agente ensina:** O funcionamento dos títulos onde o investidor atua como credor e recebe juros.
  * **Títulos Públicos Federais (Tesouro Direto):** Emprestar dinheiro para o Governo Federal. O ativo de menor risco de crédito do país (risco soberano). Tesouro Selic, Prefixado e IPCA+.
  * **Títulos Privados Bancários (CDB, LCI, LCA):** Emprestar dinheiro para instituições financeiras financiarem empresas, imóveis ou agronegócio.
  * **O Papel do FGC (Fundo Garantidor de Créditos):** A garantia de até R$ 250 mil por CPF e instituição (teto de R$ 1 milhão a cada 4 anos) para Poupança, CDB, RDB, LCI e LCA. O FGC **não** cobre ações, fundos ou títulos públicos.

#### 2. 📊 Renda Variável: Tornar-se Sócio de Negócios na B3
* **O que o agente ensina:** Participar dos resultados econômicos de empresas e imóveis reais.
  * **Ações:** Fração do capital social de uma empresa listada na Bolsa de Valores. Ganho via valorização das cotas e recebimento de proventos (Dividendos e JCP).
  * **Fundos Imobiliários (FIIs):** Condomínios de investidores para aquisição de imóveis físicos (shoppings, galpões logísticos, hospitais) ou títulos imobiliários (CRI), com distribuição mensal de aluguéis.
  * **Mentalidade de Longo Prazo:** No curto prazo o preço oscila como uma votação; no longo prazo o retorno acompanha o lucro e a solidez da empresa.

#### 3. 🥗 Diversificação: Não Colocar Todos os Ovos na Mesma Cesta
* **O que o agente ensina:** A técnica matemática de combinar ativos descorrelacionados para reduzir o risco total sem sacrificar o retorno esperado.
  * Se um setor da economia sofre (ex: alta dos juros prejudica o varejo), outro se beneficia (ex: setor bancário e renda fixa pós-fixada ganham mais).
  * Alocação proporcional conforme o perfil: mais Renda Fixa para quem busca tranquilidade, e uma parcela moderada de Renda Variável para crescimento patrimonial.

---

### 🔗 Fontes de Dados e Links Institucionais (Módulo 3)

| Tópico | Instituição | Fonte Oficial / Link Direto | Trecho para Ingestão no RAG |
| :--- | :--- | :--- | :--- |
| **Garantia de Renda Fixa & Limites** | **FGC (Fundo Garantidor de Créditos)** | [Estatuto e Regulamento Oficial do FGC](https://www.fgc.org.br/garantia-fgc/sobre-a-garantia-fgc) | Resolução CMN 4.222: Cobertura de R$ 250 mil e lista taxativa de produtos garantidos. |
| **Títulos Públicos Federais** | **Tesouro Nacional / B3** | [Manual Oficial de Títulos do Tesouro Direto](https://www.tesourodireto.com.br/titulos/tipos-de-tesouro.htm) | Regras do Tesouro Selic, Tesouro Prefixado e Tesouro IPCA+. |
| **Mercado Acionário e Governança** | **B3 (Bolsa do Brasil)** | [Regulamento de Listagem do Novo Mercado B3](https://www.b3.com.br/pt_br/produtos-e-servicos/solucoes-para-emissores/segmentos-de-listagem/novo-mercado/) | Ações ON, 100% Tag Along e proteção aos minoritários. |
| **Fundos Imobiliários (FIIs)** | **B3 / CVM** | [Guia Oficial de Fundos Imobiliários - B3 Bora Investir](https://borainvestir.b3.com.br/guia-de-fiis/) | Como funcionam os FIIs, rendimentos isentos de IR e liquidez em cotas. |
| **Conceito de Ações e Direitos Societários** | **CVM Educacional** | [Caderno CVM nº 2 - Ações e Mercado de Capitais](https://www.gov.br/investidor/pt-br/educacional/publicacoes-educacionais/cadernos-cvm) | O que são ações ordinárias vs preferenciais, dividendos e direitos do acionista. |
| **Diversificação e Teoria de Carteira** | **CVM / ANBIMA** | [Portal do Investidor CVM - Como Diversificar seus Investimentos](https://www.gov.br/investidor/pt-br/educacional/publicacoes-educacionais) | Redução do risco não-sistêmico através da diversificação de classes e emissores. |

---

## 🗃️ Estrutura Recomendada de Arquivos para o RAG (`data/raw/`)

Para manter o banco vetorial (**ChromaDB**) 100% organizado e auditável, estruture a pasta `data/raw/` dividida por módulo:

```
rag-finance-agent/data/raw/
├── modulo_1_fundamentos/
│   ├── bcb_gestao_financas_pessoais.md          # Orçamento, 50-30-20 e dívidas caras
│   ├── b3_ordem_de_operacoes_iniciante.md       # Dicas de início, prioridades e reserva
│   └── tesouro_reserva_emergencia.md            # Tesouro Selic e liquidez para emergência
│
├── modulo_2_pilares/
│   ├── cvm_triade_risco_retorno_liquidez.md     # Conceito dos 3 pilares e trade-offs
│   ├── cvm_guia_prevencao_golpes_promessas.md   # Desmistificando promessa de lucro sem risco
│   └── anbima_volatilidade_e_prazos.md          # Riscos de crédito, mercado e liquidez
│
└── modulo_3_classes_e_diversificacao/
    ├── fgc_regulamento_garantia_oficial.md      # Teto R$ 250 mil, teto R$ 1 mi e produtos
    ├── tesouro_titulos_regras_tributacao.md     # Tipos de Tesouro e tabela regressiva
    ├── b3_acoes_fiis_guia_iniciante.md          # Mercado de ações na B3 e fundos imobiliários
    └── cvm_caderno_acoes_diversificacao.md      # Alocação de ativos e redução de risco
```

### 🏷️ Schema de Metadados Recomendado para o `ingest.py`:
Ao indexar no ChromaDB, cada chunk deve carregar os seguintes metadados estruturados:

```python
metadata = {
    "module": "modulo_1",                          # modulo_1 | modulo_2 | modulo_3
    "topic": "reserva_de_emergencia",             # topico exato da pergunta
    "institution": "B3 / Tesouro Nacional",        # Orgao oficial
    "source_title": "Bora Investir B3 - Reserva", # Nome amigavel para exibir no card do Chat
    "source_url": "https://borainvestir.b3.com.br/...", # Link clicavel no frontend
    "section": "Tamanho ideal da reserva e onde aplicar"
}
```

---

## 🎮 Desafios Práticos de Cada Módulo (Boss Fight para Ganho de XP)

Para integrar com o fluxo do frontend e destravar a barra de progresso:

### Desafio 1 (Módulo 1 - Fundamentos):
* **Caso:** *"Mariana ganha R$ 4.000 líquidos por mês. Ela possui R$ 5.000 acumulados no rotativo do cartão de crédito (pagando 15% de juros ao mês) e quer aplicar R$ 500 no Tesouro Direto para 'começar a investir'. Qual conselho financeiro baseado na ordem de operações Mariana deve seguir antes de comprar qualquer título?"*
* **Gabarito Semântico:** Mariana deve primeiro quitar ou renegociar a dívida do cartão de crédito, pois o custo dos juros rotativos destrói qualquer rendimento de investimento. Somente após zerar essa dívida ela deve formar sua reserva de emergência e começar a investir.

### Desafio 2 (Módulo 2 - Os Pilares):
* **Caso:** *"Um aplicativo promete um investimento que rende 5% ao mês garantido, sem nenhuma oscilação negativa e com resgate imediato a qualquer hora via Pix. Analisando através do Trilema dos Investimentos (Risco, Retorno e Liquidez), por que essa oferta viola os princípios financeiros e é provavelmente um golpe?"*
* **Gabarito Semântico:** Viola a Tríade dos Investimentos porque é impossível unir rentabilidade muito acima do mercado (5% a.m.), liquidez imediata e risco zero simultaneamente. Promessas desse tipo ignoram o trade-off financeiro e configuram golpe/pirâmide.

### Desafio 3 (Módulo 3 - Classes & Diversificação):
* **Caso:** *"Pedro tem R$ 100.000 e decidiu colocar todo o dinheiro em ações de uma única empresa do setor de varejo porque ela subiu 30% no ano anterior. O que acontece com a segurança de Pedro segundo os conceitos de Diversificação e Renda Variável? Como ele deveria reestruturar a carteira?"*
* **Gabarito Semântico:** Pedro assumiu risco não-sistêmico máximo por concentrar 100% do patrimônio em uma única empresa de renda variável volátil. Ele deveria diversificar entre Renda Fixa (para previsibilidade e reserva) e diferentes setores de Renda Variável, reduzindo o risco de perda permanente.
