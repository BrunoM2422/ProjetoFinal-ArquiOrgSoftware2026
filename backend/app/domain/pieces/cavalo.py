"""O Cavalo — salta em "L", único a pular sobre outras peças."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.casa import Casa
from app.domain.pieces.peca import Peca, _lances_por_saltos

if TYPE_CHECKING:
    from app.domain.board import Tabuleiro
    from app.domain.moves.lance import Lance

_SALTOS = [
    (1, 2), (2, 1), (2, -1), (1, -2),
    (-1, -2), (-2, -1), (-2, 1), (-1, 2),
]


class Cavalo(Peca):
    simbolo = "N"  # kNight, na notação FEN internacional (K já é do Rei)
    valor = 3

    def gerar_lances_pseudolegais(
        self, tabuleiro: "Tabuleiro", origem: Casa
    ) -> list["Lance"]:
        return _lances_por_saltos(self, tabuleiro, origem, _SALTOS)
