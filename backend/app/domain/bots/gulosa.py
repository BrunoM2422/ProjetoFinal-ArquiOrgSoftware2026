"""Estratégia gulosa — o nível intermediário do bot.

Olha apenas um meio-lance à frente: simula cada lance legal numa cópia do
tabuleiro e escolhe o que deixa o melhor saldo de material imediato. Captura
peças sem defesa e evita dar material de graça, mas, por não olhar a
resposta do adversário, cai facilmente em iscas. Entre os lances de mesmo
valor, desempata por sorteio.
"""

from __future__ import annotations

import copy
import random
from typing import TYPE_CHECKING

from app.domain.bots.avaliacao import material
from app.domain.ports.estrategia_bot import EstrategiaDeBot

if TYPE_CHECKING:
    from app.domain.moves.lance import Lance
    from app.domain.partida import Partida


class EstrategiaGulosa(EstrategiaDeBot):
    nome = "guloso"

    def __init__(self, aleatorio: random.Random | None = None) -> None:
        self._aleatorio = aleatorio or random.Random()

    def escolher_lance(self, partida: "Partida") -> "Lance | None":
        legais = partida.lances_legais()
        if not legais:
            return None

        cor = partida.vez
        melhor_pontuacao: int | None = None
        melhores: list["Lance"] = []
        for lance in legais:
            tabuleiro = copy.deepcopy(partida.tabuleiro)
            tabuleiro.aplicar_lance(lance)
            pontuacao = material(tabuleiro, cor)
            if melhor_pontuacao is None or pontuacao > melhor_pontuacao:
                melhor_pontuacao = pontuacao
                melhores = [lance]
            elif pontuacao == melhor_pontuacao:
                melhores.append(lance)
        return self._aleatorio.choice(melhores)
