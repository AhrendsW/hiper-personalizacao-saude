# 07. Modelo de Negócio, Go-to-Market e Times

> Responde diretamente ao eixo **Management & Business** do PDF e ao eixo **Digital & Innovation** na parte de novos modelos de negócio.

## Modelo de negócio

### Para a operadora
A plataforma **não é produto vendido**. É **infraestrutura de cuidado** que reduz sinistralidade e melhora desfecho. A receita aparece no demonstrativo da operadora como **redução de despesa médica** e como **diferencial competitivo na captação e retenção** de beneficiários.

| Mecanismo de retorno | Como mede |
|---|---|
| Redução de claims evitáveis | Custo evitado vs custo da plataforma |
| Retenção de beneficiários | Churn segmentado por engajamento |
| Captação por diferencial | NPS, atribuição de novos contratos |
| Eficiência operacional | Médico atende mais com menos sobrecarga (copiloto) |

### Modelos de negócio adjacentes que o PDF pede ("Novos modelos de negócio")

Inspirados em movimentos do mercado de saúde suplementar (planos pet, farmácia digital, clubes de vantagens, programas de longevidade), a plataforma habilita:

1. **Cuidado por assinatura para não-beneficiários:** Versão da trilha preventiva como D2C, sem cobertura hospitalar mas com telemed e wearable. Funil para conversão em plano completo.
2. **Programa B2B2C com empresas:** Empregadores oferecem trilha preventiva como benefício, Unimed como provedora.
3. **Atenção domiciliar como serviço:** Trilha de idoso comercializada como serviço discreto, com ou sem plano.
4. **Marketplace de bem-estar:** Integração com a base já existente de parceiros (academias, alimentação, telemedicina especializada) com personalização guiada por IA.
5. **Longevidade e prevenção de longo prazo:** Pacote para coorte 50+ que ainda não é crônica, focado em healthspan.

Cada um desses é uma **alavanca de receita nova** sem competir com o produto principal. Todos compartilham a mesma plataforma de IA e dados.

## Estratégia de Go-to-Market

### Fase 1. Piloto controlado (3-6 meses)
- **Coorte:** 5.000 beneficiários (mix dos 3 perfis) em 1-2 regiões
- **Objetivo:** validar tese clínica e operacional, não escalar
- **Sucesso medido por:** sinais de engajamento + sinais clínicos preliminares (não custo ainda)
- **Decisão go/no-go** após pré-registro de hipótese e medição

### Fase 2. Expansão regional (6-12 meses)
- **Coorte:** 100.000-300.000 beneficiários, regiões adicionais com diferentes perfis socioeconômicos
- **Objetivo:** validar generalização, calibrar custo, refinar trilhas
- **Quase-experimento** entre regiões com e sem plataforma para CAEP defensável

### Fase 3. Escala nacional (12-24 meses)
- **Coorte:** todos os 4,6M
- **Roll-out por trilha** (crônico primeiro, depois jovem, depois idoso) ou por região conforme aprendizado das fases anteriores
- **Holdout permanente** mantido
- **Time clínico distribuído** com central de comando

### Fase 4. Modelos adjacentes (24+ meses)
- Lançamento dos novos modelos de negócio
- Plataforma já madura suporta multi-tenant e multi-produto

## Estrutura de times

### Princípio: squad por jornada, não por tecnologia

Squads multidisciplinares organizados por **trilha de cuidado**, não por camada técnica. Cada squad entrega valor ponta a ponta dentro do seu domínio.

```
                Tribo de Cuidado Hiper Personalizado
                              │
   ┌──────────────┬───────────┼───────────┬──────────────┐
   │              │           │           │              │
 Squad         Squad        Squad        Squad        Squad
 Jovens       Crônicos      Idosos     Plataforma     IA & MLOps
                                       (data, infra)
```

### Composição típica de um squad de jornada (Jovens/Crônicos/Idosos)
- 1 PM (com background em saúde)
- 1 Tech lead
- 2-3 Engenheiros (full stack ou backend)
- 1 Cientista de dados / ML engineer
- 1 Designer (UX em saúde)
- 1 Médico/enfermeiro consultor part-time (responsável clínico)
- Acesso a Pesquisa, BI, Dados

### Squad Plataforma
- Engenharia de dados, infra, observabilidade, segurança
- Atende as squads de jornada como "clientes internos"
- Mantém lakehouse, feature store, ingestão, cloud, IAM

### Squad IA & MLOps
- Cientistas de dados sênior, ML engineers, prompt engineers
- Mantém modelos compartilhados (risco, propensão), GenAI gateway, guardrails
- Atende squads de jornada com modelos especializados sob demanda

### Funções centralizadas
- **Comitê clínico:** Direção médica, especialistas, valida protocolos e modelos
- **DPO + jurídico:** Privacidade, conformidade, contratos
- **Comitê ético de experimentação:** Aprova RCTs digitais que tocam desfecho clínico
- **Liderança de produto:** Alinhamento de roadmap, OKRs trimestrais
- **CISO:** Segurança da informação, gestão de incidente

## Como rodar com agilidade sem virar caos

### Cadência
- **Quarterly Planning** com OKRs por tribo, alinhados ao Plano Plurianual da Unimed
- **Sprints de 2 semanas** com demo aberta
- **Releases canários** sempre. Nada vai a 100% do tempo
- **Postmortem de incidente** sem culpa, com aprendizado documentado

### Métricas de saúde do time
- Lead time de mudança
- Frequência de deploy
- MTTR
- Taxa de mudança bem-sucedida
- (DORA metrics. Padrão para times de plataforma maduros)

### Princípios operacionais
1. **Decisão local, padrão global:** Squad decide implementação dentro do trilho da plataforma.
2. **Toda mudança em modelo passa pelo squad de IA & MLOps:** Para auditabilidade e fairness.
3. **Toda mudança que afeta cuidado clínico passa pelo Comitê Clínico** antes de promover.
4. **Documentação como código:** ADR, model card, runbook versionados com o produto.

## Desafios de TI mais críticos (resposta direta à questão do PDF)

| Desafio | Mitigação |
|---|---|
| Integração com EHR/claims legados | Camada de integração FHIR + adapters por sistema legado, mapeamento documentado, testes de contrato |
| Qualidade de dados multi-fonte | Pipeline com `great_expectations`, MDM no silver, observabilidade de qualidade no painel |
| Latência em decisão clínica | Feature store online + cache + ML serving próximo ao API gateway |
| Custo de cloud e GenAI em escala | FinOps de IA: cache semântico, roteamento por modelo, monitoramento de custo por unidade de negócio, orçamento mensal por squad |
| Recrutamento de perfis raros (ML eng com saúde) | Plano de carreira + parceria com academia (FIAP, USP, UFMG) + comunidade interna |
| Conformidade cruzando jurisdições estaduais | Camada de regras de negócio configurável por região, governança centralizada |
| Onboarding de novos parceiros | Sandbox padronizado + documentação API + checklist de conformidade |

## Estratégia de adoção (como faz a IA "pegar")

Resposta direta à questão "Quais estratégias podem ser implementadas para incentivar o uso de IA":

1. **Dor real do médico primeiro:** Copiloto resume prontuário em 30s. Médico vira advogado interno.
2. **Painel clínico que mostra resultado:** "estes pacientes evitaram internação após intervenção" é convincente.
3. **Time clínico no design:** Médicos validam prompts, dataset, model card. Não é IA jogada por cima do cuidado.
4. **Transparência radical:** Toda decisão tem explicação. Caixa-preta gera resistência.
5. **Aprendizado contínuo:** Feedback do médico vira treino do modelo. Quem ajuda a melhorar o sistema sente ownership.
6. **Limite explícito:** "isto não substitui orientação médica" é o que dá confiança, não tirar o aviso.

## Como gerenciar o produto digital (resposta direta à questão do PDF)

| Aspecto | Como gerenciar |
|---|---|
| **Crescimento** | OKRs por tribo, métricas estrela por trilha, escalonamento progressivo |
| **Adoção pelo mercado** | Diferencial em NPS, atribuição em captação/retenção, programas B2B2C |
| **Roadmap** | Quarterly com input clínico, financeiro e de produto |
| **Priorização** | Impacto clínico × impacto financeiro × esforço. Em planilha versionada |
| **Comunicação** | Demos abertas a stakeholders, newsletters internas, painéis em tempo real |
| **Cultura** | Erro sem culpa, postmortem aprendido, celebração de evento prevenido |

## Sumário em uma frase

> **Modelo de negócio é cuidado preventivo virando alavanca financeira; GTM é piloto-expansão-escala com mensuração rigorosa; time é squad por jornada com plataforma central; a IA pega quando reduz dor real e mostra resultado.**
