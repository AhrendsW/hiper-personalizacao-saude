# ADR 005 — Feature Store dedicada (Feast)

**Status:** aceito
**Data:** 2026-04

## Contexto

Modelos de ML clássico em saúde sofrem com **skew entre treino e inferência** quando features são calculadas em pipelines diferentes. Em saúde isso vira erro clínico — modelo prevê risco com features que na prática são calculadas diferente.

Outro desafio: features precisam estar disponíveis em **online** (latência baixa para serving) e em **offline** (dataset reproduzível para treino).

## Decisão

Adotar **Feature Store dedicada** com **Feast** (open-source, federado, integra bem com Iceberg/Delta + Redis/DynamoDB).

Princípios:
- **Definição única** de feature (mesma transformação em treino e online)
- **Materialização agendada** para online store
- **Time travel** — datasets de treino com `as_of` correto, sem leakage temporal
- **Lineage** — cada feature tem dataset de origem, transformação documentada e owner

## Alternativas consideradas

| Opção | Por que descartada |
|---|---|
| Sem feature store, calcula sob demanda | Skew treino-inferência inevitável; reuso entre modelos sofre |
| Feature store gerenciada (Vertex/SageMaker) | Lock-in; custo cresce com escala; menos flexível |
| Construir do zero | Reinventa roda; equipe pequena não justifica |

## Consequências

**Positivas:**
- Skew minimizado — mesma feature, mesma fórmula
- Reuso de features entre modelos (risco e propensão compartilham várias)
- Datasets de treino reproduzíveis com `as_of`
- Onboarding de novo cientista é mais rápido (catalog navegável)

**Negativas:**
- Camada operacional adicional para manter
- Latência de online store (Redis/Dynamo) precisa ser orçada
- Curva de aprendizado para o time

## Notas

- Online store: Redis para latência, com cache local na inferência para os hot paths
- Offline store: Iceberg sobre S3 (mesmo backbone do lakehouse)
- Feature views versionadas em Git
- Materialização monitorada — atraso de feature pode degradar modelo silenciosamente
