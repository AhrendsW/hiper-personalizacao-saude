"""
Demo visual da fatia vertical da plataforma.

Faz POST /score para as três personas (Júlia, Maria, João) e imprime
o resultado formatado com cores, separadores e blocos legíveis.

Uso típico em apresentação ao vivo: roda em paralelo a docker compose up
ou uvicorn local, e mostra o caminho ML -> SHAP -> orquestrador -> GenAI
em alguns segundos, sem JSON cru no terminal.

Para integração técnica (orquestrador, painel médico, BI), o contrato é
o JSON puro de POST /score; este script é apenas a camada de apresentação.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API_BASE = "http://localhost:8000"
SAMPLES_DIR = Path(__file__).parent / "samples"
PERSONAS = [
    ("julia", "Júlia", "28 anos", "jovem digitalmente ativa, sem comorbidades"),
    ("maria", "Maria", "55 anos", "hipertensa, baixa adesão à medicação"),
    ("joao", "João", "72 anos", "idoso, polifarmácia, internação recente"),
]


# ANSI escape codes
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GREY = "\033[90m"

    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"


RISK_COLOR = {"verde": C.GREEN, "amarelo": C.YELLOW, "vermelho": C.RED}
RISK_ICON = {"verde": "🟢", "amarelo": "🟡", "vermelho": "🔴"}

FEATURE_LABEL = {
    "age": "idade",
    "hr_rest_avg": "FC repouso",
    "hrv_avg": "HRV",
    "sleep_hours_avg": "sono (h)",
    "steps_daily_avg": "passos/dia",
    "sbp_avg": "pressão sistólica",
    "dbp_avg": "pressão diastólica",
    "adherence_gap": "lacuna de adesão",
    "n_consult_12m": "consultas 12m",
    "n_emergency_12m": "PS 12m",
    "n_admissions_12m": "internações 12m",
    "chronic_count": "comorbidades",
}


def hr(char: str = "═", color: str = C.CYAN, width: int = 60) -> str:
    return f"{color}{char * width}{C.RESET}"


def header(title: str) -> None:
    print()
    print(hr())
    print(f"{C.BOLD}{C.CYAN}  {title}{C.RESET}")
    print(hr())


def fetch_health() -> bool:
    try:
        with urllib.request.urlopen(f"{API_BASE}/health", timeout=2) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError):
        return False


def fetch_score(persona_file: Path) -> dict:
    data = persona_file.read_bytes()
    req = urllib.request.Request(
        f"{API_BASE}/score",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def format_value(name: str, value: float) -> str:
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    if name in {"sbp_avg", "dbp_avg", "hr_rest_avg", "hrv_avg"}:
        return f"{value}"
    if name == "steps_daily_avg":
        return f"{int(value):,}".replace(",", ".")
    if name == "adherence_gap":
        return f"{value:.2f}"
    if name == "sleep_hours_avg":
        return f"{value:.1f}"
    return f"{value}"


def render_persona(idx: int, total: int, key: str, name: str, age: str, desc: str) -> None:
    sample = SAMPLES_DIR / f"{key}.json"
    if not sample.exists():
        print(f"{C.RED}sample {sample} não encontrado{C.RESET}")
        return

    print()
    print(f"{C.BOLD}{C.MAGENTA}[{idx}/{total}]  {name}{C.RESET}  {C.GREY}· {age} · {desc}{C.RESET}")
    print(f"{C.GREY}{'─' * 60}{C.RESET}")

    started = time.perf_counter()
    try:
        result = fetch_score(sample)
    except Exception as exc:  # noqa: BLE001
        print(f"  {C.RED}falha ao chamar /score: {exc}{C.RESET}")
        return
    elapsed_ms = (time.perf_counter() - started) * 1000

    risk = result["risk_class"]
    risk_color = RISK_COLOR.get(risk, C.WHITE)
    risk_icon = RISK_ICON.get(risk, "·")
    confidence = max(result["probabilities"].values()) * 100

    print(
        f"  {C.BOLD}Risco:{C.RESET}      "
        f"{risk_icon} {risk_color}{C.BOLD}{risk.upper()}{C.RESET}  "
        f"{C.DIM}({confidence:.1f}% de confiança){C.RESET}"
    )
    src = result["message_source"]
    src_label = (
        f"{C.GREEN}LLM real{C.RESET}"
        if src == "llm"
        else f"{C.YELLOW}fallback determinístico{C.RESET}"
    )
    print(f"  {C.BOLD}Mensagem:{C.RESET}   gerada via {src_label}")
    print(f"  {C.BOLD}Latência:{C.RESET}   {elapsed_ms:.0f} ms")

    print()
    print(f"  {C.BOLD}Top features explicativas (SHAP):{C.RESET}")
    for i, feat in enumerate(result["top_features"], start=1):
        label = FEATURE_LABEL.get(feat["name"], feat["name"])
        value = format_value(feat["name"], feat["value"])
        contrib = feat["contribution"]
        color = C.RED if contrib >= 0 else C.GREEN
        print(f"     {i}. {label:<22}  {value:>10}   {color}{contrib:+.2f}{C.RESET}")

    print()
    print(f"  {C.BOLD}Decisão da jornada:{C.RESET}")
    requires_human = "✓ humano no loop" if result["requires_human"] else "automatizado"
    print(f"     Ação    → {C.CYAN}{result['action']}{C.RESET}")
    print(f"     Canal   → {C.CYAN}{result['channel']}{C.RESET}")
    print(
        f"     Prio.   → {C.CYAN}{result['priority']}{C.RESET}  {C.DIM}({requires_human}){C.RESET}"
    )

    print()
    print(f"  {C.BOLD}Mensagem para o beneficiário:{C.RESET}")
    msg = result["message"]
    for line in wrap(msg, width=66):
        print(f"     {C.ITALIC}{line}{C.RESET}")


def wrap(text: str, width: int) -> list[str]:
    words = text.split()
    out, current = [], ""
    for word in words:
        if len(current) + len(word) + 1 > width and current:
            out.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        out.append(current)
    return out


def main() -> int:
    header("DEMO · Hiper Personalização do Cuidado em Saúde")
    print(f"  {C.DIM}Endpoint: {API_BASE}/score{C.RESET}")
    print(f"  {C.DIM}Personas: Júlia (jovem) · Maria (crônica) · João (idoso){C.RESET}")

    if not fetch_health():
        print()
        print(f"  {C.RED}{C.BOLD}API não está respondendo em {API_BASE}.{C.RESET}")
        print("  Suba a stack antes de rodar este script:")
        print(f"     {C.CYAN}docker compose up --build{C.RESET}  (Caminho 1)")
        print(f"     {C.CYAN}uv run uvicorn api.main:app --port 8000{C.RESET}  (Caminho 2)")
        return 1

    for idx, (key, name, age, desc) in enumerate(PERSONAS, start=1):
        render_persona(idx, len(PERSONAS), key, name, age, desc)

    print()
    print(hr())
    print(f"  {C.BOLD}Notas:{C.RESET}")
    print(
        f"  {C.GREY}·{C.RESET} O contrato técnico do endpoint é JSON puro "
        f"({C.CYAN}curl ... | jq{C.RESET} para ver bruto)."
    )
    print(
        f"  {C.GREY}·{C.RESET} Em produção, /score é consumido por orquestrador, "
        f"painel médico e BI (ver {C.CYAN}docs/08{C.RESET})."
    )
    print(
        f"  {C.GREY}·{C.RESET} Mensagem com {C.GREEN}LLM real{C.RESET} requer "
        f"{C.CYAN}OPENROUTER_API_KEY{C.RESET} no {C.CYAN}.env{C.RESET}."
    )
    print(hr())
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
