"""O lance — um value object que descreve um movimento no tabuleiro.

Um lance guarda apenas a *intenção* do movimento (de onde, para onde e, se
for o caso, em que peça o peão promove) mais alguns marcadores que dizem
que tipo de lance especial ele é. A execução propriamente dita — mover a
peça, capturar, atualizar direitos de roque — é responsabilidade do
tabuleiro, não deste objeto.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.casa import Casa


@dataclass(frozen=True)
class Lance:
    origem: Casa
    destino: Casa
    # Símbolo FEN da peça promovida (ex.: "Q" para dama), quando um peão
    # alcança a última fileira. ``None`` quando não há promoção.
    promocao: str | None = None
    # Marcadores de lances especiais, preenchidos pelo gerador de lances.
    eh_roque: bool = False
    eh_en_passant: bool = False

    def __str__(self) -> str:
        sufixo = f"={self.promocao}" if self.promocao else ""
        return f"{self.origem.algebrica}{self.destino.algebrica}{sufixo}"
