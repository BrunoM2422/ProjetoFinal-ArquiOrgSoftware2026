"""Cor das peças e do lado que joga."""

from __future__ import annotations

from enum import Enum


class Cor(Enum):
    """As duas cores do xadrez.

    Além de identificar o dono de uma peça, a cor carrega o *sentido de
    avanço* dos peões: as brancas sobem o tabuleiro (linha +1) e as pretas
    descem (linha -1).
    """

    BRANCA = "branca"
    PRETA = "preta"

    @property
    def adversaria(self) -> "Cor":
        """Devolve a cor oposta — útil para saber de quem é a vez seguinte."""
        return Cor.PRETA if self is Cor.BRANCA else Cor.BRANCA

    @property
    def sentido_avanco(self) -> int:
        """Direção em que os peões desta cor avançam (+1 brancas, -1 pretas)."""
        return 1 if self is Cor.BRANCA else -1
