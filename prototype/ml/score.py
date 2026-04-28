"""
Inferência online: classe de risco + probabilidades + top-K features explicativas (SHAP).
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from ml.features import FEATURE_COLUMNS

DEFAULT_MODEL_PATH = Path("artifacts/model.joblib")


@dataclass
class FeatureExplanation:
    name: str
    value: float
    contribution: float


@dataclass
class RiskPrediction:
    risk_class: str
    probabilities: dict[str, float]
    top_features: list[FeatureExplanation]


@lru_cache(maxsize=1)
def _load_bundle(model_path: str) -> dict[str, Any]:
    return joblib.load(model_path)


def predict(features: dict, model_path: Path | str = DEFAULT_MODEL_PATH) -> RiskPrediction:
    bundle = _load_bundle(str(model_path))
    model = bundle["model"]
    explainer = bundle["explainer"]
    int_to_class = bundle["int_to_class"]

    row = pd.DataFrame([{c: features[c] for c in FEATURE_COLUMNS}])
    proba = model.predict_proba(row)[0]
    cls_idx = int(np.argmax(proba))
    cls_name = int_to_class[cls_idx]

    shap_values = explainer.shap_values(row)
    contributions = shap_values[0, :, cls_idx] if shap_values.ndim == 3 else shap_values[0]
    contributions = np.asarray(contributions, dtype=float)

    pairs = sorted(
        zip(FEATURE_COLUMNS, row.iloc[0].tolist(), contributions.tolist(), strict=True),
        key=lambda t: abs(t[2]),
        reverse=True,
    )
    top = [
        FeatureExplanation(name=n, value=float(v), contribution=float(c)) for n, v, c in pairs[:3]
    ]

    return RiskPrediction(
        risk_class=cls_name,
        probabilities={int_to_class[i]: float(round(p, 4)) for i, p in enumerate(proba)},
        top_features=top,
    )
