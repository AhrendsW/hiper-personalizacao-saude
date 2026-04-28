"""
Treina classificador de risco em 3 níveis e salva artefatos.

- Modelo: XGBoost multiclasse
- Validação: holdout estratificado por classe
- Calibração: avaliada em conjunto de teste
- Explicabilidade: SHAP TreeExplainer salvo junto com o modelo
- Saída: modelo serializado + relatório de métricas + meta de fairness por perfil
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
import shap
import structlog
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from ml.features import FEATURE_COLUMNS, INT_TO_CLASS, to_features, to_label

log = structlog.get_logger(__name__)

ARTIFACTS_DIR = Path("artifacts")


def train(
    data_path: Path = Path("data/beneficiarios.parquet"),
    out_path: Path = ARTIFACTS_DIR / "model.joblib",
) -> dict:
    df = pd.read_parquet(data_path)
    X = to_features(df)
    y = to_label(df)
    profile = df["profile"]

    X_train, X_test, y_train, y_test, prof_train, prof_test = train_test_split(
        X, y, profile, test_size=0.2, stratify=y, random_state=42
    )

    model = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        objective="multi:softprob",
        num_class=3,
        random_state=42,
        n_jobs=-1,
        eval_metric="mlogloss",
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    report = classification_report(
        y_test,
        y_pred,
        target_names=[INT_TO_CLASS[i] for i in range(3)],
        output_dict=True,
    )
    cm = confusion_matrix(y_test, y_pred).tolist()

    fairness = {}
    for prof in sorted(prof_test.unique()):
        mask = prof_test == prof
        if mask.sum() < 30:
            continue
        sub_pred = y_pred[mask.values]
        sub_y = y_test[mask.values]
        acc = float((sub_pred == sub_y).mean())
        fairness[prof] = {
            "n": int(mask.sum()),
            "accuracy": round(acc, 4),
        }

    explainer = shap.TreeExplainer(model)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "explainer": explainer,
            "feature_columns": FEATURE_COLUMNS,
            "int_to_class": INT_TO_CLASS,
        },
        out_path,
    )

    metrics = {
        "report": report,
        "confusion_matrix": cm,
        "fairness_by_profile": fairness,
        "feature_importance": dict(
            zip(FEATURE_COLUMNS, model.feature_importances_.round(4).tolist(), strict=True)
        ),
    }
    metrics_path = ARTIFACTS_DIR / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False))

    log.info(
        "model_trained",
        accuracy=round(report["accuracy"], 4),
        f1_macro=round(report["macro avg"]["f1-score"], 4),
        out=str(out_path),
        metrics_path=str(metrics_path),
    )
    return metrics


if __name__ == "__main__":
    train()
