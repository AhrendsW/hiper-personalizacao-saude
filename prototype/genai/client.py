"""
Cliente GenAI com fallback determinístico.

- Se ANTHROPIC_API_KEY estiver definida, chama Claude via SDK oficial.
- Caso contrário, ou em caso de erro/validação que falha, monta mensagem
  por template determinístico — beneficiário recebe mensagem mais genérica,
  mas a jornada não trava.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import structlog

from genai.prompts import RISK_GUIDANCE, SYSTEM_PROMPT, build_user_prompt

log = structlog.get_logger(__name__)

DEFAULT_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
MAX_OUTPUT_TOKENS = 200


@dataclass
class GeneratedMessage:
    text: str
    source: str  # "llm" ou "fallback"
    model: str | None


def _fallback_message(profile: str, risk_class: str, top_features: list[dict]) -> str:
    main = top_features[0]["name"] if top_features else "seus indicadores"
    pretty = {
        "sbp_avg": "sua pressão",
        "dbp_avg": "sua pressão diastólica",
        "hr_rest_avg": "sua frequência cardíaca de repouso",
        "hrv_avg": "sua variabilidade cardíaca",
        "sleep_hours_avg": "seu sono",
        "steps_daily_avg": "seu nível de atividade",
        "adherence_gap": "a regularidade da sua medicação",
        "n_admissions_12m": "seu histórico recente",
        "chronic_count": "suas condições acompanhadas",
        "age": "seu perfil",
    }.get(main, "seus indicadores")

    if risk_class == "vermelho":
        cta = "Vamos agendar um contato com a equipe de saúde nas próximas horas?"
    elif risk_class == "amarelo":
        cta = "Que tal agendar uma revisão preventiva nas próximas duas semanas?"
    else:
        cta = "Continue com os bons hábitos e acompanhe seus dados pelo app."

    if profile == "idoso":
        return f"Olá. Notamos algo importante em {pretty}. {cta} Estamos aqui para apoiar você."
    if profile == "cronico":
        return (
            f"Vimos uma mudança em {pretty} nos últimos dias. "
            f"{cta} "
            f"Esta mensagem complementa, não substitui, orientação médica."
        )
    return f"Olhando {pretty}, vale uma atenção a mais. {cta}"


def _validate_response(text: str) -> bool:
    """Sanidade básica de resposta — em produção esta camada faz mais coisa."""
    if not text or not text.strip():
        return False
    if len(text) > 400:
        return False
    forbidden = ["mg", "ml", "dose", "comprimido", "prescrev", "diagnostic"]
    lower = text.lower()
    return not any(token in lower for token in forbidden)


def generate_message(
    profile: str,
    risk_class: str,
    top_features: list[dict],
    persona_name: str | None = None,
) -> GeneratedMessage:
    if risk_class not in RISK_GUIDANCE:
        raise ValueError(f"risk_class inválido: {risk_class}")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        log.info("genai_fallback", reason="no_api_key", profile=profile, risk=risk_class)
        return GeneratedMessage(
            text=_fallback_message(profile, risk_class, top_features),
            source="fallback",
            model=None,
        )

    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)
        user_prompt = build_user_prompt(profile, risk_class, top_features, persona_name)
        resp = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=MAX_OUTPUT_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = "".join(
            block.text for block in resp.content if getattr(block, "type", "") == "text"
        ).strip()

        if not _validate_response(text):
            log.warning(
                "genai_response_invalid",
                profile=profile,
                risk=risk_class,
                length=len(text),
            )
            return GeneratedMessage(
                text=_fallback_message(profile, risk_class, top_features),
                source="fallback",
                model=DEFAULT_MODEL,
            )

        return GeneratedMessage(text=text, source="llm", model=DEFAULT_MODEL)

    except Exception as exc:
        log.error("genai_call_failed", error=str(exc), profile=profile, risk=risk_class)
        return GeneratedMessage(
            text=_fallback_message(profile, risk_class, top_features),
            source="fallback",
            model=None,
        )
