"""Testes do adaptador REST (FastAPI) ponta a ponta via TestClient."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _criar(nivel: str = "aleatorio", cor: str = "branca") -> dict:
    resposta = client.post(
        "/v1/games", json={"nivel_bot": nivel, "cor_humano": cor}
    )
    assert resposta.status_code == 201
    return resposta.json()


def test_criar_partida_devolve_estado_inicial():
    corpo = _criar()
    assert corpo["vez"] == "branca"
    assert corpo["cor_bot"] == "preta"
    assert corpo["cor_humano"] == "branca"
    assert corpo["historico"] == []
    assert corpo["fen"].startswith("rnbqkbnr/pppppppp")
    assert len(corpo["lances_legais"]) == 20  # 20 lances legais na posição inicial


def test_criar_partida_com_nivel_invalido_da_400():
    resposta = client.post(
        "/v1/games", json={"nivel_bot": "grandmaster", "cor_humano": "branca"}
    )
    assert resposta.status_code == 400
    assert "erro" in resposta.json()


def test_obter_partida_inexistente_da_404():
    resposta = client.get("/v1/games/nao-existe")
    assert resposta.status_code == 404


def test_obter_partida_existente():
    corpo = _criar()
    resposta = client.get(f"/v1/games/{corpo['id']}")
    assert resposta.status_code == 200
    assert resposta.json()["id"] == corpo["id"]


def test_aplicar_lance_dispara_resposta_do_bot():
    corpo = _criar()
    resposta = client.post(
        f"/v1/games/{corpo['id']}/moves",
        json={"origem": "e2", "destino": "e4"},
    )
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["lance_humano"]["notacao"] == "e2e4"
    assert dados["lance_bot"] is not None
    assert len(dados["partida"]["historico"]) == 2
    assert dados["partida"]["vez"] == "branca"


def test_lance_ilegal_da_400():
    corpo = _criar()
    resposta = client.post(
        f"/v1/games/{corpo['id']}/moves",
        json={"origem": "e2", "destino": "e5"},
    )
    assert resposta.status_code == 400


def test_lance_fora_de_vez_da_409():
    corpo = _criar()  # humano de brancas; tentar mover peça preta
    resposta = client.post(
        f"/v1/games/{corpo['id']}/moves",
        json={"origem": "e7", "destino": "e5"},
    )
    assert resposta.status_code == 409


def test_undo_e_redo():
    corpo = _criar()
    id_partida = corpo["id"]
    client.post(f"/v1/games/{id_partida}/moves", json={"origem": "e2", "destino": "e4"})

    desfeito = client.post(f"/v1/games/{id_partida}/undo")
    assert desfeito.status_code == 200
    assert desfeito.json()["historico"] == []

    refeito = client.post(f"/v1/games/{id_partida}/redo")
    assert refeito.status_code == 200
    assert len(refeito.json()["historico"]) == 2


def test_listar_lances():
    corpo = _criar()
    id_partida = corpo["id"]
    client.post(f"/v1/games/{id_partida}/moves", json={"origem": "d2", "destino": "d4"})
    resposta = client.get(f"/v1/games/{id_partida}/moves")
    assert resposta.status_code == 200
    lances = resposta.json()
    assert lances[0] == "d2d4"
    assert len(lances) == 2


def test_analise_nao_afeta_a_partida_real():
    corpo = _criar()
    id_partida = corpo["id"]

    resposta = client.post(
        f"/v1/games/{id_partida}/analysis",
        json={"lances": [{"origem": "e2", "destino": "e4"}]},
    )
    assert resposta.status_code == 200
    analise = resposta.json()
    assert len(analise["historico"]) == 1
    assert analise["lance_sugerido"] is not None

    # A partida real permanece intocada.
    atual = client.get(f"/v1/games/{id_partida}").json()
    assert atual["historico"] == []
