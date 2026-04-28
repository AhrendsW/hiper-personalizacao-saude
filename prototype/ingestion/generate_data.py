"""
Gerador de dados sintéticos para o protótipo.

Cria 10k beneficiários distribuídos em 3 trilhas (jovem / crônico / idoso) com:
- 30 dias de sinais de wearable (HR, HRV, sono, passos, PA estimada)
- features de claims agregadas (consultas, exames, internações no último ano)
- features de adesão (gap dispensação x prescrição)

A distribuição emula correlações clínicas plausíveis sem usar PHI real.
O target (`risk_class`) é gerado por uma função latente com ruído — o modelo
deve aprender a recuperar a estrutura, não decorar.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import structlog

log = structlog.get_logger(__name__)

RNG = np.random.default_rng(seed=42)

PROFILES = {
    "jovem": {"share": 0.40, "age_range": (18, 39)},
    "cronico": {"share": 0.25, "age_range": (40, 64)},
    "idoso": {"share": 0.15, "age_range": (65, 90)},
    "demais": {"share": 0.20, "age_range": (18, 75)},
}


def _draw_profile(n: int) -> np.ndarray:
    profiles = list(PROFILES.keys())
    weights = np.array([PROFILES[p]["share"] for p in profiles])
    weights = weights / weights.sum()
    return RNG.choice(profiles, size=n, p=weights)


def _draw_age(profile: str) -> int:
    lo, hi = PROFILES[profile]["age_range"]
    return int(RNG.integers(lo, hi + 1))


def _draw_features_for(profile: str, age: int) -> dict:
    """Features mensais agregadas por beneficiário, com correlação por perfil."""
    if profile == "jovem":
        hr_rest = RNG.normal(64, 6)
        hrv = RNG.normal(60, 12)
        sleep_h = RNG.normal(7.0, 1.0)
        steps = RNG.normal(9000, 2500)
        sbp = RNG.normal(118, 8)
        dbp = RNG.normal(75, 6)
        adherence_gap = RNG.beta(2, 8)
        n_consult_12m = RNG.poisson(0.8)
        n_emergency_12m = RNG.poisson(0.05)
        n_admissions_12m = 0
        chronic_count = 0
    elif profile == "cronico":
        hr_rest = RNG.normal(78, 8)
        hrv = RNG.normal(38, 10)
        sleep_h = RNG.normal(6.2, 1.2)
        steps = RNG.normal(5500, 2200)
        sbp = RNG.normal(142, 14)
        dbp = RNG.normal(90, 9)
        adherence_gap = RNG.beta(4, 6)
        n_consult_12m = RNG.poisson(4)
        n_emergency_12m = RNG.poisson(0.5)
        n_admissions_12m = RNG.poisson(0.3)
        chronic_count = int(RNG.integers(1, 4))
    elif profile == "idoso":
        hr_rest = RNG.normal(74, 9)
        hrv = RNG.normal(28, 9)
        sleep_h = RNG.normal(6.0, 1.4)
        steps = RNG.normal(3500, 1800)
        sbp = RNG.normal(138, 16)
        dbp = RNG.normal(82, 10)
        adherence_gap = RNG.beta(5, 5)
        n_consult_12m = RNG.poisson(6)
        n_emergency_12m = RNG.poisson(0.9)
        n_admissions_12m = RNG.poisson(0.6)
        chronic_count = int(RNG.integers(1, 5))
    else:
        hr_rest = RNG.normal(70, 9)
        hrv = RNG.normal(48, 14)
        sleep_h = RNG.normal(6.8, 1.2)
        steps = RNG.normal(7000, 2800)
        sbp = RNG.normal(126, 12)
        dbp = RNG.normal(80, 8)
        adherence_gap = RNG.beta(2, 6)
        n_consult_12m = RNG.poisson(2)
        n_emergency_12m = RNG.poisson(0.2)
        n_admissions_12m = RNG.poisson(0.1)
        chronic_count = int(RNG.integers(0, 2))

    return {
        "age": age,
        "profile": profile,
        "hr_rest_avg": float(np.clip(hr_rest, 40, 130)),
        "hrv_avg": float(np.clip(hrv, 5, 120)),
        "sleep_hours_avg": float(np.clip(sleep_h, 3, 11)),
        "steps_daily_avg": float(np.clip(steps, 200, 25000)),
        "sbp_avg": float(np.clip(sbp, 85, 200)),
        "dbp_avg": float(np.clip(dbp, 50, 130)),
        "adherence_gap": float(np.clip(adherence_gap, 0, 1)),
        "n_consult_12m": int(n_consult_12m),
        "n_emergency_12m": int(n_emergency_12m),
        "n_admissions_12m": int(n_admissions_12m),
        "chronic_count": int(chronic_count),
    }


def _latent_risk_score(row: dict) -> float:
    """Função latente que combina os fatores. O modelo deve aprender a aproximar."""
    score = 0.0
    score += 0.030 * (row["age"] - 40)
    score += 0.020 * max(0.0, row["sbp_avg"] - 130)
    score += 0.030 * max(0.0, row["dbp_avg"] - 85)
    score += 0.025 * max(0.0, row["hr_rest_avg"] - 75)
    score += 0.020 * max(0.0, 45 - row["hrv_avg"])
    score += 0.250 * row["chronic_count"]
    score += 0.300 * row["n_admissions_12m"]
    score += 0.150 * row["n_emergency_12m"]
    score += 0.040 * max(0.0, 6.5 - row["sleep_hours_avg"])
    score += 0.500 * row["adherence_gap"] * (row["chronic_count"] > 0)
    score -= 0.030 * (row["steps_daily_avg"] / 1000)
    return score


def _bin_risk(score: float, noise: float) -> str:
    perturbed = score + noise
    if perturbed < 0.6:
        return "verde"
    if perturbed < 1.6:
        return "amarelo"
    return "vermelho"


def generate(n: int = 10_000, out_path: Path | None = None) -> pd.DataFrame:
    out_path = out_path or Path("data/beneficiarios.parquet")
    profiles = _draw_profile(n)
    rows = []
    for i in range(n):
        profile = str(profiles[i])
        age = _draw_age(profile)
        feats = _draw_features_for(profile, age)
        score = _latent_risk_score(feats)
        noise = float(RNG.normal(0, 0.25))
        feats["risk_class"] = _bin_risk(score, noise)
        feats["patient_id"] = f"BEN{i:07d}"
        rows.append(feats)

    df = pd.DataFrame(rows)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)

    dist = df["risk_class"].value_counts(normalize=True).round(3).to_dict()
    log.info(
        "synthetic_dataset_generated",
        rows=len(df),
        out_path=str(out_path),
        distribution=dist,
    )
    return df


if __name__ == "__main__":
    generate()
