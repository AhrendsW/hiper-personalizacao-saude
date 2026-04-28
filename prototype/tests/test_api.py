import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def _load(name: str) -> dict:
    return json.loads((Path("samples") / f"{name}.json").read_text())


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


@pytest.mark.parametrize(
    "persona,expected_risk",
    [
        ("julia", "verde"),
        ("maria", "vermelho"),
        ("joao", "vermelho"),
    ],
)
def test_score_classifica_personas(client, persona, expected_risk):
    payload = _load(persona)
    r = client.post("/score", json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["risk_class"] == expected_risk
    assert len(body["top_features"]) == 3
    assert body["message"]
    assert body["channel"]
    assert body["action"]


def test_event_aceita_payload(client):
    r = client.post(
        "/event",
        json={
            "patient_id": "BEN0000001",
            "action": "telemed",
            "channel": "call",
            "outcome": "executed",
        },
    )
    assert r.status_code == 200
    assert r.json()["received"] is True
