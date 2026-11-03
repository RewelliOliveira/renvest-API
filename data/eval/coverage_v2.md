# Checagem de cobertura – avaliação v2

Gerado em 03/11/2026 11:25 · top-5 · k do chat = 3 · limiar = 0.5 · embedding = text-embedding-3-small

`*` = trecho que o chat usaria (top-k dentro do limiar) · `✓` = documento esperado

| ID | Resultado automático |
| :-- | :-- |
| N1.1 | PARCIAL: documento esperado só no top-5 (fora do top-3 do chat) |
| N1.2 | PROVÁVEL: documento esperado no top-3 do chat; confira o texto |
| N1.3 | PARCIAL: documento esperado só no top-5 (fora do top-3 do chat) |
| N2.1 | PROVÁVEL: documento esperado no top-3 do chat; confira o texto |
| N2.2 | PROVÁVEL: documento esperado no top-3 do chat; confira o texto |
| N2.3 | PROVÁVEL: documento esperado no top-3 do chat; confira o texto |
| N2.4 | PARCIAL: documento esperado só no top-5 (fora do top-3 do chat) |
| N2.5 | PARCIAL: documento esperado só no top-5 (fora do top-3 do chat) |
| N3.1 | PARCIAL: documento esperado só no top-5 (fora do top-3 do chat) |
| N3.2 | PROVÁVEL: documento esperado no top-3 do chat; confira o texto |
| N3.3 | PROVÁVEL: documento esperado no top-3 do chat; confira o texto |
| N3.4 | PROVÁVEL: documento esperado no top-3 do chat; confira o texto |
| N3.5 | PROVÁVEL: documento esperado no top-3 do chat; confira o texto |
| N4.1 | PROVÁVEL: documento esperado no top-3 do chat; confira o texto |
| N4.2 | ATENÇÃO: 3 trecho(s) passariam para o chat; confira se são pertinentes |
| N4.3 | FALHOU: documento esperado não aparece com distância <= limiar; trocar ou reformular |

## N1.1 (N1, sem filtro)

**Pergunta:** O que é renda fixa e quais são os principais produtos dessa categoria no Brasil?

**Esperado:** responder · documentos: bcb_caderno_gestao_financas_pessoais, cvm_livro_top_planejamento_financeiro_pessoal

**Resultado automático:** PARCIAL: documento esperado só no top-5 (fora do top-3 do chat)

**Conferência manual:** [ ] contém a informação  

| # | Documento | Página | Distância | Chat |
| :-: | :-- | :-- | :-: | :-: |
| 1 | cvm_livro_top_direito_mercado_valores_mobiliarios | p. 313 | 0.341 | * |
| 2 | cvm_caderno_03_fundos_investimento | p. 16 | 0.369 | * |
| 3 | cvm_livro_top_mercado_valores_mobiliarios | p. 269 | 0.375 | * |
| 4 | cvm_livro_top_planejamento_financeiro_pessoal ✓ | p. 85-86 | 0.377 |  |
| 5 | cvm_livro_top_mercado_valores_mobiliarios | p. 104 | 0.382 |  |

> **1.** 9.4. Mercado de renda fixa e mercado de renda variável. Considerando o valor mobiliário ou ativo/produto negociado ou ofertado, podemos classificar o mercado como sendo mercado de renda fixa ou de renda variável. Por renda fixa, entende-se que o rendimento a ser auferido pelo investidor é determinad…

> **2.** Fundos de Renda Fixa Os fundos classificados como “Renda Fixa” apresentam como principal fator de risco de sua carteira a variação da taxa de juros, de índice de preços, ou ambos. Devem ter pelo menos 80% da sua carteira investida em ativos que estejam relacionados a esses fatores de risco. Na práti…

> **3.** 8.2.3. Renda Fixa Há muitos títulos e valores mobiliários de renda fixa no mercado financeiro, que permi tem que pessoas, empresas e governos captem empréstimos ou cedam recebíveis, levan tando recursos para o desenvolvimento das suas atividades. Na B3 Alguns são registrados e outros negociados. a B…

> **4.** De acordo com o tipo de remuneração, os títulos de renda fixa podem ser classifica dos em: . Prefixados: o investidor sabe, no momento da compra, o montante em reais que receberá no vencimento. São títulos com juros fixos, estabelecidos no mo mento de seu lançamento ao público. . Pós-fixados: atrela…

> **5.** Renda Fixa - Curto Prazo As classes Renda Fixa - Curto Prazo devem investir seus recursos exclusivamente em: (i) títulos públicos federais e operações compromissadas neles lastreadas; (ii) títulos privados de baixo risco de crédito com prazo máximo a decorrer de 375 dias e prazo médio da carteira in…

## N1.2 (N1, sem filtro)

**Pergunta:** O que é a CVM e qual é o seu papel no mercado de capitais brasileiro?

**Esperado:** responder · documentos: cvm_caderno_01_o_que_e_a_cvm

**Resultado automático:** PROVÁVEL: documento esperado no top-3 do chat; confira o texto

**Conferência manual:** [ ] contém a informação  

| # | Documento | Página | Distância | Chat |
| :-: | :-- | :-- | :-: | :-: |
| 1 | cvm_caderno_01_o_que_e_a_cvm ✓ | p. 7 | 0.206 | * |
| 2 | cvm_livro_top_direito_mercado_valores_mobiliarios | p. 22-23 | 0.224 | * |
| 3 | cvm_caderno_01_o_que_e_a_cvm ✓ | p. 3-7 | 0.239 | * |
| 4 | cvm_livro_top_direito_mercado_valores_mobiliarios | p. 55-56 | 0.241 |  |
| 5 | cvm_caderno_01_o_que_e_a_cvm ✓ | p. 7-8 | 0.252 |  |

> **1.** a cvm 1 1.1. QUEM É A CVM é a instituição do governo responsável pela regulação e fiscalização do mercado de capitais no Brasil. Criada em 1976, é uma Autarquia Federal que tem entre suas funções: estabelecer normas, fiscalizar seu cumprimento, punir aqueles que as descumprem e buscar o desenvolvime…

> **2.** 1.3.5. Entidade supervisora do mercado de capitais: Comissão de Valores Mobiliários A Comissão de Valores Mobiliários (CVM) foi criada em 1976, pela Lei no 6.385/76. Passou a funcionar efetivamente em 1978, absorvendo as competências da antiga GEMEC. É o órgão regulador do mercado de capitais e, ass…

> **3.** Aproveite este conteúdo, utilize as ferramentas e os sites indicados e entre em contato caso tenha dúvidas ou algum problema ao investir. o que você vai ver a cvm 07 1 quem é, área de atuação, histórico a regulação 13 2 fundamentos, funções da cvm, autorregulação divulgação de informações 21 3 impor…

> **4.** FUNDAÇÃO GETÚLIO VARGAS (FGV). 3. A CVM: COMPETÊNCIA LEGAL, FUNÇÕES, PODERES E ATRIBUIÇÕES O mercado de capitais brasileiro é regulado pela Comissão de Valores Mobiliários – CVM, autarquia federal instituída pela Lei n° 6.385/76, com sede na cidade do Rio de Janeiro e representação nas cidades de Br…

> **5.** • Promover o desenvolvimento e a eficiência do mercado; • Proteger os investidores contra fraudes e práticas irregulares. 1.2. ÁREA DE ATUAÇÃO A CVM atua, primordialmente, no mercado de valores mobiliários, também chamado de mercado de capitais. Mas o que é esse mercado? O mercado de capitais É o se…

## N1.3 (N1, sem filtro)

**Pergunta:** O que é o FGC e quais produtos ele cobre?

**Esperado:** responder · documentos: cmn_resolucao_4222_fgc

**Resultado automático:** PARCIAL: documento esperado só no top-5 (fora do top-3 do chat)

**Conferência manual:** [ ] contém a informação  

| # | Documento | Página | Distância | Chat |
| :-: | :-- | :-- | :-: | :-: |
| 1 | cvm_livro_top_planejamento_financeiro_pessoal | p. 103-104 | 0.359 | * |
| 2 | cvm_livro_top_planejamento_financeiro_pessoal | p. 96 | 0.378 | * |
| 3 | cvm_livro_top_planejamento_financeiro_pessoal | p. 106 | 0.382 | * |
| 4 | cmn_resolucao_4222_fgc ✓ | p. 12 | 0.393 |  |
| 5 | cmn_resolucao_4222_fgc ✓ | p. 9 | 0.408 |  |

> **1.** Fundo Garantidor de Créditos (FGC) O Fundo Garantidor de Créditos (FGC) é uma associação civil sem fins lucrativos e tem por objeto prestar garantia de créditos contra instituições dele participantes, nas hipóteses de: . Decretação da intervenção, liquidação extrajudicial ou falência da associada. .…

> **2.** Emissor Bancos comerciais, múltiplos, de desenvolvimento, de investimento, sociedades de crédito, financiamento e investimento e caixas econômicas. Garantia do FGC Limitada a R$ 20 milhões por titular, englobando o principal mais os juros do total de créditos de cada pessoa contra a mesma instituiçã…

> **3.** Para saber mais sobre Limite de Cobertura Ordinária do FGC acesse < e <-nova- garantia>. ​ Fundo Garantidor do Cooperativismo de Crédito (FGCoop) O FGCoop foi fundado em 2013 pelo BACEN objetivando dar estabilidade do Siste ma Nacional de Crédito Cooperativo (SNCC). O fundo visa igualar as condições…

> **4.** Parágrafo único. Havendo indícios da existência de adoção de procedimentos com o objetivo de obtenção de ressarcimento além do limite individual estabelecido ou de operações que revelem indícios de fraude ou de tentativa, por qualquer meio, de exceder os valores máximos de cobertura, o pagamento das…

> **5.** ANEXO I À RESOLUÇÃO No 4.222, DE 23 DE MAIO DE 2013 (Anexo I com redação dada pela Resolução no 4.688, de 25/9/2018.) ESTATUTO DO FGC CAPÍTULO I DA DENOMINAÇÃO, DO OBJETO, DA FINALIDADE, DA SEDE E DO PRAZO Art. 1o O Fundo Garantidor de Créditos (FGC) é uma associação civil sem fins lucrativos, com p…

## N2.1 (N2, sem filtro)

**Pergunta:** Qual é o limite de garantia do FGC por pessoa e por instituição, e existe um teto total para quem tem aplicações em vários bancos?

**Esperado:** responder · documentos: cmn_resolucao_4222_fgc

**Resultado automático:** PROVÁVEL: documento esperado no top-3 do chat; confira o texto

**Conferência manual:** [ ] contém a informação  

| # | Documento | Página | Distância | Chat |
| :-: | :-- | :-- | :-: | :-: |
| 1 | cvm_livro_top_planejamento_financeiro_pessoal | p. 96 | 0.237 | * |
| 2 | cvm_livro_top_planejamento_financeiro_pessoal | p. 106 | 0.266 | * |
| 3 | cmn_resolucao_4222_fgc ✓ | p. 36-37 | 0.273 | * |
| 4 | cvm_livro_top_planejamento_financeiro_pessoal | p. 103-104 | 0.315 |  |
| 5 | cvm_livro_top_planejamento_financeiro_pessoal | p. 106 | 0.316 |  |

> **1.** Emissor Bancos comerciais, múltiplos, de desenvolvimento, de investimento, sociedades de crédito, financiamento e investimento e caixas econômicas. Garantia do FGC Limitada a R$ 20 milhões por titular, englobando o principal mais os juros do total de créditos de cada pessoa contra a mesma instituiçã…

> **2.** Limitação da garantia até R$ 1 milhão O Conselho Monetário Nacional (CMN) aprovou, em 21 de dezembro de 2017, a al teração promovida no Regulamento do Fundo Garantidor de Créditos (FGC), que estabelece teto de R$ 1 milhão, a cada período de quatro anos, para garantias pagas para cada CPF ou CNPJ. Ga…

> **3.** I - até o valor máximo de R$400.000.000,00 (quatrocentos milhões de reais) nas operações cujo titular do crédito seja instituição associada ao FGC; e (Incluído pela Resolução no 4.805, de 23/4/2020.) II - até o valor máximo de R$40.000.000,00 (quarenta milhões de reais) para os demais titulares. (In…

> **4.** Fundo Garantidor de Créditos (FGC) O Fundo Garantidor de Créditos (FGC) é uma associação civil sem fins lucrativos e tem por objeto prestar garantia de créditos contra instituições dele participantes, nas hipóteses de: . Decretação da intervenção, liquidação extrajudicial ou falência da associada. .…

> **5.** Para saber mais sobre Limite de Cobertura Ordinária do FGC acesse < e <-nova- garantia>. ​ Fundo Garantidor do Cooperativismo de Crédito (FGCoop) O FGCoop foi fundado em 2013 pelo BACEN objetivando dar estabilidade do Siste ma Nacional de Crédito Cooperativo (SNCC). O fundo visa igualar as condições…

## N2.2 (N2, sem filtro)

**Pergunta:** Em quanto tempo o dinheiro de uma venda antecipada no Tesouro Direto cai na conta, e o horário da venda muda isso?

**Esperado:** responder · documentos: tesouro_direto_regulamento

**Resultado automático:** PROVÁVEL: documento esperado no top-3 do chat; confira o texto

**Conferência manual:** [ ] contém a informação  

| # | Documento | Página | Distância | Chat |
| :-: | :-- | :-- | :-: | :-: |
| 1 | tesouro_direto_regulamento ✓ | p. 38 | 0.309 | * |
| 2 | tesouro_direto_regulamento ✓ | p. 37-38 | 0.324 | * |
| 3 | tesouro_direto_regulamento ✓ | p. 17 | 0.364 | * |
| 4 | tesouro_direto_regulamento ✓ | p. 16-17 | 0.365 |  |
| 5 | tesouro_direto_regulamento ✓ | p. 13 | 0.378 |  |

> **1.** agendamento entre as 00:00 hora e as 5:00 horas no mesmo dia útil da venda, desde que os preços/taxas dos respectivos Títulos sejam disponibilizados no Tesouro Direto antes das 13:00 horas do mesmo dia útil; no caso de disponibilização dos preços/taxas após às 13:00hs, o repasse dos recursos líquido…

> **2.** respectivos Títulos sejam disponibilizados no Tesouro Direto antes das 13:00 horas do mesmo dia útil; ix. repassar os recursos líquidos aos Investidores que venderam seus Títulos por meio de agendamento entre as 18:01 horas e as 23:59 horas, no máximo no dia útil posterior à venda, desde que os preç…

> **3.** Tesouro Direto. 54. Os preços e as quantidades de Títulos disponíveis para venda no Tesouro Direto são atualizados diariamente pela STN, segundo critérios por ela definidos e divulgados no site do Tesouro Direto. A STN, a qualquer momento e a seu critério, poderá alterar os preços e as quantidades d…

> **4.** Fator de Divisibilidade será previamente definido pela STN e disponibilizado no Tesouro Direto; e vi. para os títulos Tesouro RendA+ Aposentadoria Extra (NTN-B1) e Tesouro Educa+ (NTN-B1), é necessário que tenha transcorrido o período de carência de venda de 60 (sessenta) dias, contados a partir da …

> **5.** por CPF estabelecido pela STN somado, na data de sua ocorrência, aos resgates, juros e amortizações de Títulos do Investidor no Tesouro Direto. O Limite máximo mensal de compra do Investidor é válido do primeiro ao último dia do mês. 34. Caso um dos critérios ou requisitos estabelecidos no parágrafo…

## N2.3 (N2, sem filtro)

**Pergunta:** Por quanto tempo antes da divulgação das demonstrações financeiras os administradores de uma companhia aberta ficam proibidos de negociar ações da empresa?

**Esperado:** responder · documentos: cvm_resolucao_44_2021

**Resultado automático:** PROVÁVEL: documento esperado no top-3 do chat; confira o texto

**Conferência manual:** [ ] contém a informação  

| # | Documento | Página | Distância | Chat |
| :-: | :-- | :-- | :-: | :-: |
| 1 | cvm_livro_top_direito_mercado_valores_mobiliarios | p. 234 | 0.235 | * |
| 2 | cvm_livro_top_direito_mercado_valores_mobiliarios | p. 539 | 0.275 | * |
| 3 | cvm_resolucao_44_2021 ✓ | p. 13 | 0.289 | * |
| 4 | cvm_livro_top_direito_mercado_valores_mobiliarios | p. 863 | 0.293 |  |
| 5 | cvm_livro_top_direito_mercado_valores_mobiliarios | p. 534 | 0.296 |  |

> **1.** § 2o Sem prejuízo do disposto no parágrafo anterior, a vedação do caput se aplica também aos administradores que se afastem da administração da companhia antes da divulgação pública de negócio ou fato iniciado durante seu período de gestão, e se estenderá pelo prazo de seis meses após o seu afastame…

> **2.** A vedação à negociação por acionistas, administradores e pela própria companhia enquanto estiver em curso programa de recompra de ações da companhia (§ 3o, II), no período que antecede a publicação de demonstrações financeiras (§ 4o) e no período relevante para definir condições de negócios divulgad…

> **3.** trimestrais e das demonstrações financeiras anuais da companhia. § 1o A proibição de que trata o caput independe da avaliação quanto à existência de informação relevante pendente de divulgação ou da intenção em relação à negociação. § 2o A contagem do prazo referido no caput deve ser feita excluindo…

> **4.** . 22 Art. 13. Antes da divulgação ao mercado de ato ou fato relevante ocorrido nos negócios da companhia, é vedada a negociação com valores mobiliários de sua emissão, ou a eles referenciados, pela própria companhia aberta, pelos acionistas controladores, diretos ou indiretos, diretores, membros do …

> **5.** . 13. Antes da divulgação ao mercado de ato ou fato relevante ocorrido nos negócios da companhia, é vedada a negociação com valores mobiliários de sua emissão, ou a eles referenciados, pela própria companhia aberta, pelos acionistas controladores, diretos ou indiretos, diretores, membros do conselho…

## N2.4 (N2, sem filtro)

**Pergunta:** Se uma informação relevante vazar antes de a empresa divulgar, o que a companhia é obrigada a fazer e em quanto tempo?

**Esperado:** responder · documentos: cvm_resolucao_44_2021

**Resultado automático:** PARCIAL: documento esperado só no top-5 (fora do top-3 do chat)

**Conferência manual:** [ ] contém a informação  

| # | Documento | Página | Distância | Chat |
| :-: | :-- | :-- | :-: | :-: |
| 1 | cvm_livro_top_direito_mercado_valores_mobiliarios | p. 523 | 0.301 | * |
| 2 | cvm_livro_top_mercado_valores_mobiliarios | p. 209 | 0.303 | * |
| 3 | cvm_livro_top_direito_mercado_valores_mobiliarios | p. 523 | 0.305 | * |
| 4 | cvm_livro_top_mercado_valores_mobiliarios | p. 155-156 | 0.310 |  |
| 5 | cvm_resolucao_44_2021 ✓ | p. 15 | 0.316 |  |

> **1.** Exepcionalmente, nos casos em que os acionistas controladores ou os administradores entenderem que a revelação do ato ou fato relevante porá em risco interesse legítimo da companhia, a divulgação não necessariamente ocorrerá de forma imediata à ocorrência do fato relevante. A adoção desse procedimen…

> **2.** Esses fatos também devem ser incluídos como vetores de risco no planejamento de administração de crises. Mas, sobretudo, não podem nem devem, nos termos da regulamentação, ser omitidos no caso de se mostrarem relevantes. Para contornar esses momentos e minimizar a perda de valor para a companhia, é …

> **3.** No entanto, caso a informação escape ao controle45 ou caso ocorra oscilação atípica na cotação, preço ou quantidade negociada dos valores mobiliários de emissão da companhia ou a eles referenciados, surge a obrigação de se divulgar imediatamente o ato ou fato relevante, conforme o § único do art. 6o…

> **4.** Além de comunicar à CVM e à Bolsa, a empresa deve disseminar a informação por meio do seu site de relações com investidores e dos jornais de grande circulação normalmente utilizados 155 Companhias pela companhia para publicações. Neste último caso, é possível publicar o fato resumidamen te, desde qu…

> **5.** que utiliza para disseminar informações sobre atos e fatos relevantes nos termos do art. 3o, § 4o, e os procedimentos relativos à manutenção de sigilo acerca de informações relevantes não divulgadas. § 1o A companhia deve comunicar formalmente os termos da deliberação aos acionistas controladores e …

## N2.5 (N2, sem filtro)

**Pergunta:** Qual percentual mínimo de ações em circulação (free float) uma empresa do Novo Mercado precisa manter?

**Esperado:** responder · documentos: b3_regulamento_novo_mercado

**Resultado automático:** PARCIAL: documento esperado só no top-5 (fora do top-3 do chat)

**Conferência manual:** [ ] contém a informação  

| # | Documento | Página | Distância | Chat |
| :-: | :-- | :-- | :-: | :-: |
| 1 | cvm_livro_top_mercado_valores_mobiliarios | p. 279 | 0.228 | * |
| 2 | cvm_livro_top_direito_mercado_valores_mobiliarios | p. 723-724 | 0.244 | * |
| 3 | cvm_livro_top_mercado_valores_mobiliarios | p. 277 | 0.267 | * |
| 4 | b3_regulamento_novo_mercado ✓ | p. 7 | 0.271 |  |
| 5 | cvm_livro_top_direito_mercado_valores_mobiliarios | p. 724 | 0.281 |  |

> **1.** 25% a partir do 7o ano de listagem 25% a partir do 7o ano de listagem Percentual mínimo de ações em circulação (free float) Regra geral: 20% Regra alternativa: 15%, (i) caso o ADTV (average daily trading volume) seja igual ou superior a R$ 20 milhões, considerando os negócios realizados nos últimos …

> **2.** 723 Ofertas Públicas de Aquisição de Ações (OPAs) Percentual Mínimo de Ações em Circulação Os regulamentos de listagem do Novo Mercado e dos Níveis 1 e 2 de governança corporativa, dispõem que, permanentemente, a companhia listada deverá manter em circulação (free float), ao menos, 25% do capital so…

> **3.** . Para isso, divulgam informações adicionais às exigidas em lei, como por exemplo, um calendário anual de eventos corporativos. . O free float mínimo de 20%, podendo ser de 15% caso o volume médio de negociação diária (adtv) seja de R$ 20.000.000 ou mais,ou seja, a empresa se com promete a manter no…

> **4.** correspondente a, no mínimo: 20% (vinte por cento) do capital social; ou 15% (quinze por cento) do capital social, desde que o volume financeiro médio diário de negociação das ações da companhia se mantenha igual ou superior a R$20.000.000,00 (vinte milhões de reais), considerados os negócios realiz…

> **5.** 42 Com a reforma no regulamento de listagem do Novo Mercado em 2017, foi criada a possibilidade de companhias listadas em tal segmento manterem um nível inferior de ações em circulação – desde que suas ações sejam objeto de elevado volume de negociação. Assim, companhias com um volume financeiro méd…

## N3.1 (N3, sem filtro)

**Pergunta:** Tenho R$ 400 mil para aplicar e quero ficar protegido pelo FGC. Como posso distribuir entre CDB, LCI e Tesouro Direto e o que fica fora da garantia?

**Esperado:** responder · documentos: cmn_resolucao_4222_fgc, tesouro_direto_regulamento

**Resultado automático:** PARCIAL: documento esperado só no top-5 (fora do top-3 do chat)

**Conferência manual:** [ ] contém a informação  

| # | Documento | Página | Distância | Chat |
| :-: | :-- | :-- | :-: | :-: |
| 1 | bcb_caderno_gestao_financas_pessoais | p. 64-65 | 0.365 | * |
| 2 | bcb_caderno_gestao_financas_pessoais | p. 59 | 0.372 | * |
| 3 | cvm_livro_top_planejamento_financeiro_pessoal | p. 104 | 0.376 | * |
| 4 | cmn_resolucao_4222_fgc ✓ | p. 36-37 | 0.378 |  |
| 5 | cvm_livro_top_planejamento_financeiro_pessoal | p. 106 | 0.387 |  |

> **1.** É importante saber que existem o Fundo Garantidor de Créditos (FGC) e o Fundo Garantidor do Cooperativismo de Crédito (FGCoop), instituições que protegem depositantes e investidores em certas modalidades de investimentos financeiros. A garantia de crédito prestada por essas instituições é especialme…

> **2.** . Assim, se a instituição financeira onde você tem sua conta de poupança vier a falir, uma parte substantiva do seu patrimônio está protegida pelo FGC ou pelo FGCoop (que também protegem outros investimentos financeiros, tais como CDB, RDB, RDC, LCI, LCA).…

> **3.** . Sociedades de crédito imobiliário. . Companhias hipotecárias. . Associações de poupança e empréstimo. Garantia ordinária até R$250 mil Ativos financeiros que contam com a garantia ordinária, até R$ 250.000,00 por CPF ou CNPJ, proporcionada pelo FGC: . Depósitos à vista ou sacáveis mediante aviso p…

> **4.** I - até o valor máximo de R$400.000.000,00 (quatrocentos milhões de reais) nas operações cujo titular do crédito seja instituição associada ao FGC; e (Incluído pela Resolução no 4.805, de 23/4/2020.) II - até o valor máximo de R$40.000.000,00 (quarenta milhões de reais) para os demais titulares. (In…

> **5.** Limitação da garantia até R$ 1 milhão O Conselho Monetário Nacional (CMN) aprovou, em 21 de dezembro de 2017, a al teração promovida no Regulamento do Fundo Garantidor de Créditos (FGC), que estabelece teto de R$ 1 milhão, a cada período de quatro anos, para garantias pagas para cada CPF ou CNPJ. Ga…

## N3.2 (N3, sem filtro)

**Pergunta:** Trabalho numa companhia aberta e soube de uma aquisição antes do anúncio oficial. Posso comprar ações dela? O que a regra diz e o que pode acontecer?

**Esperado:** responder · documentos: cvm_resolucao_44_2021, cvm_livro_top_direito_mercado_valores_mobiliarios, cvm_livro_top_mercado_valores_mobiliarios

**Resultado automático:** PROVÁVEL: documento esperado no top-3 do chat; confira o texto

**Conferência manual:** [ ] contém a informação  

| # | Documento | Página | Distância | Chat |
| :-: | :-- | :-- | :-: | :-: |
| 1 | cvm_livro_top_mercado_valores_mobiliarios ✓ | p. 178 | 0.342 | * |
| 2 | cvm_livro_top_direito_mercado_valores_mobiliarios ✓ | p. 241 | 0.352 | * |
| 3 | cvm_livro_top_direito_mercado_valores_mobiliarios ✓ | p. 719-720 | 0.354 | * |
| 4 | cvm_livro_top_direito_mercado_valores_mobiliarios ✓ | p. 706 | 0.372 |  |
| 5 | cvm_livro_top_direito_mercado_valores_mobiliarios ✓ | p. 698 | 0.375 |  |

> **1.** 7. Aquisição de uma empresa por outra sem prévia negociação com a administração ou os acionistas, geralmente atra vés de transação em bolsa. 8. É um mecanismo de proteção ao acionista minoritário que obriga o adquirente de controle a fazer oferta pública de aquisição a todos os acionistas, asseguran…

> **2.** 3.4 Esse é o critério adotado pelas instruções da CVM e consagrado pelo art. 155 da Lei no 6.404, de 15 de dezembro de 1976: Art. 155 (...) § 1o Cumpre, ademais, ao administrador de companhia aberta, guardar sigilo sobre qualquer informação que ainda não tenha sido divulgada para conhecimento do mer…

> **3.** Exatamente por não ter um acionista controlador, na companhia com capital pulverizado, a aquisição de controle mediante a oferta pública de compra de ações pode, muitas vezes, ser considerada uma aquisição hostil, tendo em vista que, possivelmente, o controle desse tipo de companhia é gerencial, ou …

> **4.** . 16 Nos termos do §4o do artigo 109 do RICADE. 17 Conforme definição prevista nos artigos 2°, II, da Instrução CVM 361, e 4o, "§6o, da Lei das S.A.: §6o O acionista controlador ou a sociedade controladora que adquirir ações da companhia aberta sob seu controle que elevem sua participação, direta ou…

> **5.** No entanto, fica o Diretor de Relações com Investidores da companhia objeto obrigado a divulgar imediatamente a existência de negociações acerca da potencial oferta, caso a informação escape ao controle dos envolvidos ou se verifique oscilação atípica na cotação, preço ou quantidade negociada dos va…

## N3.3 (N3, sem filtro)

**Pergunta:** Quero começar com pouco dinheiro na bolsa. Que diferença faz, em proteção ao acionista minoritário, comprar ações de uma empresa do Novo Mercado em vez de uma empresa de outro segmento?

**Esperado:** responder · documentos: b3_regulamento_novo_mercado, cvm_livro_top_mercado_valores_mobiliarios

**Resultado automático:** PROVÁVEL: documento esperado no top-3 do chat; confira o texto

**Conferência manual:** [ ] contém a informação  

| # | Documento | Página | Distância | Chat |
| :-: | :-- | :-- | :-: | :-: |
| 1 | cvm_livro_top_mercado_valores_mobiliarios ✓ | p. 275-276 | 0.326 | * |
| 2 | cvm_livro_top_direito_mercado_valores_mobiliarios | p. 1310 | 0.361 | * |
| 3 | cvm_livro_top_mercado_valores_mobiliarios ✓ | p. 278 | 0.372 | * |
| 4 | cvm_livro_top_mercado_valores_mobiliarios ✓ | p. 277-278 | 0.387 |  |
| 5 | cvm_livro_top_mercado_valores_mobiliarios ✓ | p. 105 | 0.399 |  |

> **1.** Este novo ambiente de gestão profissional faz com que o investidor veja os segmentos de listagem diferenciados como um criador de valor na empresa, influenciando positivamente os resultados que espera obter com seu investimento. 8.5.1. Novo Mercado A principal inovação do Novo Mercado, em relação à …

> **2.** 14. Um dos princípios fundamentais adotados pelo Novo Mercado é o tratamento igualitário dos acionistas de Companhias que tenham aderi da a tal segmento no contexto de ofertas públicas de aquisição em razão de alienação de controle. O objetivo é que, diante de tal situação, todos os acionistas não c…

> **3.** O Bovespa Mais possibilita a realização de captações menores se comparadas ao Novo Mercado, mas suficientes para financiar o seu projeto de crescimento. As empresas listadas no Bovespa Mais tendem a atrair investidores que visualizem um potencial de desenvolvimento mais acentuado no negócio. As ofer…

> **4.** Nível 2: Neste segmento, as exigências são maiores do que no Nível 1. Além daquelas citadas anteriormente, devem ser observadas: . O segmento de listagem Nível 2 é similar ao Novo Mercado, porém com algumas exceções. As empresas listadas têm o direito de manter ações preferen ciais (PN). No caso de …

> **5.** Como seu principal fator de risco é a variação nos preços das ações que compõem sua carteira, são mais indicados para objetivos de investimento de longo prazo e que su portem uma maior exposição a riscos em troca de uma expectativa de rentabilidade mais elevada. Ações - Mercado de Acesso Caso o anex…

## N3.4 (N3, sem filtro)

**Pergunta:** Estou em dúvida entre um fundo imobiliário e comprar um imóvel para alugar. O que muda em liquidez, diversificação e custos, segundo o material da CVM?

**Esperado:** responder · documentos: cvm_caderno_06_fundos_imobiliarios, cvm_livro_top_planejamento_financeiro_pessoal

**Resultado automático:** PROVÁVEL: documento esperado no top-3 do chat; confira o texto

**Conferência manual:** [ ] contém a informação  

| # | Documento | Página | Distância | Chat |
| :-: | :-- | :-- | :-: | :-: |
| 1 | cvm_livro_top_planejamento_financeiro_pessoal ✓ | p. 151-152 | 0.324 | * |
| 2 | cvm_caderno_06_fundos_imobiliarios ✓ | p. 7-8 | 0.345 | * |
| 3 | cvm_livro_top_planejamento_financeiro_pessoal ✓ | p. 149 | 0.345 | * |
| 4 | cvm_caderno_06_fundos_imobiliarios ✓ | p. 8-9 | 0.364 |  |
| 5 | cvm_caderno_06_fundos_imobiliarios ✓ | p. 7 | 0.369 |  |

> **1.** Uma maneira mais simples de investir em imóveis, correndo riscos semelhantes, é comprar cotas de um fundo imobiliário. Vantagens . Custo reduzido de investimento (é possível investir pequenas e médias quantias) . Baixo custo . Maior diversificação . Isenção do imposto de renda sobre rendimentos pago…

> **2.** Além disso, os custos da administração dos investimentos do Fundo são diluídos entre todos os cotistas, na proporção de suas participações. • Diversificação Os Fundos de Investimento Imobiliário representam uma oportunidade de diversificação de aplicações para o investidor, pois os rendimentos de su…

> **3.** Investimento em fundos imobiliários também agrada ao perfil de muitos investidores, sendo uma boa alternativa de diversificação de carteira. Os rendimentos são pagos periodicamente, isentos do IR (se o fundo atender às exigências da Receita Fe deral). O investidor conta, ainda, com a possibilidade d…

> **4.** • Possibilidade de Fracionar o Investimento Caso o investidor necessite utilizar parte dos recursos aplicados, não precisará, como no investimento direto em imóveis, liquidar todo o seu investimento, podendo vender no mercado secundário, caso líquido, apenas a quantidade de cotas suficientes para su…

> **5.** II.2) VANTAGENS Quais as vantagens do Fundo de Investimento Imobiliário? • Acesso ao Mercado Imobiliário O Fundo de Investimento Imobiliário permite a formação de uma carteira composta de empreendimentos imobiliários ou de ativos ligados a esse setor, os quais, pelo volume de recursos envolvidos, nã…

## N3.5 (N3, sem filtro)

**Pergunta:** Quero investir numa empresa e ver se ela é confiável. Que documento obrigatório devo consultar, onde encontro e que informações ele traz?

**Esperado:** responder · documentos: cvm_resolucao_80_2022, cvm_caderno_01_o_que_e_a_cvm

**Resultado automático:** PROVÁVEL: documento esperado no top-3 do chat; confira o texto

**Conferência manual:** [ ] contém a informação  

| # | Documento | Página | Distância | Chat |
| :-: | :-- | :-- | :-: | :-: |
| 1 | cvm_caderno_03_fundos_investimento | p. 30-31 | 0.310 | * |
| 2 | cvm_caderno_01_o_que_e_a_cvm ✓ | p. 23 | 0.345 | * |
| 3 | cvm_caderno_01_o_que_e_a_cvm ✓ | p. 22-23 | 0.347 | * |
| 4 | bcb_caderno_gestao_financas_pessoais | p. 63 | 0.367 |  |
| 5 | cvm_livro_top_direito_mercado_valores_mobiliarios | p. 764 | 0.372 |  |

> **1.** Solicite informações e verifique as regras da Receita Federal. 2 antes de investir 2.1. INFORMAÇÕES E DOCUMENTOS A base de uma decisão de investimento consciente é a informação. Por essa razão é exigido que os fundos divulguem informações de forma abrangente, equitativa e simultânea para todos, incl…

> **2.** Todas as companhias abertas devem possuir um site de Relações com Investidores Na página de Relações com Investidores das empresas também é óssível acessar esses documentos e, muitas vezs, informações adicionais. Além disso, são oferecidos canais de comunicação para que o investidor entre em contato…

> **3.** ceiras, atos e fatos relevantes, comunicados ao mercado, formulário de referência, prospectos, atas de assembleias e estatuto social. Instituído em 2009, o formulário de referência é um documento riquíssimo em informações sobre a empresa: atividades principais, fatores de risco, estrutura de capital…

> **4.** O mais importante é, antes de qualquer aplicação, verificar a solidez das instituições envolvidas e pesquisar nos documentos correspondentes (Regulamento do Fundo, Prospecto da Oferta Pública etc.) qual o perfil de risco assumido. OBJETIVOS DO INVESTIMENTO O que você pretende fazer com o seu dinheir…

> **5.** . Por essa razão, dada a magnitude e alcance da oferta, que pode atingir irrestritamente todo e qualquer investidor, inclusive pessoas comuns que não sejam considerados investidores qualificados e não tenham qualquer prática ou experiência no investimento em ações, faz-se necessária a análise dos do…

## N4.1 (N4, sem filtro)

**Pergunta:** Como o FGC garante meus títulos do Tesouro Direto se a corretora quebrar?

**Esperado:** corrigir_premissa · documentos: cmn_resolucao_4222_fgc, tesouro_direto_regulamento

**Nota:** Premissa falsa: o FGC não cobre títulos públicos.

**Resultado automático:** PROVÁVEL: documento esperado no top-3 do chat; confira o texto

**Conferência manual:** [ ] contém a informação  

| # | Documento | Página | Distância | Chat |
| :-: | :-- | :-- | :-: | :-: |
| 1 | tesouro_direto_regulamento ✓ | p. 25 | 0.366 | * |
| 2 | tesouro_direto_regulamento ✓ | p. 4 | 0.373 | * |
| 3 | cvm_livro_top_planejamento_financeiro_pessoal | p. 96 | 0.379 | * |
| 4 | tesouro_direto_regulamento ✓ | p. 5-6 | 0.385 |  |
| 5 | cvm_livro_top_planejamento_financeiro_pessoal | p. 68 | 0.387 |  |

> **1.** no Tesouro Direto é instruída pelo Agente de Custódia mediante solicitação do Investidor, seu cliente, por meio dos sistemas da B3 e são efetivados no Selic, onde os Títulos se encontram custodiados, de forma escritural. 109. Para fins de publicidade e eficácia perante terceiros, a constituição de Ô…

> **2.** sistemas do Tesouro Direto. Bloqueio de Títulos em Garantia - processo em que os Títulos disponíveis do Investidor no Tesouro Direto são bloqueados uma vez entregues em garantia para assegurar operações do próprio Investidor compensadas e liquidadas nas Câmaras da B3, com o adequado registro do bloq…

> **3.** Emissor Bancos comerciais, múltiplos, de desenvolvimento, de investimento, sociedades de crédito, financiamento e investimento e caixas econômicas. Garantia do FGC Limitada a R$ 20 milhões por titular, englobando o principal mais os juros do total de créditos de cada pessoa contra a mesma instituiçã…

> **4.** Ônus e Gravames. Desbloqueio de Títulos em Garantia - processo em que os Títulos do Investidor utilizados em garantias de operações do próprio Investidor compensadas e liquidadas nas Câmaras da B3 são disponibilizados nas Contas de Custódia do Investidor, mantendo-se a titularidade original do Inves…

> **5.** Os títulos emitidos por instituições financeiras são protegidos pelo Fundo Garantidor de Créditos (FGC), observados os limites vigentes. Saiba mais a respeito desse assunto no item 3.1.1.2.1 deste volume. Os títulos privados emitidos por instituições não financeiras, como debêntures e notas promissó…

## N4.2 (N4, sem filtro)

**Pergunta:** Qual é a alíquota de imposto de renda sobre o lucro com criptomoedas?

**Esperado:** declarar_fora_da_base · documentos: nenhum (ausência intencional)

**Nota:** Fora do corpus: o sistema deve dizer que a base não cobre o tema.

**Resultado automático:** ATENÇÃO: 3 trecho(s) passariam para o chat; confira se são pertinentes

**Conferência manual:** [ ] contém a informação  

| # | Documento | Página | Distância | Chat |
| :-: | :-- | :-- | :-: | :-: |
| 1 | cvm_livro_top_planejamento_financeiro_pessoal | p. 213-214 | 0.388 | * |
| 2 | cvm_livro_top_planejamento_financeiro_pessoal | p. 231-232 | 0.404 | * |
| 3 | cvm_livro_top_planejamento_financeiro_pessoal | p. 221-222 | 0.416 | * |
| 4 | cvm_livro_top_planejamento_financeiro_pessoal | p. 228 | 0.422 |  |
| 5 | cvm_livro_top_planejamento_financeiro_pessoal | p. 231 | 0.424 |  |

> **1.** Assim, nas alienações de imóveis por valor superior ao valor de aquisição, a base de cálculo do imposto de renda é o ganho de capital. Sobre o ganho de capital, aplica-se a alíquota de 15%. Ganhos acima de R$ 5 milhões são tributados de acordo com uma tabela progressiva que varia entre 15% e 22,5%. …

> **2.** Em geral, outros tipos de sorteio, como concursos artísticos, científicos etc., são tributados na fonte pela tabela progressiva mensal, que varia de 0 a 27,5%. Esses rendimentos são classificados como rendimentos tributáveis. Assim, o imposto é recolhido mensalmente a título de antecipação do impost…

> **3.** Os resultados, positivos ou negativos, apurados em cada contrato corresponderão à soma algébrica dos ajustes diários incorridos entre as datas de abertura e de encerramento ou de liquidação do contrato, total ou parcial. O resultado é apurado na liquidação da operação, parcial ou total. V. Alíquotas…

> **4.** Os ganhos auferidos na alienação de cotas realizada em bolsa são tributados como aplicações de renda variável: cabe ao próprio investidor fazer o recolhimento do imposto de renda por meio de DARF. Porém, não se aplica a isenção para ganhos decorrentes de alienações de até R$ 20.000,00 ao mês de cota…

> **5.** Sobre o ganho de capital, aplica-se a alíquota de 15%. Ganhos de capital acima de R$ 5 milhões são tributados de acordo com uma tabela progressiva que varia entre 15% e 22,5%. EXEMPLO: o pai decide doar um imóvel pelo valor de R$ 2 milhões ao seu filho. O imóvel consta em sua Declaração de Ajuste An…

## N4.3 (N4, sem filtro)

**Pergunta:** Segundo a Instrução CVM 555, quais são as regras de cotas para fundos de investimento?

**Esperado:** corrigir_premissa · documentos: cvm_caderno_03_fundos_investimento

**Nota:** Norma revogada pela Res. CVM 175/2022; o Caderno CVM 3 é anterior (teste de atualidade).

**Resultado automático:** FALHOU: documento esperado não aparece com distância <= limiar; trocar ou reformular

**Conferência manual:** [ ] contém a informação  

| # | Documento | Página | Distância | Chat |
| :-: | :-- | :-- | :-: | :-: |
| 1 | cvm_livro_top_direito_mercado_valores_mobiliarios | p. 631 | 0.263 | * |
| 2 | cvm_livro_top_direito_mercado_valores_mobiliarios | p. 616 | 0.278 | * |
| 3 | cvm_livro_top_direito_mercado_valores_mobiliarios | p. 571 | 0.279 | * |
| 4 | cvm_livro_top_direito_mercado_valores_mobiliarios | p. 1205-1206 | 0.282 |  |
| 5 | cvm_livro_top_direito_mercado_valores_mobiliarios | p. 625 | 0.282 |  |

> **1.** Por fim, entendemos ser conveniente mencionar os dois diferentes tipos de fundos de investimento previstos na ICVM 555. O primeiro tipo diz respeito aos Fundos de Investimento em si, ou seja, aqueles que podem investir nos ativos financeiros e operações diretamente, conforme suas respectivas classes…

> **2.** O comando da ICVM 555 quanto à sua aplicabilidade geral a todos os fundos de investimento registrados junto à CVM deve ser interpretado com cautela. A Instrução regula, precipuamente, fundos de investimento cujas carteiras de investimento diferem de forma relevante dos demais fundos regulados por ou…

> **3.** As cotas de fundos de investimentos abertos, por poderem ser resgatadas a qualquer momento, não podem ser objeto de cessão ou transferência, exceto nos casos de (i) decisão judicial ou arbitral; (ii) operações de cessão fiduciária; (iii) execução de garantia; (iv) sucessão universal; (v) dissolução …

> **4.** 46. Apesar disto, nada impede que a CVM estabeleça regras especiais de concessão au tomática de registro de funcionamento e de distribuição de cotas de fundos de investi mento, ou mesmo para sua dispensa, inclusive condicionando a concessão de tais favores ao número máximo de destinatários e ao valo…

> **5.** A qualificação dos investidores nas categorias acima descritas é relevante não só para a ICVM 555, mas para todo o mercado de capitais. Isso porque, a aquisição dos demais fundos (por exemplo, fundos estruturados) e outros ativos também pode estar restrita apenas a um determinado público-alvo, com o…
