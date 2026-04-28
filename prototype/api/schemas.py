"""Schemas Pydantic da API — validação de input e shape de resposta."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class WearableSnapshot(BaseModel):
    hr_rest_avg: float = Field(..., ge=30, le=200)
    hrv_avg: float = Field(..., ge=1, le=200)
    sleep_hours_avg: float = Field(..., ge=0, le=14)
    steps_daily_avg: float = Field(..., ge=0, le=40000)
    sbp_avg: float = Field(..., ge=70, le=240)
    dbp_avg: float = Field(..., ge=40, le=160)


class ClinicalSnapshot(BaseModel):
    adherence_gap: float = Field(..., ge=0, le=1)
    n_consult_12m: int = Field(..., ge=0, le=200)
    n_emergency_12m: int = Field(..., ge=0, le=50)
    n_admissions_12m: int = Field(..., ge=0, le=30)
    chronic_count: int = Field(..., ge=0, le=10)


class ScoreRequest(BaseModel):
    patient_id: str
    persona_name: str | None = None
    profile: Literal["jovem", "cronico", "idoso", "demais"]
    age: int = Field(..., ge=0, le=120)
    wearable: WearableSnapshot
    clinical: ClinicalSnapshot


class FeatureContribution(BaseModel):
    name: str
    value: float
    contribution: float


class ScoreResponse(BaseModel):
    patient_id: str
    risk_class: Literal["verde", "amarelo", "vermelho"]
    probabilities: dict[str, float]
    top_features: list[FeatureContribution]
    action: str
    channel: str
    priority: str
    requires_human: bool
    message: str
    message_source: str
    model_version: str = "xgboost-v0"


class EngagementEvent(BaseModel):
    patient_id: str
    decision_id: str | None = None
    action: str
    channel: str
    outcome: Literal["delivered", "opened", "executed", "ignored", "escalated"]


class EngagementAck(BaseModel):
    received: bool = True
    patient_id: str
