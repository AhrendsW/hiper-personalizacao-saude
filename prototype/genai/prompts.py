"""
Templates de prompt por persona, com tom calibrado por trilha de cuidado.

Princípios:
- Persona define tom, canal e nível de detalhe.
- Risco define urgência e direcionamento (preventivo / consulta / telemed imediata).
- Top features SHAP entram como justificativa concreta — não como jargão técnico.
- Mensagem nunca prescreve, nunca diagnostica, nunca substitui orientação médica.
"""

from __future__ import annotations

PERSONA_PROFILES = {
    "jovem": {
        "tone": "leve, direto, sem paternalismo",
        "channel": "push do app",
        "guidance": (
            "Use linguagem cotidiana e curta. Foque em hábito e prevenção. "
            "Evite alarmismo. Trate o leitor como pessoa ativa e capaz."
        ),
    },
    "cronico": {
        "tone": "apoiador, sem culpabilização",
        "channel": "push + lembrete no app",
        "guidance": (
            "Reconheça o esforço. Cite os indicadores observados de forma clara. "
            "Sugira próximo passo simples (aferir, agendar revisão, ajustar rotina). "
            "Nunca culpe falha de adesão; ofereça apoio."
        ),
    },
    "idoso": {
        "tone": "claro, paciente, com instruções curtas",
        "channel": "voz (TTS) ou WhatsApp em texto curto, com cópia para o cuidador",
        "guidance": (
            "Frases curtas e diretas. Uma instrução por vez. "
            "Inclua apoio do cuidador autorizado quando aplicável. "
            "Priorize segurança — risco vermelho dispara contato humano antes da mensagem."
        ),
    },
    "demais": {
        "tone": "neutro e informativo",
        "channel": "push do app",
        "guidance": ("Linguagem clara e objetiva. Foque na ação concreta sugerida."),
    },
}

RISK_GUIDANCE = {
    "verde": "manter hábitos saudáveis, lembrete de prevenção",
    "amarelo": "agendar revisão ou consulta preventiva nas próximas duas semanas",
    "vermelho": "contato com profissional de saúde com prioridade — telemedicina ou emergência",
}


def build_user_prompt(
    profile: str,
    risk_class: str,
    top_features: list[dict],
    persona_name: str | None = None,
) -> str:
    persona = PERSONA_PROFILES.get(profile, PERSONA_PROFILES["demais"])
    feature_lines = "\n".join(
        f"  - {f['name']} = {f['value']} (peso na decisão: {f['contribution']:+.2f})"
        for f in top_features
    )
    name_block = f"Nome: {persona_name}\n" if persona_name else ""
    return (
        f"{name_block}"
        f"Perfil de cuidado: {profile}\n"
        f"Tom desejado: {persona['tone']}\n"
        f"Canal alvo: {persona['channel']}\n"
        f"Nível de risco classificado pelo modelo: {risk_class}\n"
        f"Direcionamento clínico geral: {RISK_GUIDANCE[risk_class]}\n"
        f"Indicadores que mais influenciaram a decisão (SHAP):\n"
        f"{feature_lines}\n\n"
        f"Diretriz de redação: {persona['guidance']}\n\n"
        f"Tarefa: redija UMA mensagem curta (máx. 3 frases, 280 caracteres) "
        f"para o beneficiário, no tom acima, citando 1-2 indicadores em linguagem "
        f"cotidiana (sem jargão clínico) e com chamada de ação clara. "
        f"Não prescreva, não diagnostique, não cite valores numéricos exatos."
    )


SYSTEM_PROMPT = (
    "Você é um copiloto de comunicação de saúde para uma operadora brasileira. "
    "Sua função é redigir mensagens curtas, empáticas, em português do Brasil, "
    "que conectem o que o modelo de risco identificou ao próximo passo de cuidado. "
    "Restrições:\n"
    "- Nunca prescreva medicação, dose ou tratamento.\n"
    "- Nunca emita diagnóstico.\n"
    "- Sempre lembre que a mensagem complementa, não substitui, orientação médica.\n"
    "- Mantenha tom respeitoso e centrado no beneficiário.\n"
    "- Devolva apenas o texto da mensagem, sem aspas, sem cabeçalho, sem explicação."
)
