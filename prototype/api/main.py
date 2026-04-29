"""API do protótipo — fatia vertical da plataforma."""

from __future__ import annotations

import os
import uuid

import structlog
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from api.schemas import (
    EngagementAck,
    EngagementEvent,
    FeatureContribution,
    ScoreRequest,
    ScoreResponse,
)
from genai.client import generate_message
from ml.score import predict
from orchestration.decisions import decide

load_dotenv()
log = structlog.get_logger(__name__)

app = FastAPI(
    title="Hiper Personalização do Cuidado — protótipo",
    description=(
        "Fatia vertical: wearable+claims → ML decide risco → GenAI compõe mensagem → API entrega."
    ),
    version="0.1.0",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/score", response_model=ScoreResponse)
def score(req: ScoreRequest) -> ScoreResponse:
    decision_id = uuid.uuid4().hex
    log.info(
        "score_request",
        decision_id=decision_id,
        patient_id=req.patient_id,
        profile=req.profile,
    )

    features = {
        "age": req.age,
        **req.wearable.model_dump(),
        **req.clinical.model_dump(),
    }

    try:
        risk = predict(features)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="Modelo não encontrado. Rode `uv run python -m ml.train` antes.",
        ) from exc

    action = decide(req.profile, risk.risk_class)

    top_features_payload = [
        {"name": f.name, "value": f.value, "contribution": f.contribution}
        for f in risk.top_features
    ]
    msg = generate_message(
        profile=req.profile,
        risk_class=risk.risk_class,
        top_features=top_features_payload,
        persona_name=req.persona_name,
    )

    log.info(
        "score_decision",
        decision_id=decision_id,
        patient_id=req.patient_id,
        risk=risk.risk_class,
        action=action.action,
        channel=action.channel,
        message_source=msg.source,
    )

    return ScoreResponse(
        patient_id=req.patient_id,
        risk_class=risk.risk_class,
        probabilities=risk.probabilities,
        top_features=[FeatureContribution(**fp) for fp in top_features_payload],
        action=action.action,
        channel=action.channel,
        priority=action.priority,
        requires_human=action.requires_human,
        message=msg.text,
        message_source=msg.source,
    )


@app.post("/event", response_model=EngagementAck)
def event(evt: EngagementEvent) -> EngagementAck:
    log.info(
        "engagement_event",
        patient_id=evt.patient_id,
        decision_id=evt.decision_id,
        action=evt.action,
        channel=evt.channel,
        outcome=evt.outcome,
    )
    return EngagementAck(patient_id=evt.patient_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=False,
    )
