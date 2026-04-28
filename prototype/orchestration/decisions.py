"""
Orquestrador: traduz risco + perfil em ação + canal.

Em produção essa lógica vive como workflow Temporal (ADR 006), com retries
idempotentes, sinais externos (consentimento revogado, alta hospitalar) e
escalonamento humano. Aqui é uma função pura para a fatia vertical do protótipo.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CareAction:
    action: str
    channel: str
    priority: str  # "rotina" | "agendamento_proativo" | "imediato"
    requires_human: bool


_RULES: dict[tuple[str, str], CareAction] = {
    # Jovens
    ("jovem", "verde"): CareAction(
        action="conteudo_preventivo",
        channel="push_app",
        priority="rotina",
        requires_human=False,
    ),
    ("jovem", "amarelo"): CareAction(
        action="agendar_checkup",
        channel="push_app",
        priority="agendamento_proativo",
        requires_human=False,
    ),
    ("jovem", "vermelho"): CareAction(
        action="telemedicina_24h",
        channel="push_app",
        priority="imediato",
        requires_human=True,
    ),
    # Crônicos
    ("cronico", "verde"): CareAction(
        action="lembrete_aferição_e_medicação",
        channel="push_app",
        priority="rotina",
        requires_human=False,
    ),
    ("cronico", "amarelo"): CareAction(
        action="agendar_revisão_cardiologia",
        channel="push_app+sms",
        priority="agendamento_proativo",
        requires_human=False,
    ),
    ("cronico", "vermelho"): CareAction(
        action="telemedicina_imediata_e_alerta_medico",
        channel="ligacao_ativa+telemed",
        priority="imediato",
        requires_human=True,
    ),
    # Idosos — sempre com cuidador no loop quando consentido
    ("idoso", "verde"): CareAction(
        action="lembrete_falado_e_visita_quinzenal",
        channel="voz+visita_domiciliar",
        priority="rotina",
        requires_human=True,
    ),
    ("idoso", "amarelo"): CareAction(
        action="visita_enfermagem_e_revisao_polifarmacia",
        channel="visita_domiciliar+cuidador",
        priority="agendamento_proativo",
        requires_human=True,
    ),
    ("idoso", "vermelho"): CareAction(
        action="contato_humano_imediato_e_telemed_geriatria",
        channel="ligacao_ativa+cuidador+telemed",
        priority="imediato",
        requires_human=True,
    ),
    # Demais
    ("demais", "verde"): CareAction(
        action="conteudo_preventivo",
        channel="push_app",
        priority="rotina",
        requires_human=False,
    ),
    ("demais", "amarelo"): CareAction(
        action="agendar_consulta",
        channel="push_app",
        priority="agendamento_proativo",
        requires_human=False,
    ),
    ("demais", "vermelho"): CareAction(
        action="telemedicina_24h",
        channel="push_app+sms",
        priority="imediato",
        requires_human=True,
    ),
}


def decide(profile: str, risk_class: str) -> CareAction:
    key = (profile, risk_class)
    if key not in _RULES:
        return _RULES[("demais", risk_class)]
    return _RULES[key]
