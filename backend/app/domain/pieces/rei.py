"""O Rei — move uma casa em qualquer direção.

O roque, por depender de estado que a peça não conhece (direitos de roque,
casas atacadas pelo adversário), é gerado em nível mais alto pelo gerador
de lances, e não aqui.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.casa import Casa
from app.domain.pieces.peca import Peca, _lances_por_saltos

if TYPE_CHECKING:
    from app.domain.board import Tabuleiro
    from app.domain.moves.lance import Lance

_PASSOS = [
    (1, 0), (-1, 0), (0, 1), (0, -1),
    (1, 1), (1, -1), (-1, 1), (-1, -1),
]


class Rei(Peca):
    simbolo = "K"  # King, na notação FEN internacional
    # O rei nunca é capturado em jogo legal; manter o valor em 0 evita
    # poluir a contagem de material das estratégias de bot.
    valor = 0

    def gerar_lances_pseudolegais(
        self, tabuleiro: "Tabuleiro", origem: Casa
    ) -> list["Lance"]:
        return _lances_por_saltos(self, tabuleiro, origem, _PASSOS)
