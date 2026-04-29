import pytest

from genai.client import generate_message


@pytest.fixture(autouse=True)
def _no_api_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)


def _features():
    return [
        {"name": "sbp_avg", "value": 148.0, "contribution": 1.0},
        {"name": "dbp_avg", "value": 92.0, "contribution": 0.8},
    ]


def test_fallback_quando_sem_api_key():
    msg = generate_message("cronico", "vermelho", _features(), persona_name="Maria")
    assert msg.source == "fallback"
    assert msg.model is None
    assert "pressão" in msg.text.lower()


def test_mensagem_de_idoso_e_acolhedora():
    msg = generate_message("idoso", "vermelho", _features(), persona_name="João")
    assert "apoiar" in msg.text.lower() or "estamos aqui" in msg.text.lower()


def test_mensagem_de_jovem_e_concisa_sem_alarme():
    msg = generate_message("jovem", "verde", _features())
    assert len(msg.text) < 220
    assert "emergência" not in msg.text.lower()


def test_risco_invalido_levanta():
    with pytest.raises(ValueError):
        generate_message("jovem", "preto", _features())
