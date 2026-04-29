# Hiper Personalização do Cuidado em Saúde Suplementar

> Solução ponta a ponta de IA para uma jornada de cuidado **hiper personalizada** em uma operadora de saúde, desenhada para **maximizar a saúde do beneficiário** e **reduzir a sinistralidade** da operadora.

Estudo técnico de arquitetura e protótipo combinando ML clássico, GenAI, conformidade LGPD/ANS/CFM e mensuração clínica e financeira.

---

## TL;DR

Cada beneficiário é único. Tratá-los de forma idêntica é caro para a operadora e ruim para o paciente. Esta proposta combina **modelos de ML clássico** (decisão clínica auditável) com **GenAI** (comunicação personalizada e raciocínio sobre texto), em uma arquitetura de dados conforme com **LGPD** e **regulação ANS/CFM**, dimensionada para uma operadora nacional na faixa de **4,6 milhões de beneficiários**.

```
Wearables + Claims + Prontuário  →  ML decide risco  →  GenAI compõe ação  →  Engajamento
        (coleta)                     (tratamento+IA)     (personalização)      (mensuração)
```

## Como rodar

```bash
cd prototype
docker compose up --build
# em outro terminal
curl -X POST localhost:8000/score \
  -H 'Content-Type: application/json' \
  -d @samples/maria.json
```

Saída esperada: score de risco, top features explicativas (SHAP) e mensagem personalizada gerada para a persona.

Detalhes completos de setup (Docker, uv local, CLI), configuração do `.env`, obtenção da `OPENROUTER_API_KEY` e troca de modelos: [`prototype/README.md`](prototype/README.md).

## Como navegar

| Tópico | Documento |
|---|---|
| Problema, proposta de valor, KPIs | [`docs/01-problema.md`](docs/01-problema.md) |
| Arquitetura ponta a ponta (C4) | [`docs/02-arquitetura.md`](docs/02-arquitetura.md) |
| Trilhas de cuidado por perfil (Júlia, Maria, João) | [`docs/03-trilhas-de-cuidado.md`](docs/03-trilhas-de-cuidado.md) |
| Dados, LGPD, ANS, CFM, segurança | [`docs/04-dados-e-conformidade.md`](docs/04-dados-e-conformidade.md) |
| Estratégia de IA. ML clássico vs GenAI | [`docs/05-estrategia-ia.md`](docs/05-estrategia-ia.md) |
| Mensuração de efetividade e engajamento | [`docs/06-mensuracao.md`](docs/06-mensuracao.md) |
| Modelo de negócio, escalabilidade, times | [`docs/07-modelo-de-negocio.md`](docs/07-modelo-de-negocio.md) |
| Como o `/score` é consumido em produção | [`docs/08-integracao-em-producao.md`](docs/08-integracao-em-producao.md) |
| Decisões arquiteturais (ADRs) | [`docs/adr/`](docs/adr/) |
| Protótipo executável | [`prototype/`](prototype/) |
| Arquitetura-alvo de produção | [`infra/architecture-target.md`](infra/architecture-target.md) |

## Diferenciais da proposta

- **ML onde decide, GenAI onde comunica:** Escolha técnica justificada em [`docs/05`](docs/05-estrategia-ia.md), evitando o anti-padrão de usar LLM para classificação tabular em saúde.
- **Conformidade por design:** LGPD, ANS e CFM tratados como requisito de arquitetura, não como anexo.
- **Três trilhas de cuidado:** Jovens (Júlia, 28), crônicos (Maria, 55) e idosos (João, 72), com cuidador no loop e atenção domiciliar para idosos.
- **Mensuração dupla:** Saúde do paciente *e* sinistralidade da operadora, lado a lado.
- **Provider-neutral:** GenAI via OpenRouter (default `anthropic/claude-haiku-4.5`), trocável para qualquer modelo via env var.
- **Protótipo demonstrável:** `docker compose up` e em segundos a stack completa responde com ML real e GenAI real.

## Cobertura por eixo técnico

| Eixo | Onde está respondido |
|---|---|
| Data, AI & Analytics | [`docs/05`](docs/05-estrategia-ia.md), [`prototype/notebooks/01-eda-e-treino.ipynb`](prototype/notebooks/01-eda-e-treino.ipynb) |
| Dev & Engineering | [`docs/02`](docs/02-arquitetura.md), [`prototype/`](prototype/), [`infra/architecture-target.md`](infra/architecture-target.md) |
| Digital & Innovation | [`docs/05`](docs/05-estrategia-ia.md), [`docs/07`](docs/07-modelo-de-negocio.md) |
| Management & Business | [`docs/07`](docs/07-modelo-de-negocio.md) |
| Integração em produção | [`docs/08`](docs/08-integracao-em-producao.md) |

---

**Autor:** Gabriel Ahrends · `gabriel.ahrends.andrade@gmail.com`
