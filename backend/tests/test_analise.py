"""Testes da análise "e se?" via clonagem (Prototype)."""

from app.domain.casa import Casa
from app.domain.moves.lance import Lance
from app.domain.partida import Partida


def _lance(texto: str) -> Lance:
    return Lance(Casa.de_algebrica(texto[:2]), Casa.de_algebrica(texto[2:4]))


def test_clone_e_independente_do_original():
    original = Partida()
    clone = original.clonar()

    clone.aplicar_lance(_lance("e2e4"))

    # O lance hipotético afeta só o clone; o jogo real fica intacto.
    assert clone.tabuleiro.esta_vazia(Casa.de_algebrica("e2"))
    assert original.tabuleiro.peca_em(Casa.de_algebrica("e2")) is not None
    assert original.historico == []
    assert clone.vez.value == "preta"
    assert original.vez.value == "branca"


def test_clone_preserva_o_historico_ja_jogado():
    original = Partida()
    original.aplicar_lance(_lance("e2e4"))
    clone = original.clonar()

    assert [str(l) for l in clone.historico] == ["e2e4"]
    # Desfazer no clone não mexe no original.
    clone.desfazer()
    assert clone.historico == []
    assert [str(l) for l in original.historico] == ["e2e4"]


def test_varias_simulacoes_nao_interferem_entre_si():
    original = Partida()
    linha_a = original.clonar()
    linha_b = original.clonar()

    linha_a.aplicar_lance(_lance("e2e4"))
    linha_b.aplicar_lance(_lance("d2d4"))

    assert linha_a.tabuleiro.esta_vazia(Casa.de_algebrica("e2"))
    assert linha_a.tabuleiro.peca_em(Casa.de_algebrica("d2")) is not None
    assert linha_b.tabuleiro.esta_vazia(Casa.de_algebrica("d2"))
    assert linha_b.tabuleiro.peca_em(Casa.de_algebrica("e2")) is not None
