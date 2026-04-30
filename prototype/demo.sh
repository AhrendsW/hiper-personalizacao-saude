#!/usr/bin/env bash
# Demo visual da plataforma — wrapper que executa demo.py via uv.
# Uso: ./demo.sh   (requer API rodando em localhost:8000)

set -euo pipefail

cd "$(dirname "$0")"

if ! command -v uv >/dev/null 2>&1; then
    echo "uv não encontrado. Instale com: brew install uv (https://docs.astral.sh/uv/)" >&2
    exit 1
fi

exec uv run python demo.py "$@"
