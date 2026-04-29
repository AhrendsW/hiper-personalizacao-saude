# Protótipo. Fatia vertical executável

> **wearable + claims sintético → ML decide risco → GenAI compõe mensagem → API entrega**

Stack: Python 3.11 · FastAPI · XGBoost · SHAP · OpenRouter (provider-neutral) · Docker · uv.

---

## Sumário

1. [Pré-requisitos por caminho](#pré-requisitos-por-caminho)
2. [Configuração do `.env` e da chave do OpenRouter](#configuração-do-env-e-da-chave-do-openrouter)
3. [Caminho 1. Docker (recomendado)](#caminho-1--docker-recomendado)
4. [Caminho 2. Local com `uv`](#caminho-2--local-com-uv)
5. [Caminho 3. CLI / scripts diretos](#caminho-3--cli--scripts-diretos)
6. [Como testar a API](#como-testar-a-api)
7. [Trocar de modelo de LLM](#trocar-de-modelo-de-llm)
8. [Estrutura do código](#estrutura-do-código)
9. [Fluxo do `/score`](#fluxo-do-score)
10. [Limitações conhecidas e próximos passos](#limitações-conhecidas-e-próximos-passos)

---

## Pré-requisitos por caminho

| Caminho | Requer |
|---|---|
| **Docker** | Docker Desktop, OrbStack ou Colima ([instalação](https://docs.docker.com/get-started/get-docker/)) |
| **uv local** | Python 3.11+, [uv](https://docs.astral.sh/uv/) e dependência de sistema do XGBoost (`brew install libomp` no macOS, `apt install libgomp1` no Linux) |
| **CLI / scripts** | Python 3.11+, uv |

`OPENROUTER_API_KEY` é **opcional** em todos os caminhos. Sem ela, a API responde normalmente com mensagens via **fallback determinístico** (template parametrizado). Com ela, as mensagens vêm do LLM real.

---

## Configuração do `.env` e da chave do OpenRouter

### 1. Crie o `.env` a partir do exemplo

```bash
cp prototype/.env.example prototype/.env
```

Conteúdo:

```dotenv
OPENROUTER_API_KEY=
LOG_LEVEL=INFO
MODEL_PATH=artifacts/model.joblib
DATA_PATH=data/beneficiarios.parquet
OPENROUTER_MODEL=anthropic/claude-haiku-4.5
```

### 2. Obtenha a chave do OpenRouter (~2 min)

1. Crie conta em <https://openrouter.ai/>
2. Acesse <https://openrouter.ai/keys> → **Create key**
3. Adicione créditos em <https://openrouter.ai/credits>. Qualquer valor pequeno (US$ 1-5) já demonstra o protótipo várias centenas de vezes em Haiku
4. Cole a chave em `prototype/.env`:

```dotenv
OPENROUTER_API_KEY=sk-or-v1-...
```

> O `.env` está em `prototype/.gitignore`. Nunca vai pro repo.

### 3. Como cada caminho consome o `.env`

| Caminho | Como o `.env` é lido |
|---|---|
| **Docker** | `docker-compose.yml` interpola `${OPENROUTER_API_KEY}` automaticamente a partir do `.env` no diretório do compose |
| **uv local** | `api/main.py` chama `load_dotenv()` no startup. Lê `.env` do diretório atual |
| **CLI** | Igual ao uv local. Ou exporta no shell: `export OPENROUTER_API_KEY=sk-or-v1-...` |

---

## Caminho 1. Docker (recomendado)

Build da imagem treina o modelo internamente, então o container sobe pronto.

```bash
cd prototype
docker compose up --build
```

A primeira vez leva ~30s (instala deps + treina modelo). Próximas subidas: ~3s.

API em <http://localhost:8000>. Swagger em <http://localhost:8000/docs>.

Para parar:

```bash
docker compose down
```

---

## Caminho 2. Local com `uv`

```bash
cd prototype
uv sync                                    # instala deps, cria .venv
uv run python -m ingestion.generate_data   # gera dataset sintético
uv run python -m ml.train                  # treina modelo + SHAP
uv run uvicorn api.main:app --port 8000    # sobe API
```

API em <http://localhost:8000>.

Para rodar testes:

```bash
uv run pytest -q
```

Para lint:

```bash
uv run ruff check .
```

---

## Caminho 3. CLI / scripts diretos

Útil para validação rápida sem subir API.

```bash
cd prototype
uv sync
uv run python -m ingestion.generate_data
uv run python -m ml.train
```

Inferência direta sem HTTP:

```python
from ml.score import predict

features = {
    "age": 55,
    "hr_rest_avg": 80, "hrv_avg": 32, "sleep_hours_avg": 5.8,
    "steps_daily_avg": 4200, "sbp_avg": 148, "dbp_avg": 92,
    "adherence_gap": 0.6,
    "n_consult_12m": 5, "n_emergency_12m": 1,
    "n_admissions_12m": 0, "chronic_count": 1,
}
print(predict(features))
```

Notebook didático em [`notebooks/01-eda-e-treino.ipynb`](notebooks/01-eda-e-treino.ipynb). Abra com:

```bash
uv run --with jupyter jupyter lab notebooks/
```

---

## Como testar a API

### Pelo Swagger
<http://localhost:8000/docs>. Clique em `POST /score`, **Try it out**, cole o conteúdo de qualquer arquivo em `samples/` e **Execute**.

### Por curl

```bash
curl -X POST localhost:8000/score \
  -H 'Content-Type: application/json' \
  -d @samples/maria.json
```

Personas disponíveis em `samples/`: `julia.json` (jovem), `maria.json` (crônica), `joao.json` (idoso).

### Customizando o input

```bash
curl -X POST localhost:8000/score -H 'Content-Type: application/json' -d '{
  "patient_id": "TESTE",
  "persona_name": "Carlos",
  "profile": "cronico",
  "age": 50,
  "wearable": {"hr_rest_avg":72,"hrv_avg":42,"sleep_hours_avg":7,"steps_daily_avg":6500,"sbp_avg":132,"dbp_avg":85},
  "clinical": {"adherence_gap":0.25,"n_consult_12m":3,"n_emergency_12m":0,"n_admissions_12m":0,"chronic_count":1}
}'
```

### Registrando engajamento

```bash
curl -X POST localhost:8000/event -H 'Content-Type: application/json' -d '{
  "patient_id": "BEN0000001",
  "action": "telemedicina_imediata_e_alerta_medico",
  "channel": "ligacao_ativa+telemed",
  "outcome": "executed"
}'
```

---

## Trocar de modelo de LLM

A arquitetura é **provider-neutral via OpenRouter**. Trocar de modelo é só uma variável de ambiente:

```dotenv
OPENROUTER_MODEL=anthropic/claude-haiku-4.5     # default, equilíbrio qualidade/custo
# OPENROUTER_MODEL=openai/gpt-4o-mini             # mais barato
# OPENROUTER_MODEL=google/gemini-flash-1.5        # latência baixa
# OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct  # open source
```

Lista completa em <https://openrouter.ai/models>.

> Sem `OPENROUTER_API_KEY`, o sistema cai em **fallback determinístico**. Beneficiário recebe mensagem mais genérica, mas a jornada não trava. Princípio de "falha segura" em saúde.

---

## Estrutura do código

```
prototype/
├── pyproject.toml + uv.lock          dependências (uv)
├── Dockerfile + docker-compose.yml   imagem que treina e roda
├── .env.example                      template de configuração
├── samples/                          payloads de exemplo (3 personas)
├── data/                             dataset sintético (gerado)
├── artifacts/                        modelo treinado + métricas (gerado)
├── ingestion/
│   └── generate_data.py              gerador de dados sintéticos
├── ml/
│   ├── features.py                   definição única de features
│   ├── train.py                      treino XGBoost + SHAP + métricas
│   └── score.py                      inferência online com explicabilidade
├── genai/
│   ├── client.py                     cliente OpenRouter + fallback determinístico
│   └── prompts.py                    templates por persona
├── orchestration/
│   └── decisions.py                  matriz declarativa (perfil × risco) → ação
├── api/
│   ├── main.py                       FastAPI: /health, /score, /event
│   └── schemas.py                    Pydantic com validação clínica
├── notebooks/
│   └── 01-eda-e-treino.ipynb         EDA + treino + SHAP
└── tests/                            13 testes (orquestração, GenAI, API)
```

---

## Fluxo do `/score`

```
POST /score (payload Pydantic validado)
  └→ extrai features (mesmo módulo do treino, sem skew)
  └→ ML clássico (XGBoost) classifica em verde/amarelo/vermelho com prob calibrada
  └→ SHAP TreeExplainer extrai top-3 features explicativas
  └→ orquestrador decide ação + canal + prioridade + requires_human por trilha
  └→ GenAI (OpenRouter) compõe mensagem personalizada usando persona + risco + features
      └→ se key ausente, falha ou validação rejeita → fallback determinístico
  └→ retorna JSON com tudo + decision_id propagado em logs estruturados
```

---

## Limitações conhecidas e próximos passos

| Limitação | Observação |
|---|---|
| **Dados sintéticos** | Distribuição realista mas sem PHI. Não vale como modelo clínico real. |
| **Sem feature store** | Treino e inferência usam o mesmo módulo `features.py`. Em produção, Feast com online (Redis) e offline (Iceberg). |
| **Prompt único por persona** | Em produção, golden set + roteamento por modelo + cache semântico. |
| **Sem Kafka/Airflow/Temporal** | Documentados em [`../infra/architecture-target.md`](../infra/architecture-target.md) com diagrama do gap. |
| **Modelo determinístico** | Sem retreino contínuo. Em produção, MLflow + Evidently + gate de promoção (ver `docs/05` e ADR 003-005). |
| **Como o `/score` é chamado de verdade** | Ver [`../docs/08-integracao-em-producao.md`](../docs/08-integracao-em-producao.md). |
