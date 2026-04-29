# 05 — Estratégia de IA

> **Tese central:** ML clássico onde a IA **decide**, GenAI onde a IA **comunica**.
> Em saúde, essa separação não é estilística — é regulatória, financeira e de segurança.

## Resumo executivo

| Dimensão | ML clássico | GenAI / LLM |
|---|---|---|
| Saída | Probabilidade, classe, score | Texto, raciocínio, resumo |
| Auditabilidade | Alta (SHAP, importâncias, calibração) | Baixa nativa, exige instrumentação |
| Custo de inferência em escala | Centavos por milhão | Ordens de grandeza maior |
| Determinismo | Sim | Não, sem amarração |
| Risco de alucinação | Zero | Real |
| Encaixe regulatório | Forte | Aceitável só com guardrail |
| **Onde aplicar aqui** | Risco, predição, propensão, alocação | Mensagem, copiloto, RAG, extração |

## Onde ML clássico ganha

### 1. Estratificação de risco
- **Modelo:** XGBoost / LightGBM em features tabulares (wearable agregado, claims, EHR estruturado)
- **Saída:** classe de risco (verde/amarelo/vermelho) + probabilidade calibrada (Platt/Isotônica)
- **Explicabilidade:** SHAP por predição → lista as 3-5 features que mais empurraram o paciente para aquela classe
- **Por que não LLM:** dado tabular com forte sinal numérico; LLM teria custo proibitivo, latência maior e zero auditabilidade — sem ganho de qualidade

### 2. Predição de evento clínico
- **Modelos por janela:** descompensação em 30/60/90 dias, internação em 90 dias, queda em 30 dias (idosos)
- **Treino supervisionado** com horizonte temporal e validação **time-based**, não k-fold ingênuo
- **Calibração** é mais importante que acurácia bruta — operação clínica precisa de probabilidade confiável para definir gatilhos

### 3. Propensão a engajamento
- **Modelo:** classificador binário ou de uplift (se eu mando push agora vs não mando, o que muda?)
- **Saída:** probabilidade de resposta por canal × horário × tom
- **Treina-se com eventos de engajamento históricos** — leitura, clique, ação executada
- **Uso:** orquestrador escolhe canal/horário com maior expected response

### 4. Modelagem de sinistralidade
- **Modelo:** regressão/Gradient Boosting para custo médico esperado por coorte e por intervenção
- **Saída:** custo esperado com e sem programa preventivo → ROI direto
- **Uso financeiro:** prioriza onde investir (qual coorte tem maior delta esperado)

## Onde GenAI ganha

### 1. Comunicação personalizada com o beneficiário
- **Input do LLM:** persona + nível de risco + 3 features explicativas SHAP + canal alvo + tom
- **Output:** mensagem em linguagem natural, no tom certo, com chamada de ação clara
- **Por que não template:** template não personaliza nuance ("vimos que sua pressão sobe à noite" só funciona se a explicabilidade do modelo virou linguagem). LLM faz isso bem.

### 2. Copiloto clínico
- **Caso:** médico abre prontuário do paciente → copiloto resume últimos 12 meses, destaca mudanças relevantes, sugere hipóteses
- **Padrão:** sempre **com citação** ao trecho do prontuário que originou a afirmação
- **Saída sempre revisável** — médico aceita, edita ou rejeita; feedback alimenta avaliação contínua

### 3. RAG sobre protocolos e diretrizes
- **Conteúdo indexado:** protocolos clínicos da Unimed, diretrizes de sociedades médicas (SBC, SBD, SBGG), bulários, manuais ANS
- **Consulta:** médico pergunta em linguagem natural, recebe resposta com **citações verificáveis**
- **Não substitui referência** — facilita o acesso

### 4. Extração de dados não estruturados
- **Caso:** anamnese livre → estrutura em campos FHIR. Áudio de call center → transcrição + categorização.
- **Output validado** por schema antes de virar dado de produção

### 5. Chatbot de engajamento
- **Caso:** beneficiário pergunta dúvida simples no app
- **Limites:** allowlist de tópicos, recusa firme em diagnóstico, escalonamento humano configurado por intent

## Critério de decisão (quando usar cada um)

```
A tarefa é classificação/regressão sobre dado estruturado?
├── Sim → ML clássico
│
└── Não, é texto/linguagem/raciocínio?
    ├── Existe dado tabular auxiliar relevante?
    │   └── ML decide o que, LLM compõe o como
    └── Tarefa puramente linguística → GenAI
        └── Sempre com guardrail, citação e validação
```

## Stack de modelos

### ML clássico
- **Frameworks:** scikit-learn, XGBoost, LightGBM, CatBoost
- **Validação:** holdout temporal + cross-validation time-based
- **Interpretabilidade:** SHAP (por predição e global), Partial Dependence, calibração visual
- **Auditoria de fairness:** Aequitas / Fairlearn — gate de promoção
- **Servir:** BentoML, FastAPI, ou serviço gerenciado (SageMaker / Vertex AI)
- **Feature Store:** Feast — garante que treino e inferência usam mesma feature

### GenAI
- **Gateway provider-neutral:** OpenRouter no protótipo (default `anthropic/claude-haiku-4.5`,
  trocável para `openai/gpt-4o-mini`, `google/gemini-flash-1.5`, etc. via env var).
  Em produção, LiteLLM ou camada própria com a mesma ideia, e roteamento por tarefa
  (Haiku-class para mensagem, Sonnet/Opus para copiloto clínico complexo).
- **Provedor secundário:** open-weights via vLLM para cenários de soberania ou custo
- **Roteamento:** LiteLLM ou camada própria — escolhe modelo por tarefa, custo e SLA
- **Cache semântico** para perguntas recorrentes — corta custo significativamente
- **Avaliação contínua:** golden set de exemplos validados clinicamente, regressão automática a cada mudança

## MLOps

### Ciclo de vida do modelo

```
Concepção → Dataset → Treino → Avaliação clínica e fairness → Aprovação humana → Deploy canário → Monitoria → Retreino
```

- **Versionamento:** Git para código, MLflow para modelos e experimentos
- **Registry:** modelos só vão a produção via promoção explícita com aprovação clínica e técnica
- **Deploy:** canário com fração crescente, comparado contra modelo atual
- **Rollback:** automático em queda de métrica clínica ou aumento de viés
- **Lineage:** todo modelo em produção tem rastreio até dataset, código e configuração

### Monitoramento

| O que se monitora | Sinal | Ação |
|---|---|---|
| Drift de input | PSI / KS por feature | Alerta + investigação |
| Drift de output | Distribuição de classe ao longo do tempo | Alerta |
| Performance offline | Desempenho em janela rotulada recente | Alerta + retreino |
| Fairness | FPR/FNR por subgrupo | Bloqueio se ultrapassar limiar |
| Latência | p50/p95/p99 | Auto-scaling |
| Erros | Taxa de erro por endpoint | Alerta |
| Qualidade do GenAI | Avaliação LLM-as-judge + amostra humana | Revisão de prompt / modelo |

### Gates de promoção
Modelo só vai a produção se:
1. Desempenho técnico ≥ baseline + tolerância
2. Fairness sem desvio inaceitável por subgrupo
3. Calibração validada
4. Aprovação do time clínico para casos sensíveis
5. Documentação atualizada (model card)

## Guardrails de GenAI

| Camada | O que faz |
|---|---|
| **Pré-prompt** | PII redaction, sanitização, allowlist de tópicos |
| **Prompt** | Templates parametrizados, instruções de segurança, contexto separado de instrução |
| **Modelo** | Provider com política de não-treino sobre prompts; região e DPA contratualizados |
| **Pós-resposta** | Validação de schema, regex de PII residual, classificador de toxicidade, validador clínico |
| **Auditoria** | Log imutável de prompt + resposta + decisão, por usuário, por finalidade |
| **Humano no loop** | Toda saída clínica passa por médico antes de afetar o cuidado |

## Questão norteadora — "Como incentivar o uso de IA na personalização"

Resposta direta:

1. **Mostrar valor para o profissional primeiro.** Médico que vê o copiloto resumir 50 páginas de prontuário em 30 segundos vira advogado interno da plataforma.
2. **Transparência radical.** Cada decisão da IA tem explicação acessível ("o modelo destacou estes 3 fatores"). Caixa-preta gera resistência.
3. **Mensuração clínica visível.** Painéis mostrando "estes pacientes evitaram internação após intervenção" — incentivo é resultado mensurável.
4. **Guardrails que protegem o usuário.** A confiança vem do limite explícito ("isto não substitui orientação médica"), não da promessa.
5. **Iteração rápida com clínicos.** Time clínico no design de prompts, no rótulo de dataset, no model card.

## Anti-padrões evitados nesta proposta

1. **Usar LLM para classificação tabular** — caro, lento, opaco, sem ganho.
2. **GenAI prescrevendo conduta** — risco regulatório e clínico inaceitável.
3. **Modelo único multitask para tudo** — fica medíocre em todas. Modelos especializados por caso.
4. **Métrica única (AUC) como gate** — em saúde, calibração e fairness importam tanto quanto.
5. **"Vamos coletar dado e ver no que dá"** — sem hipótese clínica, modelo vira firula.

## Sumário

A estratégia escolhe o tipo certo de IA para cada problema, com auditabilidade onde decide e com guardrails onde se comunica. O resultado é uma plataforma onde **a IA aumenta o profissional de saúde sem substituí-lo**, **comunica com o beneficiário no tom certo**, e **é auditável o suficiente para passar em fiscalização** — clínica, regulatória ou interna.
