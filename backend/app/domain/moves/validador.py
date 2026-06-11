"""Validador de lances — o guardião da legalidade.

Responsabilidade única (SRP): transformar lances *pseudolegais* em lances
*legais*. A regra que ele aplica é a única que falta após a geração: um
lance é ilegal se, depois de executado, deixar o próprio rei em xeque.

A verificação é feita por simulação: o lance é aplicado numa **cópia** do
tabuleiro (sem tocar na posição real) e pergunta-se se o rei ficou exposto.
Essa cópia isolada é o que sustenta o atributo de confiabilidade — nenhuma
simulação vaza para o jogo de verdade.
"""

from __future__ import annotations

import copy

from app.domain.board import Tabuleiro
from app.domain.cor import Cor
from app.domain.moves.gerador import GeradorDeLances
from app.domain.moves.lance import Lance


class ValidadorDeLances:
    def __init__(self, gerador: GeradorDeLances | None = None) -> None:
        self._gerador = gerador or GeradorDeLances()

    def gerar_legais(self, tabuleiro: Tabuleiro, cor: Cor) -> list[Lance]:
        """Devolve todos os lances legais da cor no tabuleiro."""
        pseudolegais = self._gerador.gerar_pseudolegais(tabuleiro, cor)
        return [lance for lance in pseudolegais if self._mantem_rei_seguro(tabuleiro, lance, cor)]

    def _mantem_rei_seguro(self, tabuleiro: Tabuleiro, lance: Lance, cor: Cor) -> bool:
        simulacao = copy.deepcopy(tabuleiro)
        simulacao.aplicar_lance(lance)
        return not simulacao.esta_em_xeque(cor)
