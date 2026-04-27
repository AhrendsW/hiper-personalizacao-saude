# Hiper Personalização do Cuidado — Unimed Nacional

> Solução ponta a ponta de IA para uma jornada de cuidado **hiper personalizada**, desenhada para **maximizar a saúde do beneficiário** e **reduzir a sinistralidade** da operadora.

**Case técnico — vaga AI Engineer / Profectum Tecnologia · FIAP MBA+ Discover · Unimed Nacional**

---

## TL;DR

Cada beneficiário é único. Tratá-los de forma idêntica é caro para a operadora e ruim para o paciente. Esta proposta combina **modelos de ML clássico** (decisão clínica auditável) com **GenAI** (comunicação personalizada e raciocínio sobre texto), em uma arquitetura de dados conforme com **LGPD** e **regulação ANS/CFM**, escalável para os **4,6M de beneficiários** da Unimed Nacional.

```
Wearables + Claims + Prontuário  →  ML decide risco  →  GenAI compõe ação  →  Engajamento
        (coleta)                     (tratamento+IA)     (personalização)      (mensuração)
```

## Demo em 60 segundos

```bash
cd prototype
docker compose up --build
# em outro terminal
curl -X POST localhost:8000/score \
  -H 'Content-Type: application/json' \
  -d @samples/maria.json
```

Saída esperada: score de risco, top features explicativas (SHAP) e mensagem personalizada gerada para a persona.

## Como navegar

| Eixo do case | Documento |
|---|---|
| Problema, proposta de valor, KPIs | [`docs/01-problema.md`](docs/01-problema.md) |
| Arquitetura ponta a ponta (C4) | [`docs/02-arquitetura.md`](docs/02-arquitetura.md) |
| Trilhas de cuidado por perfil (Júlia, Maria, João) | [`docs/03-trilhas-de-cuidado.md`](docs/03-trilhas-de-cuidado.md) |
| Dados, LGPD, ANS, CFM, segurança | [`docs/04-dados-e-conformidade.md`](docs/04-dados-e-conformidade.md) |
| Estratégia de IA — ML clássico vs GenAI | [`docs/05-estrategia-ia.md`](docs/05-estrategia-ia.md) |
| Mensuração de efetividade e engajamento | [`docs/06-mensuracao.md`](docs/06-mensuracao.md) |
| Modelo de negócio, GTM, escalabilidade, times | [`docs/07-modelo-de-negocio.md`](docs/07-modelo-de-negocio.md) |
| Decisões arquiteturais (ADRs) | [`docs/adr/`](docs/adr/) |
| Protótipo executável | [`prototype/`](prototype/) |
| Arquitetura-alvo de produção | [`infra/architecture-target.md`](infra/architecture-target.md) |

## Diferenciais da proposta

- **ML onde decide, GenAI onde comunica** — escolha técnica justificada em [`docs/05`](docs/05-estrategia-ia.md), evitando o anti-padrão de usar LLM para classificação tabular em saúde.
- **Conformidade por design** — LGPD, ANS e CFM tratados como requisito de arquitetura, não como anexo.
- **Três trilhas de cuidado** — jovens (Júlia, 28), crônicos (Maria, 55) e idosos (João, 72), preenchendo a lacuna deixada pelo case original.
- **Mensuração dupla** — saúde do paciente *e* sinistralidade da operadora, lado a lado.
- **Protótipo demonstrável** — não é só PowerPoint: roda local com `docker compose up`.

## Cobertura das questões norteadoras

| Eixo | Onde está respondido |
|---|---|
| Data, AI & Analytics | [`docs/05`](docs/05-estrategia-ia.md), [`prototype/notebooks/`](prototype/notebooks/) |
| Dev & Engineering | [`docs/02`](docs/02-arquitetura.md), [`prototype/src/`](prototype/src/), [`infra/architecture-target.md`](infra/architecture-target.md) |
| Digital & Innovation | [`docs/05`](docs/05-estrategia-ia.md), [`docs/07`](docs/07-modelo-de-negocio.md) |
| Management & Business | [`docs/07`](docs/07-modelo-de-negocio.md) |

---

**Autor:** Gabriel Ahrends · `gabriel.ahrends.andrade@gmail.com`
