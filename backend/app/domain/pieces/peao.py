"""O Peão — a peça com mais regras especiais do tabuleiro.

Reúne quatro comportamentos distintos:

* **avanço simples** de uma casa, se a frente estiver livre;
* **avanço duplo** a partir da fileira inicial, se as duas casas à frente
  estiverem livres;
* **captura na diagonal**, incluindo o **en passant** quando o adversário
  acabou de fazer um avanço duplo (a casa-alvo fica registrada no
  tabuleiro);
* **promoção** ao alcançar a última fileira, gerando um lance por peça em
  que o peão pode promover.

Além disso, o peão é a única peça que *ataca* de forma diferente de como
*anda*: avança em linha reta sem ameaçar, e ameaça nas diagonais sem
avançar. Por isso ``casas_atacadas`` é sobrescrito.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.casa import Casa
from app.domain.pieces.peca import Peca

if TYPE_CHECKING:
    from app.domain.board import Tabuleiro
    from app.domain.moves.lance import Lance

# Peças em que um peão pode promover (símbolos FEN).
_PROMOCOES = ("Q", "R", "B", "N")


class Peao(Peca):
    simbolo = "P"  # Pawn, na notação FEN internacional
    valor = 1

    def gerar_lances_pseudolegais(
        self, tabuleiro: "Tabuleiro", origem: Casa
    ) -> list["Lance"]:
        sentido = self.cor.sentido_avanco
        lances: list[Lance] = []

        self._gerar_avancos(tabuleiro, origem, sentido, lances)
        self._gerar_capturas(tabuleiro, origem, sentido, lances)
        return lances

    def casas_atacadas(self, tabuleiro: "Tabuleiro", origem: Casa) -> set[Casa]:
        sentido = self.cor.sentido_avanco
        atacadas: set[Casa] = set()
        for d_coluna in (-1, 1):
            coluna, linha = origem.coluna + d_coluna, origem.linha + sentido
            if Casa.existe(coluna, linha):
                atacadas.add(Casa(coluna, linha))
        return atacadas

    # -- Bastidores ------------------------------------------------------

    def _gerar_avancos(
        self, tabuleiro: "Tabuleiro", origem: Casa, sentido: int, lances: list["Lance"]
    ) -> None:
        uma_frente = Casa.existe(origem.coluna, origem.linha + sentido)
        if not uma_frente:
            return
        frente = Casa(origem.coluna, origem.linha + sentido)
        if tabuleiro.peca_em(frente) is not None:
            return  # caminho bloqueado: peão não captura para frente

        self._adicionar_avanco_ou_promocao(origem, frente, lances)

        # Avanço duplo só a partir da fileira inicial e com as duas casas livres.
        if origem.linha == self._fileira_inicial():
            duas_frente = Casa(origem.coluna, origem.linha + 2 * sentido)
            if tabuleiro.peca_em(duas_frente) is None:
                from app.domain.moves.lance import Lance

                lances.append(Lance(origem, duas_frente))

    def _gerar_capturas(
        self, tabuleiro: "Tabuleiro", origem: Casa, sentido: int, lances: list["Lance"]
    ) -> None:
        from app.domain.moves.lance import Lance

        for d_coluna in (-1, 1):
            if not Casa.existe(origem.coluna + d_coluna, origem.linha + sentido):
                continue
            destino = Casa(origem.coluna + d_coluna, origem.linha + sentido)
            ocupante = tabuleiro.peca_em(destino)
            if ocupante is not None and ocupante.cor is not self.cor:
                self._adicionar_avanco_ou_promocao(origem, destino, lances)
            elif destino == tabuleiro.alvo_en_passant:
                # En passant: a casa-alvo está vazia, mas captura o peão ao lado.
                lances.append(Lance(origem, destino, eh_en_passant=True))

    def _adicionar_avanco_ou_promocao(
        self, origem: Casa, destino: Casa, lances: list["Lance"]
    ) -> None:
        from app.domain.moves.lance import Lance

        if destino.linha == self._fileira_promocao():
            for peca_promovida in _PROMOCOES:
                lances.append(Lance(origem, destino, promocao=peca_promovida))
        else:
            lances.append(Lance(origem, destino))

    def _fileira_inicial(self) -> int:
        from app.domain.cor import Cor

        return 1 if self.cor is Cor.BRANCA else 6

    def _fileira_promocao(self) -> int:
        from app.domain.cor import Cor

        return 7 if self.cor is Cor.BRANCA else 0
