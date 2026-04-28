"""
Definição única de features.

Importado tanto pelo treino quanto pela inferência — garante que a mesma
transformação seja aplicada nos dois caminhos. Em produção esse papel é
do Feature Store (Feast).
"""

from __future__ import annotations

import pandas as pd

FEATURE_COLUMNS: list[str] = [
    "age",
    "hr_rest_avg",
    "hrv_avg",
    "sleep_hours_avg",
    "steps_daily_avg",
    "sbp_avg",
    "dbp_avg",
    "adherence_gap",
    "n_consult_12m",
    "n_emergency_12m",
    "n_admissions_12m",
    "chronic_count",
]

TARGET_COLUMN = "risk_class"

CLASS_TO_INT = {"verde": 0, "amarelo": 1, "vermelho": 2}
INT_TO_CLASS = {v: k for k, v in CLASS_TO_INT.items()}


def to_features(df: pd.DataFrame) -> pd.DataFrame:
    """Seleciona e ordena as colunas de feature."""
    return df[FEATURE_COLUMNS].copy()


def to_label(df: pd.DataFrame) -> pd.Series:
    return df[TARGET_COLUMN].map(CLASS_TO_INT).astype("int64")
