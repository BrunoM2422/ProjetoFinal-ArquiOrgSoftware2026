"""Testes do Factory Method de peças."""

import pytest

from app.domain.cor import Cor
from app.domain.pieces import Bispo, Cavalo, Dama, Peao, Rei, Torre, criar_peca


def test_maiuscula_cria_peca_branca():
    peca = criar_peca("N")
    assert isinstance(peca, Cavalo)
    assert peca.cor is Cor.BRANCA


def test_minuscula_cria_peca_preta():
    peca = criar_peca("q")
    assert isinstance(peca, Dama)
    assert peca.cor is Cor.PRETA


def test_cada_simbolo_mapeia_para_sua_classe():
    esperado = {
        "K": Rei,
        "Q": Dama,
        "R": Torre,
        "B": Bispo,
        "N": Cavalo,
        "P": Peao,
    }
    for simbolo, classe in esperado.items():
        assert isinstance(criar_peca(simbolo), classe)


def test_simbolo_desconhecido_levanta_erro():
    with pytest.raises(ValueError):
        criar_peca("X")


def test_simbolo_fen_respeita_a_cor():
    assert criar_peca("N").simbolo_fen == "N"
    assert criar_peca("n").simbolo_fen == "n"
