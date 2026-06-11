"""Estratégia minimax raso — o nível mais forte do bot.

Olha alguns meios-lances à frente assumindo jogo ótimo dos dois lados: o bot
maximiza o próprio material e supõe que o adversário tenta minimizá-lo. A
profundidade é fixa e pequena (padrão 2) — o objetivo é demonstrar o padrão
Strategy com um nível visivelmente melhor, não construir um motor forte.

A **poda alfa-beta** corta ramos que comprovadamente não influenciam a
escolha, reduzindo o número de posições visitadas e mantendo a resposta bem
dentro da meta de performance (< 500 ms), mesmo clonando o tabuleiro a cada
nó.
"""

from __future__ import annotations

import copy
import random
from typing import TYPE_CHECKING

from app.domain.bots.avaliacao import material
from app.domain.board import Tabuleiro
from app.domain.cor import Cor
from app.domain.moves.validador import ValidadorDeLances
from app.domain.ports.estrategia_bot import EstrategiaDeBot

if TYPE_CHECKING:
    from app.domain.moves.lance import Lance
    from app.domain.partida import Partida

# Valor que representa o mate; bem maior que qualquer saldo de material real.
_INFINITO = 10**6


class EstrategiaMinimax(EstrategiaDeBot):
    nome = "minimax"

    def __init__(
        self,
        profundidade: int = 2,
        aleatorio: random.Random | None = None,
    ) -> None:
        self._profundidade = profundidade
        self._aleatorio = aleatorio or random.Random()
        self._validador = ValidadorDeLances()

    def escolher_lance(self, partida: "Partida") -> "Lance | None":
        legais = partida.lances_legais()
        if not legais:
            return None

        cor_bot = partida.vez
        melhor_valor = -_INFINITO
        melhores: list["Lance"] = []
        alfa, beta = -_INFINITO, _INFINITO
        for lance in legais:
            tabuleiro = copy.deepcopy(partida.tabuleiro)
            tabuleiro.aplicar_lance(lance)
            valor = self._avaliar(tabuleiro, self._profundidade - 1, alfa, beta, cor_bot)
            if valor > melhor_valor:
                melhor_valor = valor
                melhores = [lance]
            elif valor == melhor_valor:
                melhores.append(lance)
            alfa = max(alfa, melhor_valor)
        return self._aleatorio.choice(melhores)

    def _avaliar(
        self, tabuleiro: Tabuleiro, profundidade: int, alfa: int, beta: int, cor_bot: Cor
    ) -> int:
        legais = self._validador.gerar_legais(tabuleiro, tabuleiro.vez)

        if not legais:
            return self._pontuar_fim_de_jogo(tabuleiro, profundidade, cor_bot)
        if profundidade == 0:
            return material(tabuleiro, cor_bot)

        # O bot maximiza nas suas jogadas; o adversário minimiza nas dele.
        if tabuleiro.vez is cor_bot:
            return self._maximizar(tabuleiro, legais, profundidade, alfa, beta, cor_bot)
        return self._minimizar(tabuleiro, legais, profundidade, alfa, beta, cor_bot)

    def _maximizar(self, tabuleiro, legais, profundidade, alfa, beta, cor_bot) -> int:
        valor = -_INFINITO
        for lance in legais:
            filho = copy.deepcopy(tabuleiro)
            filho.aplicar_lance(lance)
            valor = max(valor, self._avaliar(filho, profundidade - 1, alfa, beta, cor_bot))
            alfa = max(alfa, valor)
            if beta <= alfa:
                break  # poda: o minimizador nunca deixaria chegar aqui
        return valor

    def _minimizar(self, tabuleiro, legais, profundidade, alfa, beta, cor_bot) -> int:
        valor = _INFINITO
        for lance in legais:
            filho = copy.deepcopy(tabuleiro)
            filho.aplicar_lance(lance)
            valor = min(valor, self._avaliar(filho, profundidade - 1, alfa, beta, cor_bot))
            beta = min(beta, valor)
            if beta <= alfa:
                break  # poda: o maximizador nunca deixaria chegar aqui
        return valor

    def _pontuar_fim_de_jogo(self, tabuleiro: Tabuleiro, profundidade: int, cor_bot: Cor) -> int:
        # Sem lances legais: xeque-mate (em xeque) ou afogamento (empate).
        if not tabuleiro.esta_em_xeque(tabuleiro.vez):
            return 0  # afogamento
        # Quem está em xeque e sem saída levou mate. O '+ profundidade' faz o
        # bot preferir mates mais rápidos (e adiar os que sofre).
        if tabuleiro.vez is cor_bot:
            return -_INFINITO - profundidade
        return _INFINITO + profundidade
