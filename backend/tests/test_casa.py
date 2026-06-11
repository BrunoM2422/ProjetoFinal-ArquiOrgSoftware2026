"""Testes do value object Casa."""

import pytest

from app.domain.casa import Casa


def test_conversao_de_algebrica_para_indices():
    casa = Casa.de_algebrica("e4")
    assert (casa.coluna, casa.linha) == (4, 3)


def test_conversao_de_indices_para_algebrica():
    assert Casa(0, 0).algebrica == "a1"
    assert Casa(7, 7).algebrica == "h8"
    assert Casa(4, 3).algebrica == "e4"


def test_ida_e_volta_da_notacao():
    for texto in ("a1", "h8", "d5", "f2"):
        assert Casa.de_algebrica(texto).algebrica == texto


def test_casa_fora_do_tabuleiro_e_recusada():
    with pytest.raises(ValueError):
        Casa(8, 0)
    with pytest.raises(ValueError):
        Casa(0, -1)


def test_notacao_invalida_e_recusada():
    with pytest.raises(ValueError):
        Casa.de_algebrica("z9")


def test_existe_testa_indices_sem_construir():
    assert Casa.existe(0, 0)
    assert not Casa.existe(8, 0)
    assert not Casa.existe(-1, 3)
