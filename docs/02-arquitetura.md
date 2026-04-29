# 02 — Arquitetura Ponta a Ponta

> Este documento apresenta **duas arquiteturas** lado a lado:
>
> 1. **Arquitetura atual** — o que existe hoje no protótipo, executável.
> 2. **Arquitetura-alvo** — o que esta plataforma se torna em produção para 4,6M de beneficiários.
>
> Para cada uma: **o que atende, qual problema resolve, como faz e por que faz**. O detalhamento técnico (camadas, ADRs, capacidade) vem depois.

---

## Arquitetura atual (protótipo)

### Diagrama

```mermaid
flowchart LR
    subgraph CLIENTES[Quem chama]
        C1[curl / Swagger]
    end

    subgraph PROTO[Protótipo - fatia vertical]
        direction TB
        A1[FastAPI<br/>/score /event /health]
        A2[XGBoost<br/>+ SHAP local]
        A3[Orquestrador<br/>regra perfil x risco]
        A4[OpenRouter<br/>provider-neutral]
        A5[(Modelo treinado<br/>artifacts/model.joblib)]
        A6[(Dataset sintético<br/>data/beneficiarios.parquet)]

        A1 --> A2
        A2 -.usa.-> A5
        A2 --> A3
        A3 --> A4
        A4 --> A1
        A6 -.alimentou treino.-> A5
    end

    subgraph FALLBACK[Falha segura]
        F1[Template determinístico]
    end

    C1 -->|JSON wearable + claims| A1
    A1 -->|JSON risco + msg| C1
    A4 -.sem API key ou erro.-> F1 --> A1
```

### Framework

| Pergunta | Resposta |
|---|---|
| **O que atende** | Demonstração executável de uma fatia vertical: dado clínico simulado entra, modelo decide risco, GenAI compõe mensagem, API entrega — em segundos, sem dependência de infraestrutura externa. |
| **Qual problema resolve** | Prova material de que a tese "ML decide, GenAI comunica" funciona em saúde. Permite que o avaliador rode `docker compose up` e veja as três personas (Júlia, Maria, João) saírem com mensagens coerentes, top features SHAP e decisão por trilha. |
| **Como faz** | Dataset sintético gerado por script com correlações clínicas plausíveis. Modelo XGBoost multiclasse treinado durante o build da imagem. SHAP TreeExplainer em cada predição. Orquestrador é tabela declarativa `(perfil × risco) → ação`. GenAI via OpenRouter (default Claude Haiku) com fallback determinístico. Tudo em um único processo Python. |
| **Por que faz assim** | Simplicidade. O objetivo do protótipo é provar que a arquitetura é factível e o fluxo de dados encaixa, não suportar produção real. Cada peça que está aqui é a versão **mínima** do que estaria em produção — e está claramente isolada para que a substituição por produção não quebre o contrato. |

### O que esta arquitetura **não atende** (intencional)

- Volume: não pretende suportar mais que dezenas de req/s
- Persistência operacional: não há OLTP, estado da jornada vive na memória
- Fluxos longos: jornadas de 90 dias não cabem em uma chamada HTTP
- Fontes reais: dados são sintéticos, não há FHIR, claims, EHR
- Conformidade operacional: validação clínica, DPIA, auditoria de acesso a PHI ficam por fora — a tese é técnica, não operacional

Tudo isso é **endereçado pela arquitetura-alvo abaixo**.

---

## Arquitetura-alvo (produção)

### Diagrama

```mermaid
flowchart LR
    subgraph FONTES[Fontes de dados]
        A1[Wearables]
        A2[App do beneficiário]
        A3[EHR / Prontuário FHIR]
        A4[Claims]
        A5[Cadastrais ANS]
    end

    subgraph INGEST[Ingestão]
        B1[Stream<br/>Kafka/Kinesis]
        B2[Batch<br/>Airflow]
    end

    subgraph STORAGE[Armazenamento]
        C1[Lakehouse<br/>bronze/silver/gold]
        C2[Feature Store<br/>online + offline]
        C3[OLTP<br/>operacional]
    end

    subgraph IA[Inteligência]
        D1[ML serving<br/>risco/predição/uplift]
        D2[GenAI gateway<br/>cache + guardrail]
        D3[MLOps<br/>drift + fairness]
    end

    subgraph ATIV[Ativação]
        E1[Orquestrador Temporal<br/>jornadas duráveis]
        E2[App / Push / SMS]
        E3[Telemedicina]
        E4[Painel médico]
    end

    subgraph MED[Mensuração]
        F1[Eventos]
        F2[BI / Dashboards]
        F3[Experimentação A/B]
    end

    A1 & A2 --> B1
    A3 & A4 & A5 --> B2
    B1 & B2 --> C1
    C1 --> C2
    C1 --> C3
    C2 --> D1
    C1 --> D2
    D1 --> E1
    D2 --> E1
    D3 -.observa.-> D1 & D2
    E1 --> E2 & E3 & E4
    E2 & E3 & E4 --> F1
    F1 --> C1
    C1 --> F2
    E1 -.controla.-> F3
    F3 -.amostragem.-> E1
```

### Framework

| Pergunta | Resposta |
|---|---|
| **O que atende** | Operação real de uma plataforma de cuidado hiper personalizado para **~4,6M beneficiários**, com quatro modos de invocação (streaming, batch, evento, sob demanda — ver [`08`](08-integracao-em-producao.md)), múltiplos canais de ativação, governança clínica e financeira. |
| **Qual problema resolve** | Cuidado preventivo personalizado em escala não cabe em código de aplicação. Resolve simultaneamente: (1) ingestão contínua de dados heterogêneos (wearable em alta frequência + EHR/claims em batch), (2) decisão clínica auditável e calibrada, (3) comunicação no canal e tom certos, (4) jornadas de 90+ dias com humano no loop, (5) mensuração rigorosa de impacto clínico e financeiro, (6) conformidade LGPD/ANS/CFM por design. |
| **Como faz** | Camadas separadas e contratualizadas — cada uma tem ADR justificando a escolha (ver [`adr/`](adr/)). Lakehouse bronze/silver/gold com FHIR canônico. Feature Store online (Redis) garante latência e elimina skew. ML serving k8s + HPA com canário e gates de fairness. GenAI gateway provider-neutral com cache semântico, redação de PII e validação de saída. Orquestração via Temporal — jornadas longas são código durável, não cron+fila. Eventos voltam ao lake fechando o ciclo de mensuração. |
| **Por que faz assim** | Cada decisão é defensiva contra um risco específico em saúde: **lakehouse** porque PHI é semi-estruturado e claims é tabular — warehouse puro sofre, lake sem ACID sofre. **FHIR** porque RN ANS 506/2022 exige interoperabilidade. **ML clássico** porque decisão clínica precisa ser auditável e barata em escala (ADR 003). **GenAI só em texto** porque alucinação clínica é risco regulatório (ADR 004). **Feature Store** porque skew treino-inferência é o bug silencioso mais caro de ML em produção (ADR 005). **Temporal** porque jornada de 90 dias não cabe em HTTP nem em cron+fila (ADR 006). **Provider-neutral** porque lock-in em LLM pode duplicar custo em escala (Doc 05). |

### Capacidade-alvo

- Streaming sustentado: ~2.700 ev/s (50 ev/dia × 4,6M ÷ 86400)
- Latência `/score` p99: < 200 ms (warm cache)
- Throughput sob demanda: 1.000 req/s com auto-scaling
- Custo de inferência ML: centavos por mil predições
- Custo GenAI: ~US$ 0,0004/mensagem em Haiku-class, ~30% menos com cache semântico
- Disponibilidade: 99,9% (SLO)

### Roadmap de chegada

Documentado em [`infra/architecture-target.md`](../infra/architecture-target.md): **Foundations** (3-4m) → **Core IA** (3-4m) → **Pilotos** (3m) → **Expansão** (6-9m) → **Otimização contínua**. Total ~18 meses até maturidade nacional.

---

## Comparação direta

| Dimensão | Atual (protótipo) | Alvo (produção) |
|---|---|---|
| Quem chama o `/score` | curl manual / Swagger | stream consumer, batch nightly, webhook EHR, painel médico |
| Origem das features | payload JSON no body | Feature Store online via `patient_id` + `as_of` |
| Persistência | parquet local + joblib | Lakehouse + OLTP + cache Redis |
| Orquestração | função pura | Temporal workflows duráveis |
| Modelo | treinado uma vez no build | versionado, retreinado, gate de promoção |
| GenAI | OpenRouter + fallback | OpenRouter / LiteLLM com cache semântico, PII redaction, golden set |
| Volume | manual | 4,6M beneficiários × N chamadas/dia |
| Conformidade | documentada | DPIA viva + RoPA + DPO + auditoria contínua |
| Resiliência | "se cair, sobe de novo" | multi-AZ, retries idempotentes, fallback por camada |

---

---

# Detalhamento técnico da arquitetura-alvo

A partir daqui, cada camada da arquitetura-alvo é descrita em detalhe. Diagramas C4, contêineres, decisões de capacidade e justificativas técnicas.

## C4 nível 1 — Contexto

```mermaid
flowchart TB
    BEN[Beneficiário]
    MED[Médico assistente]
    OPER[Operadora<br/>de saúde]
    REG[ANS / LGPD]

    SYS[**Plataforma de Cuidado<br/>Hiper Personalizado**]

    EHR[Prontuários<br/>parceiros FHIR]
    WEAR[Wearables<br/>Apple Health / Google Fit / Whoop]
    PAY[Sistemas de claims]
    TELE[Telemedicina<br/>parceira]

    BEN <-->|app, push, SMS| SYS
    MED <-->|copiloto clínico| SYS
    OPER <-->|painéis<br/>governança| SYS
    REG -->|requisitos| SYS
    SYS <-->|FHIR| EHR
    SYS <-->|OAuth| WEAR
    SYS <-->|claims TUSS| PAY
    SYS <-->|integração| TELE
```

## C4 nível 2 — Contêineres

| Contêiner | Responsabilidade | Stack sugerida |
|---|---|---|
| **API Gateway** | Autenticação, throttling, observabilidade | Kong / AWS API Gateway |
| **App backend** | Jornada do beneficiário, consentimento, eventos | Python (FastAPI) |
| **Ingestion stream** | Sinais contínuos (wearable, eventos do app) | Kafka / Kinesis + schema registry |
| **Ingestion batch** | Claims, EHR, cadastrais | Airflow + Spark |
| **Lakehouse** | Bronze (raw) → Silver (curado) → Gold (analítico) | S3 + Iceberg / Delta |
| **Feature Store** | Features online (low-latency) e offline (treino) | Feast |
| **Model registry** | Versionamento de modelos, lineage | MLflow |
| **ML serving** | Inferência online (risco, propensão) | BentoML / SageMaker / Vertex |
| **GenAI gateway** | Roteamento, caching, redação de PII, guardrails | LiteLLM + camada própria |
| **Orquestrador de jornadas** | Regras + decisões → ações por canal | Temporal / Argo Workflows |
| **OLTP operacional** | Estado da jornada, consentimento, contatos | PostgreSQL |
| **Observabilidade** | Logs, métricas, traces, model monitoring | OpenTelemetry + Grafana + Evidently |
| **Data warehouse de BI** | Painéis executivos | BigQuery / Redshift / Snowflake |

## Camadas em detalhe

### 1. Coleta

| Fonte | Frequência | Volume estimado | Latência alvo |
|---|---|---|---|
| Wearable (HR, HRV, passos, sono) | Streaming (1-5 min) | ~50 eventos/dia/usuário | < 1 min |
| App (eventos de uso, PROMs) | Sob demanda | Variável | < 5 s |
| EHR (consultas, exames, diagnósticos) | Batch noturno | ~2-5 registros/mês/usuário | D+1 |
| Claims (autorizações, custos) | Batch noturno | ~1-3 registros/mês/usuário | D+1 |
| Cadastrais | Diário | Baixo | D+1 |

**Padronização:** sempre que possível, dados clínicos em **HL7 FHIR R4** (Patient, Observation, Condition, MedicationRequest). Wearables convertidos para `Observation` com `code` LOINC. Cláim em **TUSS** mapeado para FHIR `ChargeItem`.

**Consentimento:** evento de consentimento explícito por finalidade — exigência LGPD ([`docs/04`](04-dados-e-conformidade.md)). Sem consentimento ativo para uma finalidade, o dado não entra no pipeline daquela finalidade.

### 2. Ingestão

- **Streaming** para sinais contínuos (wearable, eventos do app). Pipeline `event → Kafka → schema registry → bronze`. Schema validado, eventos malformados vão para DLQ.
- **Batch** para origens transacionais (EHR, claims). Airflow orquestra extrações idempotentes. Cada DAG tem teste de qualidade (`great_expectations`) antes de promover de bronze para silver.

**Idempotência** é regra: toda escrita usa chave natural + versão, dedup é responsabilidade do consumidor.

### 3. Armazenamento

**Padrão Lakehouse com 3 camadas:**

- **Bronze** — raw, append-only, retém payload original e metadados de ingestão. Útil para reprocessamento.
- **Silver** — limpo, deduplicado, com `patient_id` resolvido (MDM). Aqui que o FHIR fica canônico.
- **Gold** — agregado por caso de uso: features de modelo, KPIs de painel, datasets analíticos.

**Particionamento** por data + tenant (operadora) + perfil. **Catálogo** unificado (Glue/Unity Catalog) com lineage e classificação de sensibilidade (PII / PHI / agregado).

**OLTP separado** para o que precisa de consistência forte e baixa latência: estado da jornada, consentimento, fila de ações pendentes.

### 4. Inteligência

Detalhe completo em [`docs/05-estrategia-ia.md`](05-estrategia-ia.md). Resumo:

- **Modelos discriminativos (ML clássico)** para decisão clínica e financeira: risco, agudização, sinistralidade, propensão a engajamento. Servidos online via feature store.
- **GenAI** para texto: copiloto clínico, geração de mensagens personalizadas, RAG sobre protocolos. Sempre com guardrail e observabilidade de prompts/respostas.
- **MLOps** com monitoramento de drift, viés por subgrupo (idade, sexo, região), e gate de promoção exigindo métrica clínica + métrica de fairness.

### 5. Ativação

O **orquestrador de jornadas** é o cérebro. Ele recebe sinais de risco/oportunidade e decide:
- Qual ação (consulta, exame, conteúdo, alerta)
- Qual canal (push, SMS, WhatsApp, ligação ativa, telemedicina)
- Qual horário (modelo de propensão por janela)
- Quando escalar para humano

A regra é declarativa, versionada, e cada execução gera evento auditável (input, decisão, ação tomada).

### 6. Mensuração

Toda ação dispara um **evento de telemetria** com `journey_id`, `decision_id`, `action`, `channel`, `outcome`. Esses eventos voltam para o lakehouse e alimentam:
- Painéis executivos (sinistralidade, custo, eventos prevenidos)
- Painéis clínicos (PQI, agudização, adesão)
- Plataforma de experimentação (A/B test e quase-experimento)

Ver [`docs/06-mensuracao.md`](06-mensuracao.md).

## Decisões arquiteturais-chave

Detalhadas em [`docs/adr/`](adr/). Resumo:

| ADR | Decisão | Por quê |
|---|---|---|
| 001 | Lakehouse > Data warehouse puro | PHI semi-estruturado + ML em escala |
| 002 | FHIR R4 como modelo canônico | Interoperabilidade + vocabulário regulado |
| 003 | ML clássico para decisão clínica | Auditabilidade, custo, regulação |
| 004 | LLM apenas em camadas de texto | Reduzir risco de alucinação clínica |
| 005 | Feature Store dedicada | Reduzir skew treino-inferência |
| 006 | Orquestração via Temporal | Idempotência + visibilidade de jornadas longas |

## Escalabilidade para 4,6M de beneficiários

- **Inferência online de risco:** ~1 req/s sustentada com picos manhã/noite. Stack horizontal (k8s + HPA), latência p99 < 200 ms.
- **Streaming de wearables:** ~2.700 eventos/s sustentados (50 ev/dia × 4,6M / 86400). Kafka particionado por `patient_id`, retenção 7 dias em quente, depois lake.
- **Batch noturno:** janela de 4h para processar EHR + claims do dia. Spark com auto-scaling.
- **GenAI:** chamadas roteadas por modelo (haiku para tarefas simples, sonnet/opus para clínico), com cache semântico para reduzir custo. Orçamento mensal monitorado por unidade de negócio.

## Resiliência

- **Falha de fonte externa** (wearable API down) → degradação graciosa, jornada continua com dados anteriores e alerta operacional.
- **Falha do ML serving** → orquestrador usa última decisão válida + escala para humano em casos vermelhos.
- **Falha do GenAI** → fallback para template determinístico por persona/risco. Beneficiário recebe mensagem mais genérica, mas recebe.
- **Multi-AZ** mínimo, multi-região como roadmap (LGPD permite, mas exige diligência sobre sub-processadores).

## O que está no protótipo vs o que está só no diagrama

| Componente | No protótipo? | Justificativa |
|---|---|---|
| API + ML + GenAI + orquestração simples | ✅ | É a fatia vertical que prova a tese |
| Dados sintéticos | ✅ | Sem PHI real, ágil |
| FastAPI + XGBoost + OpenRouter (OpenAI-compatible) | ✅ | Stack simples, demonstrável; provider-neutral via env var |
| Kafka, Airflow, Spark, Feature Store | ❌ | Documentados em [`infra/architecture-target.md`](../infra/architecture-target.md) |
| FHIR completo | ❌ | Schema simplificado no protótipo, FHIR é alvo de produção |
| Multi-tenant, multi-região | ❌ | Roadmap |

A fatia vertical do protótipo foi escolhida para **exercitar todos os 5 aspectos do case** (coleta, tratamento, armazenamento, mensuração, personalização) com o menor número de componentes possível, sem disfarçar o que de fato seria infraestrutura de produção.
