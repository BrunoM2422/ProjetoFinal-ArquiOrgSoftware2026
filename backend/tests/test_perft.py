"""Perft — contagem de nós da árvore de lances legais.

Perft (*performance test*) percorre a árvore de jogo até uma profundidade e
conta as posições-folha. Os valores da posição inicial são amplamente
tabelados e conhecidos (20, 400, 8902, ...). Bater exatamente com eles é a
prova mais forte de que a geração de lances legais está correta, incluindo
os casos especiais (roque, en passant, promoção), porque qualquer regra
errada desvia a contagem.
"""

import copy

import pytest

from app.domain.board import Tabuleiro
from app.domain.moves.validador import ValidadorDeLances

validador = ValidadorDeLances()


def perft(tabuleiro: Tabuleiro, profundidade: int) -> int:
    if profundidade == 0:
        return 1
    total = 0
    for lance in validador.gerar_legais(tabuleiro, tabuleiro.vez):
        proximo = copy.deepcopy(tabuleiro)
        proximo.aplicar_lance(lance)
        total += perft(proximo, profundidade - 1)
    return total


@pytest.mark.parametrize(
    "profundidade, esperado",
    [(1, 20), (2, 400), (3, 8902)],
)
def test_perft_posicao_inicial(profundidade, esperado):
    assert perft(Tabuleiro.inicial(), profundidade) == esperado
