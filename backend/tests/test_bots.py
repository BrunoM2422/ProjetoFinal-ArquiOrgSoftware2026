"""Testes das estratégias de bot (padrão Strategy)."""

import random
import time

import pytest

from app.domain.board import Tabuleiro
from app.domain.bots import (
    EstrategiaAleatoria,
    EstrategiaGulosa,
    EstrategiaMinimax,
    criar_estrategia,
)
from app.domain.partida import Partida


def _partida(fen: str) -> Partida:
    return Partida(Tabuleiro.de_fen(fen))


def test_aleatoria_escolhe_um_lance_legal():
    partida = Partida()
    estrategia = EstrategiaAleatoria(random.Random(0))
    escolha = estrategia.escolher_lance(partida)
    assert escolha in partida.lances_legais()


def test_estrategia_devolve_none_em_partida_terminada():
    # Xeque-mate: não há lance a escolher.
    partida = _partida("6k1/8/8/8/8/8/5PPP/r6K w - - 0 1")
    for estrategia in (
        EstrategiaAleatoria(random.Random(0)),
        EstrategiaGulosa(random.Random(0)),
        EstrategiaMinimax(aleatorio=random.Random(0)),
    ):
        assert estrategia.escolher_lance(partida) is None


def test_gulosa_captura_material_livre():
    # Torre branca em a1 pode capturar a dama preta indefesa em a8.
    partida = _partida("q6k/8/8/8/8/8/8/R3K3 w - - 0 1")
    estrategia = EstrategiaGulosa(random.Random(0))
    assert str(estrategia.escolher_lance(partida)) == "a1a8"


def test_minimax_encontra_mate_em_um():
    # Torre em h1 dá mate em h8 (rei preto preso em a8, rei branco em b6).
    partida = _partida("k7/8/1K6/8/8/8/8/7R w - - 0 1")
    estrategia = EstrategiaMinimax(profundidade=2, aleatorio=random.Random(0))
    assert str(estrategia.escolher_lance(partida)) == "h1h8"


def test_minimax_nao_morde_isca_que_a_gulosa_morderia():
    # A dama em d1 pode capturar o peão em d5, mas ele é defendido pelo peão c6:
    # após Dxd5, vem cxd5 e a dama cai. A gulosa (1 meio-lance) pega o peão; o
    # minimax (vê a resposta) recusa a isca.
    partida = _partida("4k3/8/2p5/3p4/8/8/8/3QK3 w - - 0 1")
    gulosa = EstrategiaGulosa(random.Random(0)).escolher_lance(partida)
    minimax = EstrategiaMinimax(profundidade=2, aleatorio=random.Random(0)).escolher_lance(partida)
    assert str(gulosa) == "d1d5"  # a gulosa morde a isca
    assert str(minimax) != "d1d5"  # o minimax não


def test_fabrica_cria_cada_nivel():
    assert isinstance(criar_estrategia("aleatorio"), EstrategiaAleatoria)
    assert isinstance(criar_estrategia("guloso"), EstrategiaGulosa)
    assert isinstance(criar_estrategia("minimax"), EstrategiaMinimax)


def test_fabrica_recusa_nivel_desconhecido():
    with pytest.raises(ValueError):
        criar_estrategia("grandmaster")


def test_minimax_responde_dentro_da_meta_de_performance():
    # A partir da posição inicial (35+ lances), o minimax raso deve responder
    # bem abaixo da meta de 500 ms estabelecida para o atributo de performance.
    partida = Partida()
    estrategia = EstrategiaMinimax(profundidade=2, aleatorio=random.Random(0))
    inicio = time.perf_counter()
    escolha = estrategia.escolher_lance(partida)
    decorrido = time.perf_counter() - inicio
    assert escolha is not None
    assert decorrido < 0.5
