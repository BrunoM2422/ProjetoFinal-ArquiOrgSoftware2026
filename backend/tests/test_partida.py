"""Testes do agregado Partida: aplicação de lances e invariantes."""

import pytest

from app.domain.board import Tabuleiro
from app.domain.casa import Casa
from app.domain.erros import LanceIlegalError, PartidaEncerradaError
from app.domain.moves.lance import Lance
from app.domain.partida import Partida


def _lance(texto: str, promocao: str | None = None) -> Lance:
    return Lance(Casa.de_algebrica(texto[:2]), Casa.de_algebrica(texto[2:4]), promocao)


def test_aplicar_lance_legal_avanca_a_partida():
    partida = Partida()
    aplicado = partida.aplicar_lance(_lance("e2e4"))
    assert str(aplicado) == "e2e4"
    assert partida.vez.value == "preta"
    assert len(partida.historico) == 1


def test_lance_ilegal_e_recusado():
    partida = Partida()
    with pytest.raises(LanceIlegalError):
        partida.aplicar_lance(_lance("e2e5"))  # peão não anda três casas


def test_lance_casa_com_flags_corretas():
    # O pedido vem "cru"; a partida casa com o lance legal e marca o roque.
    partida = Partida(Tabuleiro.de_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"))
    aplicado = partida.aplicar_lance(_lance("e1g1"))
    assert aplicado.eh_roque is True


def test_promocao_exige_peca_indicada():
    partida = Partida(Tabuleiro.de_fen("4k3/P7/8/8/8/8/8/4K3 w - - 0 1"))
    aplicado = partida.aplicar_lance(_lance("a7a8", promocao="Q"))
    assert aplicado.promocao == "Q"
    assert partida.tabuleiro.peca_em(Casa.de_algebrica("a8")).simbolo_fen == "Q"


def test_nao_se_joga_em_partida_encerrada():
    # Posição de xeque-mate: nenhum lance é aceito.
    partida = Partida(Tabuleiro.de_fen("6k1/8/8/8/8/8/5PPP/r6K w - - 0 1"))
    with pytest.raises(PartidaEncerradaError):
        partida.aplicar_lance(_lance("h1g1"))


def test_historico_preserva_a_ordem():
    partida = Partida()
    for texto in ("e2e4", "e7e5", "g1f3"):
        partida.aplicar_lance(_lance(texto))
    assert [str(l) for l in partida.historico] == ["e2e4", "e7e5", "g1f3"]
