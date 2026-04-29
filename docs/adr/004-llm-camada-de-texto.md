# ADR 004. LLM apenas em camadas de texto e raciocínio

**Status:** aceito
**Data:** 2026-04

## Contexto

LLM é poderoso em linguagem, mas tem riscos específicos em saúde: alucinação, custo, opacidade, exposição de PHI. ADR 003 definiu que decisão clínica/financeira fica com ML clássico. Esta ADR define **onde** LLM é usado.

## Decisão

LLM (Claude prioritariamente) é aplicado em:

1. **Comunicação personalizada com beneficiário:** Recebe persona + decisão do ML clássico + features explicativas e compõe mensagem
2. **Copiloto clínico:** Resumo de prontuário, sugestão de hipóteses, com citação verificável
3. **RAG sobre protocolos:** Médico pergunta, modelo responde com citação de fonte
4. **Extração de dados não estruturados:** Anamnese livre / áudio → FHIR estruturado, com validação de schema
5. **Chatbot de engajamento:** Dúvidas simples, allowlist de tópicos, escalonamento para humano em casos complexos

## Não é usado para

- Classificação ou regressão sobre dado tabular (ADR 003)
- Decisão de cobertura ou autorização (regulatório)
- Prescrição médica
- Diagnóstico autônomo

## Guardrails obrigatórios

| Camada | Mecanismo |
|---|---|
| Pré-prompt | PII redaction, allowlist de tópicos |
| Prompt | Templates parametrizados, separação contexto/instrução |
| Modelo | Provider com DPA + não-treino sobre prompts + residência de dados |
| Pós-resposta | Validação de schema, regex PII residual, classificador de toxicidade |
| Auditoria | Log imutável (prompt + resposta + contexto) por usuário/finalidade |
| Humano no loop | Saída clínica passa por médico antes de afetar cuidado |

## Acesso provider-neutral

LLM é consumido via **OpenRouter** (API OpenAI-compatible) no protótipo,
e via **LiteLLM** ou gateway próprio em produção. A troca de provider
(Anthropic, OpenAI, Google, modelos open-weights via vLLM) é configuração
por env var, sem mudança de código.

## Roteamento por classe de modelo

- **Haiku-class** (Claude Haiku, GPT-4o-mini, Gemini Flash). Extração
  simples, classificação leve, comunicação personalizada padrão
- **Sonnet-class** (Claude Sonnet, GPT-4o, Gemini Pro). Copiloto leve,
  geração com mais contexto
- **Opus-class** (Claude Opus, GPT-4 Turbo). Copiloto clínico complexo,
  raciocínio sobre histórico longo

Critério: tarefa mais barata possível que entrega qualidade aceitável
(avaliada com golden set).

## Consequências

**Positivas:**
- Mensagem personalizada com nuance que template não atinge
- Copiloto economiza tempo do profissional
- Custo controlado por roteamento + cache semântico

**Negativas:**
- Operação adicional (gateway, cache, observabilidade de prompts)
- Risco residual de alucinação. Mitigado por validador e humano no loop
- Dependência de provider externo. Mitigada por capacidade de trocar e fallback determinístico

## Fallback determinístico

Quando LLM está indisponível ou retorna conteúdo que não passa em validação:
- Mensagem por **template parametrizado** baseado em persona + risco + features
- Beneficiário recebe mensagem mais genérica, mas recebe. Não trava jornada
