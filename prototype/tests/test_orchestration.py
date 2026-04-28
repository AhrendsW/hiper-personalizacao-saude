from orchestration.decisions import decide


def test_jovem_verde_e_rotina_sem_humano():
    a = decide("jovem", "verde")
    assert a.action == "conteudo_preventivo"
    assert a.priority == "rotina"
    assert a.requires_human is False


def test_cronico_vermelho_dispara_telemed_imediata():
    a = decide("cronico", "vermelho")
    assert a.priority == "imediato"
    assert a.requires_human is True
    assert "telemed" in a.channel


def test_idoso_sempre_tem_humano_no_loop():
    for risk in ["verde", "amarelo", "vermelho"]:
        a = decide("idoso", risk)
        assert a.requires_human is True, f"idoso {risk} deveria ter humano no loop"


def test_perfil_desconhecido_cai_em_demais():
    a = decide("desconhecido", "vermelho")
    assert a.action == decide("demais", "vermelho").action
