"""O Bispo — desliza nas quatro diagonais."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.casa import Casa
from app.domain.pieces.peca import Peca, _lances_deslizando

if TYPE_CHECKING:
    from app.domain.board import Tabuleiro
    from app.domain.moves.lance import Lance

_DIRECOES = [(1, 1), (1, -1), (-1, 1), (-1, -1)]


class Bispo(Peca):
    simbolo = "B"  # Bishop, na notação FEN internacional
    valor = 3

    def gerar_lances_pseudolegais(
        self, tabuleiro: "Tabuleiro", origem: Casa
    ) -> list["Lance"]:
        return _lances_deslizando(self, tabuleiro, origem, _DIRECOES)
