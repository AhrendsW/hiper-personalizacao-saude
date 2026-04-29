# Protótipo

Fatia vertical do case: **wearable + claims sintético → ML decide risco → GenAI compõe mensagem → API entrega**.

## Como rodar

### Opção 1 — Docker (recomendado para demo)

```bash
docker compose up --build
# em outro terminal
curl -X POST localhost:8000/score -H 'Content-Type: application/json' -d @samples/maria.json
```

### Opção 2 — Local (Python 3.11+)

```bash
cd prototype
python -m venv .venv && source .venv/bin/activate
pip install -e .

# 1) gera dataset sintético (10k beneficiários × 30 dias)
python -m ingestion.generate_data

# 2) treina modelo de risco (XGBoost) e salva em artifacts/
python -m ml.train

# 3) sobe API
uvicorn api.main:app --reload --port 8000
```

## Estrutura

```
prototype/
├── pyproject.toml
├── docker-compose.yml
├── Dockerfile
├── samples/                        # payloads de exemplo (Júlia, Maria, João)
├── data/                           # dataset sintético (gerado)
├── artifacts/                      # modelo treinado (gerado)
├── src/
│   ├── ingestion/generate_data.py  # gerador de dados sintéticos
│   ├── ml/
│   │   ├── features.py             # feature engineering
│   │   ├── train.py                # treino + SHAP
│   │   └── score.py                # inferência + explicabilidade
│   ├── genai/
│   │   ├── client.py               # OpenRouter (OpenAI-compatible) + fallback determinístico
│   │   └── prompts.py              # templates por persona
│   ├── api/
│   │   ├── main.py                 # FastAPI
│   │   ├── schemas.py              # Pydantic
│   │   └── routes.py
│   └── orchestration/
│       └── decisions.py            # regra risco → ação → canal
├── notebooks/                      # EDA + treino didático
└── tests/
```

## Variáveis de ambiente

Crie `.env` baseado em `.env.example`:

- `OPENROUTER_API_KEY` — opcional. Se ausente, GenAI cai em fallback determinístico.
- `OPENROUTER_MODEL` — modelo a usar via OpenRouter. Default `anthropic/claude-haiku-4.5`.
  Pode ser trocado para `openai/gpt-4o-mini`, `google/gemini-flash-1.5`, etc.
- `LOG_LEVEL` — padrão `INFO`.
- `MODEL_PATH` — caminho do modelo (default `artifacts/model.joblib`).

## Fluxo do `/score`

```
POST /score
  └→ valida payload (Pydantic)
  └→ extrai features (compatíveis com treino)
  └→ ML clássico classifica risco (verde/amarelo/vermelho)
  └→ SHAP explica top 3 features
  └→ orquestrador decide canal e ação por persona
  └→ GenAI compõe mensagem (com fallback determinístico)
  └→ retorna JSON com risco, top features, ação, canal e mensagem
```

## Limitações conhecidas

- Dados são sintéticos — distribuição realista mas sem PHI.
- ML sem feature store; treino e inferência usam mesmo módulo `features.py` para evitar skew.
- GenAI usa um único prompt por persona — em produção haveria roteamento, cache semântico, golden set.
- Não usa Kafka, Airflow ou Temporal — esses estão na **arquitetura-alvo**, não no protótipo (ver `infra/architecture-target.md`).
