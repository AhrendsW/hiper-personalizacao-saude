# ADR 001. Lakehouse como backbone de dados

**Status:** aceito
**Data:** 2026-04

## Contexto

A solução precisa armazenar três tipos de dados:
1. **Dados estruturados de claims e cadastrais** (TUSS, ANS). Bem comportados, alto valor analítico
2. **Dados clínicos semiestruturados** (FHIR vindo de EHR). Schema evolui, varia por parceiro
3. **Sinais contínuos de wearable** (séries temporais). Alto volume, baixa estrutura

Volume estimado: 4,6M beneficiários × 50 eventos/dia = ~2.700 eventos/s sustentados, com batch noturno de claims/EHR.

Há também necessidade de:
- Treinar modelos de ML em datasets grandes
- Reprocessar dados após correção (auditoria, qualidade)
- Manter retenção longa para dados clínicos (até 20 anos por norma CFM)
- Atender BI/painéis com latência aceitável

## Decisão

Adotar **arquitetura Lakehouse** com object storage (S3) + camada transacional (Apache Iceberg ou Delta Lake), e **OLTP separado** (PostgreSQL) para estado operacional.

Camadas: **Bronze** (raw append-only) → **Silver** (curado, deduplicado, FHIR canônico) → **Gold** (analítico por caso de uso).

Warehouse de BI gerenciado (BigQuery/Snowflake/Redshift) consome do Gold quando latência ou concorrência exige.

## Alternativas consideradas

| Opção | Por que descartada |
|---|---|
| Data Warehouse puro | Schema rígido sofre com dados semiestruturados; ML em escala fica caro fora dele |
| Data Lake puro (sem ACID) | Sem transações, retrabalho de qualidade vira pesadelo; auditoria sofre |
| OLTP escalado | Não absorve volume nem treina ML adequadamente |

## Consequências

**Positivas:**
- Único lugar para dado clínico, financeiro e analítico
- ACID em cima de object storage (Iceberg/Delta) reduz custo vs warehouse
- Reprocessamento simples a partir de bronze
- ML treina diretamente no lake, sem mover dados

**Negativas:**
- Operação de lakehouse exige expertise (manutenção de tabelas, otimização de partições)
- Latência mais alta que warehouse para certos painéis. Mitigado com gold pré-agregado
- Curva de aprendizado para times acostumados com warehouse tradicional

## Consequências de conformidade

- Particionamento permite retenção diferenciada por camada (bronze 90d, silver 5-20a, gold conforme finalidade)
- Catálogo unificado (Glue/Unity) com classificação de sensibilidade vira política de acesso
- Pseudonimização aplicada na promoção bronze → silver
