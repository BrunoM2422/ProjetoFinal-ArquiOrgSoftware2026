"""Testes do padrão State: classificação dos estados da partida."""

from app.domain.board import Tabuleiro
from app.domain.moves.lance import Lance
from app.domain.casa import Casa
from app.domain.partida import Partida
from app.domain.states import EmAndamento, Empate, Xeque, XequeMate


def _partida(fen: str) -> Partida:
    return Partida(Tabuleiro.de_fen(fen))


def _lance(texto: str, promocao: str | None = None) -> Lance:
    return Lance(Casa.de_algebrica(texto[:2]), Casa.de_algebrica(texto[2:4]), promocao)


def test_posicao_inicial_esta_em_andamento():
    partida = Partida()
    assert isinstance(partida.estado, EmAndamento)
    assert not partida.terminada
    assert partida.estado.resultado is None


def test_xeque_simples_e_reconhecido():
    # Dama preta em e7 dá xeque no rei branco em e1 (que ainda tem saída).
    partida = _partida("4k3/4q3/8/8/8/8/8/4K3 w - - 0 1")
    assert isinstance(partida.estado, Xeque)
    assert partida.estado.em_xeque
    assert not partida.terminada


def test_xeque_mate_do_corredor():
    # Mate da torre no corredor: torre preta em a1, rei branco preso em h1.
    partida = _partida("6k1/8/8/8/8/8/5PPP/r6K w - - 0 1")
    assert isinstance(partida.estado, XequeMate)
    assert partida.terminada
    assert partida.estado.resultado == "0-1"  # vitória das pretas


def test_afogamento_e_empate():
    # Afogamento clássico: vez das pretas, sem lances legais e sem xeque.
    partida = _partida("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
    assert isinstance(partida.estado, Empate)
    assert partida.estado.motivo == "afogamento"
    assert partida.estado.resultado == "1/2-1/2"


def test_material_insuficiente_rei_contra_rei():
    partida = _partida("4k3/8/8/8/8/8/8/4K3 w - - 0 1")
    assert isinstance(partida.estado, Empate)
    assert partida.estado.motivo == "material insuficiente"


def test_material_insuficiente_rei_e_cavalo():
    partida = _partida("4k3/8/8/8/8/8/8/3NK3 w - - 0 1")
    assert isinstance(partida.estado, Empate)
    assert partida.estado.motivo == "material insuficiente"


def test_material_suficiente_com_peao():
    # Um peão já basta para haver material; a partida segue em andamento.
    partida = _partida("4k3/8/8/8/8/8/4P3/4K3 w - - 0 1")
    assert isinstance(partida.estado, EmAndamento)


def test_regra_dos_50_lances():
    # Contador já em 100 meios-lances: a próxima classificação é empate.
    partida = _partida("4k3/8/8/8/3R4/8/8/4K3 w - - 100 1")
    assert isinstance(partida.estado, Empate)
    assert partida.estado.motivo == "regra dos 50 lances"


def test_tripla_repeticao():
    # Brancas e pretas balançam os cavalos de ida e volta até repetir 3x.
    partida = Partida()
    danca = ["g1f3", "g8f6", "f3g1", "f6g8"]  # volta à posição inicial
    for _ in range(2):
        for texto in danca:
            partida.aplicar_lance(_lance(texto))
    assert isinstance(partida.estado, Empate)
    assert partida.estado.motivo == "tripla repetição"
