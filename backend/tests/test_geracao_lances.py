"""Testes da geração de lances pseudolegais por tipo de peça."""

from app.domain.board import Tabuleiro
from app.domain.casa import Casa


def _destinos(tabuleiro: Tabuleiro, origem: str) -> set[str]:
    casa = Casa.de_algebrica(origem)
    peca = tabuleiro.peca_em(casa)
    return {lance.destino.algebrica for lance in peca.gerar_lances_pseudolegais(tabuleiro, casa)}


def test_cavalo_no_centro_tem_oito_destinos():
    tabuleiro = Tabuleiro.de_fen("4k3/8/8/8/3N4/8/8/4K3 w - - 0 1")
    assert _destinos(tabuleiro, "d4") == {"b3", "b5", "c2", "c6", "e2", "e6", "f3", "f5"}


def test_cavalo_no_canto_tem_dois_destinos():
    tabuleiro = Tabuleiro.de_fen("4k3/8/8/8/8/8/8/N3K3 w - - 0 1")
    assert _destinos(tabuleiro, "a1") == {"b3", "c2"}


def test_torre_para_ao_capturar_e_nao_atravessa():
    # Torre branca em a1; peça preta em a4 (captura) e branca em c1 (bloqueia).
    tabuleiro = Tabuleiro.de_fen("4k3/8/8/8/p7/8/8/R1B1K3 w - - 0 1")
    destinos = _destinos(tabuleiro, "a1")
    assert "a4" in destinos  # captura a peça preta
    assert "a5" not in destinos  # não atravessa a peça capturada
    assert "b1" in destinos
    assert "c1" not in destinos  # bloqueada pela própria peça


def test_peao_branco_avanco_simples_e_duplo():
    tabuleiro = Tabuleiro.inicial()
    assert _destinos(tabuleiro, "e2") == {"e3", "e4"}


def test_peao_so_avanca_simples_fora_da_fileira_inicial():
    tabuleiro = Tabuleiro.de_fen("4k3/8/8/8/8/4P3/8/4K3 w - - 0 1")
    assert _destinos(tabuleiro, "e3") == {"e4"}


def test_peao_captura_na_diagonal():
    tabuleiro = Tabuleiro.de_fen("4k3/8/8/8/8/3p1p2/4P3/4K3 w - - 0 1")
    assert _destinos(tabuleiro, "e2") == {"e3", "e4", "d3", "f3"}


def test_peao_promove_em_quatro_pecas():
    tabuleiro = Tabuleiro.de_fen("4k3/P7/8/8/8/8/8/4K3 w - - 0 1")
    casa = Casa.de_algebrica("a7")
    peca = tabuleiro.peca_em(casa)
    promocoes = {
        lance.promocao
        for lance in peca.gerar_lances_pseudolegais(tabuleiro, casa)
        if lance.promocao
    }
    assert promocoes == {"Q", "R", "B", "N"}
