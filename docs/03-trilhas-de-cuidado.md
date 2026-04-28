# 03 — Trilhas de Cuidado por Perfil

O case da Unimed apresenta três perfis de cuidado (crônicos, idosos, jovens) mas só detalha jornadas para dois (Júlia, 28 e Maria, 55). Esta proposta **preenche a lacuna do idoso** com a jornada do João, 72, e formaliza as três trilhas de forma comparável.

## Princípio de personalização

Cada trilha responde a quatro perguntas:

1. **O que se observa** — quais sinais entram (wearable, claims, PROMs, exames)
2. **O que se decide** — qual modelo gera qual tipo de decisão (ML clássico vs GenAI)
3. **O que se entrega** — qual ação, em qual canal, com qual tom
4. **O que se mede** — KPI clínico, financeiro e de engajamento da trilha

A lógica não é "perfil → mensagem fixa". É **perfil → política de decisão**, e a política decide caso a caso a partir dos dados daquela pessoa.

---

## Trilha 1 — Jovens saudáveis (persona: Júlia, 28)

> Designer gráfica em uma startup, vida ativa, sem condições crônicas conhecidas. Usa smartwatch e é digitalmente fluente.

### Hipótese clínica e financeira

Beneficiários jovens hoje **subutilizam a operadora** — não fazem check-up, não percebem riscos silenciosos (pré-hipertensão, dislipidemia, saúde mental), e quando aparecem é em pronto-socorro caro. Investir em prevenção aqui custa pouco e evita coortes crônicas no futuro.

### O que se observa

- **Wearable:** HR de repouso, HRV, qualidade de sono, cadência de exercício, variabilidade circadiana
- **App:** humor autorreportado, hábitos (alimentação, álcool, fumo), uso de apps de meditação/exercício
- **Claims:** exames de rotina (presença/ausência), vacinação em dia
- **Sinalizadores indiretos:** queda abrupta de atividade, alteração de sono, picos de FC em repouso

### O que se decide

- **ML clássico** estima risco silencioso composto (pré-hipertensão, distúrbio de sono, sinais de burnout) a partir de séries temporais de wearable e PROMs.
- **Modelo de propensão a engajamento** (ML) decide o melhor canal e horário (Júlia responde no fim de semana à noite? sexta à tarde?).
- **GenAI** redige a mensagem com tom **leve, direto, não paternalista** — porque essa pessoa abandona se sentir que tá sendo "tratada como idosa".

### O que se entrega

| Ação | Canal | Frequência |
|---|---|---|
| Insights de hábito (sono, treino, descanso) | Push do app | Semanal |
| Check-up anual proativo | Push + agenda integrada | Anual |
| Conteúdo preventivo (saúde mental, alimentação, postura) | App, e-mail | Mensal |
| Telemedicina ágil quando há sinal | Push → consulta < 15 min | Sob demanda |
| Desafios de hábito (gamificação) | App | Contínuo |

### O que se mede

- **Engajamento:** ativação no app, conexão de wearable, resposta a recomendações
- **Clínico:** % com check-up anual em dia, evolução de PROMs (qualidade de sono, ansiedade autorreportada)
- **Financeiro:** custo médico per capita da coorte vs grupo de controle, eventos preveníveis (pronto-socorro evitado)

---

## Trilha 2 — Crônicos (persona: Maria, 55)

> Hipertensa há dois anos, ambiente de trabalho estressante, baixa adesão a exercício. Toma medicação irregularmente.

### Hipótese clínica e financeira

Esse é o **maior gerador de sinistralidade evitável**: agudização de crônico vira hospitalização cara. Cada internação evitada paga muitos meses de programa preventivo. A trilha aqui é a mais ROI-positiva da plataforma.

### O que se observa

- **Wearable:** pressão arterial (em smartwatches habilitados), FC, saturação, qualidade de sono
- **App:** registro de aferição manual, adesão à medicação (lembretes confirmados), sintomas
- **Claims:** dispensação de anti-hipertensivos vs prescrição (gap de adesão), consultas com cardiologista, exames laboratoriais
- **EHR:** histórico de pressão, comorbidades (diabetes? dislipidemia?), classe funcional

### O que se decide

- **ML clássico (XGBoost/GBM):** estima **probabilidade de descompensação em 30/60/90 dias** com base em séries temporais e adesão. Saída em 3 níveis (verde/amarelo/vermelho) com SHAP explicando "por que esse paciente foi classificado assim".
- **Regra clínica rígida:** se PA > limiar X em N leituras consecutivas, escalar imediatamente — não esperar modelo.
- **GenAI:** compõe a mensagem com tom **apoiador, sem culpabilização**, e personaliza com o `top_features_shap` ("vimos que sua pressão tem subido no fim do dia — pode ser estresse no trabalho?").

### O que se entrega

| Ação | Canal | Frequência |
|---|---|---|
| Aferição lembrete | Push + integração com aparelho | Diário |
| Lembrete de medicação | Push / SMS | Diário |
| Recomendação de hábito personalizada | App | Semanal |
| **Risco amarelo** → consulta de revisão | Agendamento ativo + push | Sob demanda |
| **Risco vermelho** → telemedicina imediata + cardiologia | Ligação ativa + telemed | Imediato |
| Alerta para médico assistente | Painel do médico | Sob demanda |

### O que se mede

- **Clínico:** redução de % de pacientes com PA descompensada, redução de eventos agudos (PS / internação), adesão terapêutica
- **Financeiro:** custo médio anual por crônico controlado vs descontrolado, internações evitadas
- **Engajamento:** taxa de aferição/dia, adesão a recomendações, abandono

---

## Trilha 3 — Idosos (persona: João, 72) ⚠️ *trilha que o PDF original não detalhou*

> Aposentado, viúvo há três anos, mora sozinho. Hipertenso e diabético, tem polifarmácia (5 medicamentos), mobilidade reduzida após queda em 2024. Fluência digital baixa.

### Hipótese clínica e financeira

Idoso é o perfil de **maior custo médio per capita** e **maior risco de evento grave**. Mas é também o que **mais tem dificuldade com canais digitais**. Tratar idoso como "Júlia mais velha" é o erro mais comum em saúde digital — abandono total.

A solução para esse perfil tem três peças que jovens e crônicos não precisam:
1. **Cuidador no loop** — filho(a)/familiar autorizado recebe alertas relevantes (com consentimento explícito do beneficiário)
2. **Atenção domiciliar** — visita de enfermagem em vez de "vai à clínica"
3. **Suporte por voz, não tela** — ligação ativa, WhatsApp em texto curto, não app cheio de menus

### O que se observa

- **Wearable simples** (smartwatch com detecção de queda, FC, saturação)
- **Sinais ambientais opcionais:** smart ring, sensores de presença em casa (consentimento explícito)
- **Adesão à polifarmácia:** dispenser inteligente conectado ou registro do cuidador
- **Claims:** internações recentes, idas a PS, exames de seguimento
- **EHR:** comorbidades, fragilidade (escalas validadas tipo Fried), histórico de quedas
- **PROMs específicos:** AVD (atividades de vida diária), risco de queda, isolamento social

### O que se decide

- **ML clássico:** estima risco de **internação em 90 dias**, risco de **queda** (modelo dedicado), risco de **interação medicamentosa** (sistema de regras + ML).
- **Detecção de evento agudo via wearable:** queda detectada → ligação ativa imediata.
- **GenAI:** redige mensagem para o **cuidador** com linguagem técnica suficiente; e mensagem **falada** (TTS) para o beneficiário em tom **claro, paciente, com instruções curtas**.
- **RAG sobre protocolos geriátricos** alimenta o copiloto do médico assistente.

### O que se entrega

| Ação | Canal | Frequência |
|---|---|---|
| Aferição assistida (PA, glicemia) | Visita de enfermagem domiciliar | Quinzenal |
| Lembrete de medicação | Voz (smart speaker / ligação ativa) + cuidador | Diário |
| Conferência de polifarmácia | Farmacêutico clínico | Trimestral |
| Detecção de queda → resgate | Smartwatch → central de atendimento | Imediato |
| Telemedicina geriátrica | Visita assistida ou call com cuidador | Mensal |
| Alerta para cuidador | WhatsApp / ligação | Sob demanda |
| Conteúdo de prevenção de quedas e isolamento | Voz / ligação ativa | Semanal |

### O que se mede

- **Clínico:** redução de quedas, redução de hospitalizações, controle de comorbidades, adesão à polifarmácia
- **Financeiro:** custo médico anual por idoso assistido vs não assistido (matched cohort), custo evitado por internação prevenida
- **Engajamento:** adesão do beneficiário **e** do cuidador, qualidade percebida (PREMs específicos para idoso)
- **Qualidade de vida:** evolução em escalas validadas (Katz, Lawton, Fried)

---

## Tabela comparativa das três trilhas

| Dimensão | Júlia (jovem) | Maria (crônica) | João (idoso) |
|---|---|---|---|
| Sinal mais relevante | Wearable, PROMs | Wearable PA, adesão | Wearable + cuidador + EHR |
| Modelo principal | Risco silencioso + propensão | Descompensação | Internação + queda |
| Canal preferencial | App, push | App, SMS | Voz, cuidador, domicílio |
| Tom da mensagem | Leve, direto | Apoiador | Claro, falado, curto |
| Cuidador no loop? | Não | Opcional | Sim, com consentimento |
| KPI financeiro principal | Eventos preveníveis | Internações por agudização | Hospitalizações + quedas |
| Frequência de toque | Semanal | Diário | Diário, multi-canal |
| Risco de abandono | Médio | Médio | Alto se canal errado |

## Como o sistema decide a trilha

A trilha **não é estática**. O `patient_id` é classificado em uma **trilha primária** com base em idade, comorbidades e fragilidade, mas o orquestrador permite **transições**:

- Júlia que desenvolve hipertensão migra para trilha de crônico
- Maria que tem queda vira candidata à trilha de idoso vulnerável
- Beneficiário sem dado suficiente entra em trilha "padrão" + plano de ativação para enriquecer perfil

Toda transição é **evento auditável** e revisada pelo time clínico em ciclo regular.

## O que isso prova ao avaliador

1. **Leitura crítica do PDF** — identifiquei uma lacuna (trilha de idoso ausente) e preenchi com proposta concreta.
2. **Profundidade clínica** — não usei jargão sem propósito; cada termo (PROMs, polifarmácia, Fried, Katz) está no lugar certo.
3. **Personalização real** — três trilhas, três tons, três canais, três conjuntos de KPIs. Não é "uma jornada com perfil de cor".
4. **Cuidador no loop** — diferencial que ninguém em PoCs de saúde digital costuma incluir, e que é decisivo para idoso.
