# ADR 006 — Temporal para orquestração de jornadas

**Status:** aceito
**Data:** 2026-04

## Contexto

Jornadas de cuidado são **fluxos longos, com pausas, com humanos no loop, com retries, com transições**. Crônico recebe lembrete diário por 90 dias; idoso tem visita quinzenal de enfermagem; jovem tem ciclo anual de check-up.

Implementar isso em código de aplicação tradicional (cron + filas + estado em banco) gera código frágil: estado perdido em deploy, retries inconsistentes, visibilidade ruim.

## Decisão

Usar **Temporal** (workflow engine durável, código-como-workflow) para orquestrar jornadas de cuidado.

## Alternativas consideradas

| Opção | Por que descartada |
|---|---|
| Cron + fila (RabbitMQ/SQS) | Estado da jornada espalhado, retries inconsistentes, visibilidade pobre |
| Camunda / Zeebe (BPMN) | Curva mais alta para times de engenharia; menos código-como-workflow |
| Argo Workflows | Bom para pipelines de batch, menos adequado a jornadas longas com humanos |
| Step Functions (AWS) | Lock-in; menos expressivo para fluxos longos |

## Por que Temporal especificamente

- **Durabilidade** — workflow continua exatamente onde parou após deploy/falha
- **Código-como-workflow** — mesmo Python/TypeScript que o resto do backend, sem DSL externa
- **Retries e timeouts declarativos** por activity
- **Versionamento de workflow** — deploys sem quebrar jornadas em curso
- **Visibilidade** nativa — UI mostra estado de cada jornada
- **Sinais e queries** — interage com jornada ativa (responder consentimento, escalar para humano)

## Consequências

**Positivas:**
- Jornada longa robusta a falha e deploy
- Auditoria — cada execução tem trace completo
- Reduz bug de "estado perdeu sincronia"
- Padrão claro para time

**Negativas:**
- Componente adicional para operar (cluster Temporal)
- Times precisam aprender modelo (mas é Python/TS, não DSL nova)
- Custo de licenciamento se for Cloud (open-source self-hosted é alternativa)

## Padrão de uso

- **Workflow** = jornada de cuidado (ex.: `ChronicMonitoringWorkflow(patient_id)`)
- **Activity** = chamada com side-effect (ML serving, GenAI, push, agendamento)
- **Signal** = evento externo (consentimento revogado, alta hospitalar)
- **Query** = ler estado atual (jornada ativa? qual passo?)
- Toda activity é idempotente
