# ADR 003. ML clássico para decisão clínica e financeira

**Status:** aceito
**Data:** 2026-04

## Contexto

Há tentação de usar LLM para tudo. Incluindo decisões de classificação e regressão sobre dado tabular (risco, propensão, sinistralidade). Em saúde, essa decisão tem consequências regulatórias, financeiras e de segurança.

## Decisão

Toda **decisão clínica ou financeira de classificação/regressão** sobre dado tabular usa **modelos de ML clássico** (XGBoost, LightGBM, GBM, regressão regularizada). LLM **não é usado para decisão**, apenas para texto.

## Critério de "decisão" para fins desta ADR

É decisão tudo que:
- Atribui classe de risco a paciente
- Estima probabilidade de evento clínico
- Estima custo esperado / sinistralidade
- Decide canal/horário (propensão)
- Gera input para acionar protocolo clínico

## Justificativa

| Aspecto | ML clássico | LLM |
|---|---|---|
| Auditabilidade (SHAP, calibração) | Alta | Baixa nativa |
| Custo de inferência em escala | Centavos/M | Ordens de grandeza maior |
| Determinismo | Sim | Não, sem amarração |
| Risco de alucinação | Zero | Real |
| Aceitação regulatória (ANS, CFM) | Forte | Aceitável só com guardrail |
| Performance em dado tabular | Estado da arte | Pior em geral |

## Consequências

**Positivas:**
- Custo previsível e baixo
- Auditoria clínica possível (model card, SHAP)
- Fairness mensurável e gateável
- Estabilidade. Mesmo input, mesma saída

**Negativas:**
- Exige pipeline de feature engineering tradicional
- Times precisam de skill em ML clássico (não só prompting)

## Implementação

- Framework: scikit-learn + XGBoost/LightGBM
- Validação: time-based split + CV temporal
- Calibração: Platt ou Isotônica
- Explicabilidade: SHAP por predição e global
- Fairness: Aequitas/Fairlearn como gate
- Servir: BentoML / FastAPI / serviço gerenciado
- Feature store: Feast para evitar skew treino-inferência

## Exceção

LLM **pode** ser usado para extração estruturada (texto livre → campos FHIR), desde que:
1. Output passe por validador de schema
2. Saída seja revisável por humano antes de afetar cuidado
3. Não seja chamado em loop crítico de decisão clínica
