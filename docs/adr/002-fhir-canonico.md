# ADR 002. FHIR R4 como modelo canônico de dados clínicos

**Status:** aceito
**Data:** 2026-04

## Contexto

Dados clínicos chegam em formatos diversos: HL7 v2, CDA, JSON proprietário de EHR, payloads de wearable (Apple HealthKit, Google Fit), claims em TUSS, exames em LOINC. Sem padronização, cada integração vira código novo, e modelos de IA sofrem com inconsistência.

A ANS publicou a **Resolução Normativa nº 506/2022** estabelecendo padrões de interoperabilidade obrigatórios para o setor.

## Decisão

Adotar **HL7 FHIR R4** como modelo canônico para todos os dados clínicos no silver. Mapeamentos:

| Dado | FHIR Resource |
|---|---|
| Beneficiário | `Patient` |
| Consulta | `Encounter` |
| Diagnóstico | `Condition` |
| Medicação prescrita | `MedicationRequest` |
| Medicação dispensada | `MedicationDispense` |
| Exame / sinal vital / leitura wearable | `Observation` (com `code` LOINC) |
| Cláim / item de despesa | `ChargeItem` |
| Plano de cuidado | `CarePlan` |
| Consentimento | `Consent` |

## Alternativas consideradas

| Opção | Por que descartada |
|---|---|
| Schema próprio | Precisaríamos criar e manter ontologia clínica do zero. Não justifica |
| HL7 v2 | Legado, menos estruturado, sucessor é justamente FHIR |
| OpenEHR | Mais flexível mas adoção menor no Brasil; FHIR tem suporte regulatório explícito |

## Consequências

**Positivas:**
- Suporte regulatório (RN 506/2022)
- Vocabulário internacional comum facilita integração com qualquer EHR
- Comunidade ativa, ferramentas open-source maduras (HAPI FHIR, fhir.resources)
- Portabilidade nativa para cumprir art. 18 LGPD

**Negativas:**
- FHIR é verboso. Exige cuidado com performance
- Mapeamento de fontes legadas tem custo inicial
- Versão (R4 vs R5) precisa ser fixada e atualizada com cuidado

## Notas de implementação

- Bronze mantém payload original. FHIR é canônico no silver
- Validador FHIR rodando na promoção bronze → silver, com DLQ para inválidos
- Identificadores (`Patient.identifier`) seguem catálogo nacional (CPF, CNS) para MDM
