"""Testes de undo/redo (Command + Memento)."""

from app.domain.board import Tabuleiro
from app.domain.casa import Casa
from app.domain.moves.lance import Lance
from app.domain.partida import Partida


def _lance(texto: str, promocao: str | None = None) -> Lance:
    return Lance(Casa.de_algebrica(texto[:2]), Casa.de_algebrica(texto[2:4]), promocao)


def test_desfazer_restaura_a_posicao_anterior():
    partida = Partida()
    partida.aplicar_lance(_lance("e2e4"))
    assert partida.tabuleiro.esta_vazia(Casa.de_algebrica("e2"))

    assert partida.desfazer() is True
    assert partida.tabuleiro.peca_em(Casa.de_algebrica("e2")) is not None
    assert partida.tabuleiro.esta_vazia(Casa.de_algebrica("e4"))
    assert partida.vez.value == "branca"
    assert partida.historico == []


def test_refazer_reaplica_o_lance():
    partida = Partida()
    partida.aplicar_lance(_lance("e2e4"))
    partida.desfazer()

    assert partida.refazer() is True
    assert partida.tabuleiro.esta_vazia(Casa.de_algebrica("e2"))
    assert [str(l) for l in partida.historico] == ["e2e4"]


def test_desfazer_e_refazer_sem_historico_retornam_falso():
    partida = Partida()
    assert partida.desfazer() is False
    assert partida.refazer() is False


def test_lance_novo_descarta_a_linha_de_redo():
    partida = Partida()
    partida.aplicar_lance(_lance("e2e4"))
    partida.desfazer()
    partida.aplicar_lance(_lance("d2d4"))  # outro caminho

    assert partida.refazer() is False  # o redo de e2e4 foi abandonado
    assert [str(l) for l in partida.historico] == ["d2d4"]


def test_undo_de_roque_restaura_rei_e_torre():
    # O Memento devolve rei e torre ao lugar sem o comando saber reverter roque.
    partida = Partida(Tabuleiro.de_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"))
    partida.aplicar_lance(_lance("e1g1"))
    partida.desfazer()
    assert partida.tabuleiro.peca_em(Casa.de_algebrica("e1")) is not None
    assert partida.tabuleiro.peca_em(Casa.de_algebrica("h1")) is not None
    assert partida.tabuleiro.esta_vazia(Casa.de_algebrica("f1"))
    assert partida.tabuleiro.direitos_roque == {"K", "Q", "k", "q"}


def test_undo_de_promocao_devolve_o_peao():
    partida = Partida(Tabuleiro.de_fen("4k3/P7/8/8/8/8/8/4K3 w - - 0 1"))
    partida.aplicar_lance(_lance("a7a8", promocao="Q"))
    partida.desfazer()
    peca = partida.tabuleiro.peca_em(Casa.de_algebrica("a7"))
    assert peca is not None and peca.simbolo_fen == "P"
    assert partida.tabuleiro.esta_vazia(Casa.de_algebrica("a8"))


def test_undo_de_en_passant_devolve_o_peao_capturado():
    partida = Partida(Tabuleiro.de_fen("4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1"))
    partida.aplicar_lance(_lance("e5d6"))
    partida.desfazer()
    peca_d5 = partida.tabuleiro.peca_em(Casa.de_algebrica("d5"))
    assert peca_d5 is not None and peca_d5.simbolo_fen == "p"  # peão preto de volta
    assert partida.tabuleiro.alvo_en_passant == Casa.de_algebrica("d6")
