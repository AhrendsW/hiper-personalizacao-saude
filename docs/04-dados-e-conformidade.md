# 04 — Dados, Conformidade e Segurança

> **Em saúde, conformidade não é um capítulo no final do documento. É restrição de arquitetura.**
> Toda decisão técnica abaixo passou por três filtros: **LGPD** (dado pessoal e sensível), **regulação da ANS** (operação de saúde suplementar) e **resoluções do CFM** (ato médico, telemedicina).

## Tipos de dados e classificação

| Categoria | Exemplos | Sensibilidade | Onde pode estar |
|---|---|---|---|
| **PII** | Nome, CPF, contato | Alta | OLTP, com encryption at rest e column-level access control |
| **PHI** (dado de saúde) | Diagnóstico, medicação, exame, sinal vital | **Sensível** (LGPD art. 5º, II) | Lakehouse silver+, com pseudonimização para analytics |
| **Comportamental** | Sono, atividade, humor autorreportado | Sensível por inferência | Tratado como PHI |
| **Socioeconômico** | Faixa de renda, ocupação | Pessoal | Apenas agregado para BI, não no perfil 1:1 |
| **Agregado** | Coortes, KPIs, painéis | Não pessoal | Warehouse de BI |

## Bases legais (LGPD)

A LGPD exige base legal explícita para tratar dado pessoal, e mais ainda para dado sensível (saúde). A plataforma usa as seguintes bases, **uma por finalidade**:

| Finalidade | Base legal LGPD | Justificativa |
|---|---|---|
| Operação do plano de saúde (autorização, atendimento) | Execução de contrato (art. 7º, V) | Contrato de plano de saúde |
| Tutela da saúde por profissional de saúde | Art. 11, II, "f" | Médico assistente atuando |
| Personalização preventiva e jornada digital | **Consentimento específico e granular** (art. 11, I) | Por ser preventivo, não execução de contrato |
| Mensuração e melhoria do serviço | Legítimo interesse + LIA | Com opt-out |
| Cuidador no loop (idoso) | Consentimento adicional do beneficiário | Vínculo formal autorizado |
| Pesquisa e modelos de IA | Anonimização irreversível + comitê de ética | Sem identificação possível |

**Consentimento granular:** o beneficiário pode aceitar receber lembretes mas recusar análise comportamental. O sistema **respeita por finalidade** — o que ele não consentir, não entra naquele pipeline.

## Princípios da LGPD aplicados

| Princípio | Como vira código |
|---|---|
| Finalidade | Cada pipeline tem `purpose_id`. Dado só pode ser lido por jobs com purpose autorizado. |
| Adequação e necessidade | Inventário de campos por finalidade. Campos não justificados são removidos do silver. |
| Livre acesso | Endpoint de "minhas informações" no app, exporta o que existe sobre o beneficiário. |
| Qualidade dos dados | Validação na ingestão, MDM no silver, correção retornável ao beneficiário. |
| Transparência | Política de privacidade versionada, notificações sobre mudanças. |
| Segurança | Ver seção dedicada abaixo. |
| Prevenção | Threat modeling antes de cada feature que toca PHI. |
| Não discriminação | Auditoria de viés nos modelos de risco (idade, sexo, região). |
| Responsabilização | Logs auditáveis, DPO ativo, registros de tratamento (RoPA). |

## Direitos do titular

Todo direito previsto no art. 18 vira **endpoint** ou **fluxo operacional**:

- Confirmação de tratamento → endpoint público
- Acesso aos dados → exportação no app
- Correção → fluxo no app + revisão clínica para campos clínicos
- Anonimização, bloqueio ou eliminação → SLA de 15 dias úteis
- Portabilidade → exportação em FHIR Bundle
- Revogação de consentimento → afeta pipelines marcados com aquele `purpose_id` em até 24h
- Eliminação de dados desnecessários → política de retenção automática

## DPIA (Avaliação de Impacto)

Por envolver **tratamento sistemático de dado sensível em larga escala**, a operação **exige DPIA** ([ANPD recomenda](https://www.gov.br/anpd/pt-br); art. 38 LGPD, art. 35 GDPR como referência). DPIA contempla:

- Mapeamento de fluxos de dados por finalidade
- Riscos identificados e medidas mitigadoras
- Análise de proporcionalidade (necessidade vs intrusão)
- Aprovação do DPO antes de cada release que altere o tratamento
- Revisão anual ou em mudança material

## Conformidade ANS

A Unimed Nacional é operadora regulada pela ANS. Pontos de atenção desta solução:

- **Resolução Normativa nº 506/2022** — interoperabilidade obrigatória do setor (TISS/TUSS no claim, FHIR no clínico). A arquitetura adota FHIR como canônico já pensando nisso.
- **Padrões de troca de informação** — dados que saem para parceiros (laboratório, hospital) seguem padrões da ANS.
- **Notificação de incidentes** — incidente de segurança que afete beneficiário tem fluxo dedicado para ANPD + ANS quando aplicável.
- **Reajustes e produtos** — esta plataforma **não toma decisão de cobertura, autorização ou negativa**. É camada de **cuidado preventivo**. Decisão clínica/contratual continua nos sistemas de retaguarda regulados.

## Conformidade CFM (telemedicina e ato médico)

- **Resolução CFM nº 2.314/2022** regula telemedicina no Brasil. A plataforma acopla telemedicina via parceiro homologado, não exerce ato médico.
- **IA não substitui médico.** O modelo de risco **recomenda**, o profissional **decide e prescreve**. Toda decisão clínica passa por humano, com IA como copiloto auditável.
- **Prontuário** — qualquer registro clínico gerado segue norma do CFM (assinatura digital, integridade, retenção mínima de 20 anos).

## Segurança técnica

### Criptografia
- **Em repouso:** AES-256 em todos os storages (object storage, OLTP, backups)
- **Em trânsito:** TLS 1.3, mTLS entre serviços internos
- **Chaves:** KMS gerenciado, rotação automática, segregação por ambiente e por categoria de sensibilidade

### Controle de acesso
- **IAM** com least-privilege e separação por papel (engenharia de dados, cientista, médico, atendimento, BI)
- **ABAC** em cima de RBAC para regras como "médico só vê paciente sob seus cuidados"
- **Aprovação de acesso a PHI bruto** — workflow com justificativa, expira em horas, log auditável
- **MFA** obrigatório para acesso a sistemas com PHI

### Segregação de ambientes
- Produção, staging e dev **fisicamente separados**
- **Sem PHI em ambientes não-produção** — datasets sintéticos ou anonimização irreversível para dev/QA

### Anonimização e pseudonimização
- **Pseudonimização:** silver tem `patient_id` substituído por hash com sal por finalidade. Re-identificação só com chave protegida no KMS.
- **Anonimização irreversível:** datasets para pesquisa e modelos passam por k-anonimato + supressão de quase-identificadores.
- **Avaliação de risco de re-identificação** antes de exportar qualquer dataset.

### Detecção e resposta
- **SIEM** com regras específicas de saúde (acesso anômalo a paciente VIP, exfiltração, varredura)
- **Plano de resposta a incidentes** com SLA explícito de notificação ANPD (até 2 dias úteis)
- **Pen test** anual, varredura de dependências contínua

## Segurança específica de IA

| Risco | Mitigação |
|---|---|
| Vazamento de PHI em prompt para LLM externo | **PII redaction** antes do envio. Apenas tokens não-identificáveis no prompt. |
| Alucinação clínica | LLM não decide. Saída do LLM passa por validador (regex, schema, sanidade) antes de chegar ao paciente. |
| Prompt injection | Templates parametrizados, separação de contexto, allowlist de instruções. |
| Viés discriminatório | Auditoria por subgrupo (idade, sexo, região, raça quando declarada com consentimento). Modelo barrado se diferença de FPR/FNR > limiar. |
| Drift do modelo | Monitoramento contínuo, retraining automático com gate humano para promoção. |
| Re-identificação por inferência | Output do modelo nunca contém quase-identificadores. |

## Residência e soberania de dado

- **Dado clínico de beneficiário brasileiro processado em região brasileira** sempre que possível, ou em região com nível de proteção compatível (LGPD art. 33).
- **Sub-processadores** (cloud, LLM provider, parceiros) listados, com cláusula contratual e DPA.
- **Provedor de LLM** com política explícita de não-treinamento sobre prompts e residência de dados garantida.

## Retenção e descarte

| Categoria | Retenção | Descarte |
|---|---|---|
| Bronze (raw) | 90 dias | Automático após processamento bem-sucedido |
| Silver (curado) | 5-20 anos conforme tipo (prontuário 20 anos por norma CFM) | Política por dataset |
| Gold (analítico) | Conforme finalidade | Reagregado, não regredível |
| Logs operacionais | 6 meses | Automático |
| Logs de auditoria de acesso a PHI | 5 anos | Imutável (WORM) |

## Auditoria e governança

- **Comitê de ética e privacidade** com participação clínica, jurídica e de dados, revisa novas finalidades
- **DPO** designado, contato público, prazo de resposta < 15 dias
- **RoPA** (Registro de Operações de Tratamento) sempre atualizado
- **Trilhas de auditoria** imutáveis: quem acessou qual dado, quando, com que justificativa
- **Auditoria externa** anual de práticas de privacidade e segurança

## O que não fazer (anti-padrões em saúde digital)

1. **Treinar modelo com PHI bruto enviado para LLM provider externo sem DPA** — vazamento massivo, risco institucional, multa LGPD.
2. **"Anonimizar" só removendo nome** — quase-identificadores (CEP + idade + sexo + diagnóstico raro) re-identificam fácil.
3. **Modelo opaco em decisão de cuidado** — se o médico não consegue entender por que o sistema sugeriu X, ele não vai usar e a auditoria não passa.
4. **Confundir cuidado preventivo com decisão de cobertura** — IA aqui sugere ação de saúde, não nega procedimento. Cruzar essa linha gera judicialização.
5. **Coletar tudo "porque pode ser útil"** — viola finalidade e necessidade da LGPD.

## Sumário em uma frase

> **Privacidade, segurança e ética clínica são os três trilhos sobre os quais a personalização anda. Sair de qualquer um deles é decretar a morte do produto antes de escalar.**
