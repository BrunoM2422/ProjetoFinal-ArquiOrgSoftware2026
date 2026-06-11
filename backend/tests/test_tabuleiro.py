"""Testes de construção e consulta do Tabuleiro (FEN, xeque)."""

from app.domain.board import Tabuleiro
from app.domain.casa import Casa
from app.domain.cor import Cor
from app.domain.pieces import Rei, Torre


def test_posicao_inicial_tem_32_pecas():
    tabuleiro = Tabuleiro.inicial()
    assert len(tabuleiro.casas) == 32
    assert tabuleiro.vez is Cor.BRANCA
    assert tabuleiro.direitos_roque == {"K", "Q", "k", "q"}


def test_fen_posiciona_pecas_corretamente():
    tabuleiro = Tabuleiro.inicial()
    assert isinstance(tabuleiro.peca_em(Casa.de_algebrica("a1")), Torre)
    assert isinstance(tabuleiro.peca_em(Casa.de_algebrica("e1")), Rei)
    assert tabuleiro.peca_em(Casa.de_algebrica("a1")).cor is Cor.BRANCA
    assert tabuleiro.peca_em(Casa.de_algebrica("e8")).cor is Cor.PRETA
    assert tabuleiro.esta_vazia(Casa.de_algebrica("e4"))


def test_fen_le_vez_e_alvo_en_passant():
    tabuleiro = Tabuleiro.de_fen("4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1")
    assert tabuleiro.vez is Cor.BRANCA
    assert tabuleiro.alvo_en_passant == Casa.de_algebrica("d6")
    assert tabuleiro.direitos_roque == set()


def test_encontrar_rei():
    tabuleiro = Tabuleiro.inicial()
    assert tabuleiro.encontrar_rei(Cor.BRANCA) == Casa.de_algebrica("e1")
    assert tabuleiro.encontrar_rei(Cor.PRETA) == Casa.de_algebrica("e8")


def test_deteccao_de_xeque():
    # Dama preta em e7 ataca o rei branco em e1 pela coluna aberta.
    tabuleiro = Tabuleiro.de_fen("4k3/4q3/8/8/8/8/8/4K3 w - - 0 1")
    assert tabuleiro.esta_em_xeque(Cor.BRANCA)
    assert not tabuleiro.esta_em_xeque(Cor.PRETA)


def test_para_fen_eh_inverso_de_de_fen():
    # A serialização preserva posição, vez, direitos de roque, en passant e
    # o contador de 50 lances (o número do lance cheio é cosmético = 1).
    fens = [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1",
        "r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 7 1",
    ]
    for fen in fens:
        assert Tabuleiro.de_fen(fen).para_fen() == fen
