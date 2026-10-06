# Renvest - RAG Finance Agent 🎓📈

> **Assistente Financeiro Inteligente e Gamificado para Investidores Iniciantes**  
> Trabalho de Conclusão de Curso em Engenharia de Software – Universidade Federal do Ceará (UFC - Quixadá)  
> Autor: Antonio Rewelli Oliveira dos Santos | Orientador: Prof. Dr. Emanuel Ferreira Coutinho

---

## 📌 Visão Geral do Projeto

O **Renvest / RAG Finance Agent** é uma plataforma conversacional de educação financeira projetada para superar a assimetria informacional enfrentada por investidores iniciantes no mercado de capitais brasileiro.

Diferente de IAs generativas genéricas (que alucinam regras locais e sofrem com a barreira da "tela em branco", onde o leigo não sabe o que perguntar), o sistema adota a arquitetura **RAG (Retrieval-Augmented Generation)** com **Tutor Socrático Ativo**. Ele guia o usuário através de **3 Módulos Progressivos e Fechados**, ancorando cada explicação e desafio estritamente em **fontes oficiais brasileiras (CVM, B3, FGC e Banco Central)** com auditoria e rastreabilidade total.

---

## 🗺️ Trilha de Aprendizado: Os 3 Módulos Oficiais

A aplicação possui um fluxo linear e fechado, onde todos os usuários iniciam no **Módulo 1** e avançam até o **Módulo 3** ao superarem os desafios práticos de cada etapa.

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │ MÓDULO 1: O Escudo do Iniciante (Finanças Básicas & Proteção)         │
 │ Foco: Segurança contra falências bancárias e títulos públicos federais │
 ├────────────────────────────────────────────────────────────────────────┤
 │ MÓDULO 2: Os Portões da Bolsa (Mercado de Ações & Governança B3)       │
 │ Foco: Direitos do sócio minoritário, ações ON/PN e o Novo Mercado      │
 ├────────────────────────────────────────────────────────────────────────┤
 │ MÓDULO 3: O Detetive do Mercado (Regulação CVM & Transparência)       │
 │ Foco: Fatos Relevantes, Formulário de Referência e auditoria de riscos │
 └────────────────────────────────────────────────────────────────────────┘
```

---

### 🟢 MÓDULO 1: O Escudo do Iniciante (Finanças Básicas, Renda Fixa & Proteção)
* **Objetivo:** Ensinar o investidor iniciante a compreender os instrumentos mais populares de renda fixa no Brasil (Poupança, CDB e Tesouro Selic), entender o papel da Taxa Selic e blindar seu patrimônio com as garantias do FGC.

#### 📌 Missão 1.1: O Trio de Entrada (Poupança vs. CDB vs. Tesouro Selic)
* **Conceitos e Tópicos Ensinados:**
  1. **A Taxa Selic e o CDI:** O que é a taxa básica de juros da economia brasileira definida pelo Copom/Banco Central e como ela serve de motor para o CDI e a rentabilidade da renda fixa.
  2. **Poupança (A Regra Oficial):** Como funciona o rendimento histórico e atual da poupança (regras quando a Selic está acima ou abaixo de 8,5% ao ano) e por que ela frequentemente perde para a inflação.
  3. **CDB (Certificado de Depósito Bancário):** O que significa "emprestar dinheiro para o banco" e como interpretar títulos que rendem "100% do CDI" ou prefixados.
  4. **Tesouro Selic (Títulos Públicos Federais):** O que significa emprestar dinheiro para o Governo Federal, o conceito de risco soberano (o menor risco de crédito do país) e liquidez diária.
  5. **Quadro Comparativo Direto:** Diferenças práticas entre os três instrumentos em **Segurança**, **Rentabilidade** e **Tributação (Tabela Regressiva de IR vs. Isenção da Poupança)**.
* **Dinâmica do Chat & Chips Sugeridos:**
  * O Mascote inicia: *"Olá, Antonio! Vamos dar o primeiro passo nos seus investimentos. Você já ouviu falar que deixar o dinheiro na Poupança pode fazer você perder poder de compra? Vamos entender a diferença entre Poupança, CDB e Tesouro Selic!"*
  * Chips: `[ O que é CDB? ]` `[ Por que a Poupança rende menos? ]` `[ O que é Taxa Selic? ]` `[ Qual a diferença entre CDB e Tesouro? ]`

#### 📌 Missão 1.2: A Proteção do Dinheiro (O FGC e Limites de Garantia)
* **Conceitos e Tópicos Ensinados:**
  1. O que é o FGC (Fundo Garantidor de Créditos), sua origem e finalidade no sistema financeiro nacional.
  2. Limites de garantia: teto de R$ 250.000 por CPF e por instituição financeira (ou conglomerado) e o sublimite global de R$ 1.000.000 a cada período de 4 anos.
  3. Produtos cobertos (Poupança, CDB, LCI, LCA, RDB) vs. produtos **sem** garantia do FGC (Ações, Fundos de Investimento, Debêntures, Criptoativos).
  4. Por que o Tesouro Direto não precisa de FGC (garantia 100% soberana do Tesouro Nacional).
* **Dinâmica do Chat & Chips Sugeridos:**
  * Chips: `[ O que é o FGC? ]` `[ Quanto o FGC cobre no máximo? ]` `[ Tesouro Direto tem FGC? ]` `[ E se eu tiver conta conjunta? ]`

#### ⚔️ Desafio Integrador do Módulo (Boss Fight 1):
* *Cenário Prático:* *"Dilema do Investidor: Carlos possui R$ 200.000 aplicados em um CDB no Banco Alfa, R$ 70.000 na caderneta de Poupança do mesmo Banco Alfa e R$ 50.000 em um Fundo de Renda Fixa no Banco Beta. Se o Banco Alfa sofrer intervenção do Banco Central e falir, quanto o FGC devolverá para Carlos? O que acontece com a Poupança e com o CDB?"*
* *Gabarito conceitual avaliado pelo LLM:* O FGC devolverá exatamente **R$ 250.000** somando o CDB e a Poupança (já que ambos dividem o mesmo teto de R$ 250 mil por instituição). Os R$ 20.000 excedentes do Banco Alfa não serão recuperados pelo FGC, e o dinheiro no Fundo no Banco Beta não é afetado pela quebra do Banco Alfa.

#### 🗃️ Base de Dados Documental do Módulo 1:
* `tesouro_direto_guia_oficial.pdf` *(Manual do Tesouro Direto: Títulos, Regras e Indexadores)*
* `fgc_regulamento_garantia_oficial.pdf` *(Estatuto e Regulamento do FGC - Anexo II)*
* `anbima_guia_renda_fixa.pdf` *(Caderno Didático ANBIMA: Poupança, CDB e Formação de Juros)*
* *Tool em tempo real:* `bcb_tools.py` *(API do Banco Central do Brasil para consulta da taxa Selic atual)*.


---

### 🟡 MÓDULO 2: Os Portões da Bolsa (Mercado de Ações & Governança B3)
* **Objetivo:** Desmistificar o mercado acionário brasileiro e ensinar o investidor a escolher empresas com os mais altos padrões de respeito ao acionista minoritário.
* **Tópicos Ensinados:**
  1. O que representa uma ação (fração do capital social de uma sociedade anônima).
  2. Diferenças entre Ações Ordinárias (**ON** - código com final 3, com direito a voto) e Ações Preferenciais (**PN** - código com final 4, com preferência em dividendos).
  3. O conceito de *Tag Along* (direito de venda conjunta em caso de alienação de controle).
  4. O segmento **Novo Mercado da B3**: padrão ouro de governança (obrigatoriedade de 100% de ações ON, 100% de Tag Along e percentual mínimo de ações em circulação - *free float*).
* **Dinâmica do Chat & Chips de Perguntas Sugeridas:**
  * O Mascote inicia: *"Bem-vindo ao pregão! Você sabia que nem toda ação na B3 te dá os mesmos direitos de sócio? Vamos descobrir as diferenças?"*
  * Chips: `[ Qual a diferença entre ON e PN? ]` `[ O que é Tag Along? ]` `[ O que é o Novo Mercado? ]`
* **Desafio Integrador do Módulo (Boss Fight 2):**
  * *Cenário:* *"Uma empresa listada no 'Novo Mercado' da B3 decidiu que, para levantar mais capital, vai emitir novas ações preferenciais (sem direito a voto) e oferecer 80% de Tag Along aos acionistas minoritários. De acordo com as regras oficiais da B3, essa empresa violou quais exigências do Novo Mercado?"*
  * *Gabarito conceitual:* Violou duas regras fundamentais: no Novo Mercado o capital deve ser composto **exclusivamente por ações ordinárias (ON)** e o *Tag Along* obrigatório para todos é de **100%**.
* **Documentos Oficiais da Base (`data/raw/`):**
  * `b3_regulamento_novo_mercado.pdf` *(Regulamento de Listagem do Novo Mercado B3)*
  * `cvm_caderno_02_acoes_e_mercado_capitais.pdf` *(Caderno Educacional CVM sobre Ações e Governança)*
  * `b3_regulamento_balcao_2026.pdf` *(Regulamento do Balcão B3 - já integrado)*
  * *Tool em tempo real:* `yfinance_tools.py` (Consulta cotações e histórico real de ativos da B3).

---

### 🔴 MÓDULO 3: O Detetive do Mercado (Regulação CVM & Transparência)
* **Objetivo:** Capacitar o investidor a fiscalizar as empresas de forma autônoma, consultando documentos oficiais e compreendendo a legislação contra assimetria informacional.
* **Tópicos Ensinados:**
  1. O papel da CVM (Comissão de Valores Mobiliários) como órgão fiscalizador e regulador.
  2. Distinção entre Companhia Aberta Categoria A (pode negociar ações no mercado de capitais) e Categoria B (outros títulos, como debêntures).
  3. O **Formulário de Referência (FRE)**: o documento mais completo do mercado, onde se encontram o histórico dos administradores e os Fatores de Risco do negócio (Item 4).
  4. **Fatos Relevantes (Resolução CVM nº 44)**: o dever de transparência imediata quando ocorre vazamento de notícias confidenciais ou oscilação atípica no valor das ações.
* **Dinâmica do Chat & Chips de Perguntas Sugeridas:**
  * O Mascote inicia: *"Agora você é um analista investigativo! Para não cair em promessas milagrosas, você precisa saber onde ler a verdade nua e crua sobre as empresas."*
  * Chips: `[ O que é a CVM? ]` `[ O que tem no Formulário de Referência? ]` `[ Quando a empresa deve soltar Fato Relevante? ]`
* **Desafio Integrador do Módulo (Boss Fight 3):**
  * *Cenário:* *"A diretoria de uma companhia aberta estava negociando uma fusão bilionária sob sigilo. Um jornal publicou os detalhes da operação na primeira página e as ações da empresa dispararam 15% na abertura da B3. De acordo com o Art. 6º da Resolução CVM nº 44, a empresa pode manter o sigilo ou é obrigada a se manifestar? O que ela deve publicar?"*
  * *Gabarito conceitual:* A empresa não pode mais invocar sigilo; é **obrigada a divulgar imediatamente um Fato Relevante** comunicando os fatos ao mercado e à CVM, pois a informação escapou ao controle e causou oscilação atípica.
* **Documentos Oficiais da Base (`data/raw/`):**
  * `cvm_resolucao_44_2021_fatos_relevantes.pdf` *(Texto consolidado da Resolução CVM 44)*
  * `cvm_resolucao_80_2022_companhias_abertas.pdf` *(Texto consolidado da Resolução CVM 80)*
  * `cvm_caderno_01_mercado_capitais.pdf` *(O que é e o papel da CVM no sistema financeiro)*

---

## 🗄️ Resumo da Base de Dados Oficial (`data/raw/`)

Para compor a base vetorial do sistema, os seguintes arquivos oficiais em PDF devem constar na pasta `data/raw/`:

| Arquivo no Repositório | Órgão Oficial | Módulo Correspondente |
| :--- | :--- | :--- |
| `fgc_regulamento_garantia_oficial.pdf` | FGC | **Módulo 1** |
| `tesouro_direto_guia_oficial.pdf` | Tesouro Nacional / B3 | **Módulo 1** |
| `b3_regulamento_novo_mercado.pdf` | B3 | **Módulo 2** |
| `cvm_caderno_02_acoes_e_mercado_capitais.pdf` | CVM Educacional | **Módulo 2** |
| `b3_regulamento_balcao_2026.pdf` | B3 | **Módulo 2** *(Já presente)* |
| `cvm_resolucao_44_2021_fatos_relevantes.pdf` | CVM Legislação | **Módulo 3** |
| `cvm_resolucao_80_2022_companhias_abertas.pdf` | CVM Legislação | **Módulo 3** |
| `cvm_caderno_01_mercado_capitais.pdf` | CVM Educacional | **Módulo 3** |

> **Nota Metodológica sobre o RAG:**  
> A ingestão (`src/database/ingest.py`) processa os PDFs utilizando o **PyMuPDF**, detecta tabelas com **Pandas** (convertendo-as em tabelas Markdown estruturadas), realiza o chunking com overlap de 500 caracteres e armazena os embeddings gerados pelo modelo `text-embedding-3-small` no banco vetorial **ChromaDB** local (`data/vector_db/`).

---

## 🏗️ Arquitetura do Software e Dinâmica de Trabalho

```
                  ARQUITETURA DE INTEGRAÇÃO DO SISTEMA
                  
 ┌────────────────────────────────────────────────────────┐
 │                   FRONTEND (Interface)                 │
 │  • Header com Barra de Progresso do Módulo e XP        │
 │  • Janela do Chat com Balões do Mascote (Tutor RAG)   │
 │  • Chips de Perguntas Rápidas (Scaffolding Cognitivo)  │
 │  • Card Auditável de Fontes e Citações Oficiais        │
 └───────────────────────────▲────────────────────────────┘
                             │ HTTP / JSON
 ┌───────────────────────────▼────────────────────────────┐
 │               BACKEND (FastAPI / Python)               │
 │  • POST /chat (Interação conversacional com RAG)       │
 │  • POST /challenge (Validação semântica do desafio)    │
 │  • GET /modules (Metadados dos 3 módulos e progresso)  │
 └──────┬────────────────────┬────────────────────┬───────┘
        │                    │                    │
 ┌──────▼──────┐      ┌──────▼──────┐      ┌──────▼──────┐
 │  ChromaDB   │      │ Banco Central│     │Yahoo Finance│
 │ (Vetorial)  │      │  (API SGS)  │      │ (yfinance)  │
 └─────────────┘      └─────────────┘      └─────────────┘
```

### Como a aplicação funciona na prática:
1. **Início Direto no Chat:** O usuário entra no sistema e o mascote já abre o diálogo no Módulo 1, acolhendo o iniciante e contextualizando o primeiro tema.
2. **Scaffolding Cognitivo:** Para evitar o bloqueio da tela em branco, o sistema sugere chips de perguntas rápidas, mas permite que o usuário digite dúvidas livremente.
3. **Respostas Ancoradas com RAG:** Cada resposta do agente traz a explicação didática acompanhada do card com a **fonte oficial** (documento e artigo/página).
4. **Desafio Integrador e Ganho de XP:** Ao final de cada módulo, o tutor apresenta o caso prático. A resposta do usuário é avaliada semanticamente pelo modelo. Acertando o desafio, o usuário recebe +50 XP e destrava o próximo módulo na barra de progresso!

---

## 🛠️ Instalação e Execução

### 1. Configurar o Ambiente Virtual:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configurar o `.env`:
Crie um arquivo `.env` na raiz do projeto com sua chave de API da OpenAI:
```env
OPENAI_API_KEY=sua_chave_aqui
```

### 3. Ingestão dos Documentos na Base Vetorial:
Após posicionar os PDFs oficiais em `data/raw/`:
```powershell
python main.py --ingest
```

### 4. Executar Consulta CLI (Testes Rápidos):
```powershell
python main.py --query "Se um banco falir, qual o limite máximo de proteção oferecido pelo FGC?"
```
```powershell
python main.py --query "O que o regulamento do Balcão B3 diz sobre o papel da B3 como administradora?"
```

