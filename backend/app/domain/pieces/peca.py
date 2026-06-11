"""A peça abstrata — a base da hierarquia que dá vida ao Factory Method.

Cada peça concreta (Rei, Dama, Torre, Bispo, Cavalo, Peão) encapsula as
suas próprias regras de movimento. O resto do domínio nunca pergunta "que
peça é essa?" para decidir como ela anda: pede à peça que gere os seus
lances. Isso mantém o código aberto à extensão e fechado à modificação
(OCP) e garante que qualquer subclasse seja substituível onde uma ``Peca``
é esperada (LSP).

Duas operações são deliberadamente separadas:

* ``gerar_lances_pseudolegais`` — para onde a peça *pode mover*;
* ``casas_atacadas`` — quais casas a peça *ameaça*.

Elas coincidem para quase todas as peças, mas divergem no peão (que avança
para frente sem atacar e ataca nas diagonais sem avançar), por isso a
distinção existe desde a base. "Pseudolegal" significa que o lance respeita
o movimento da peça, mas ainda pode ser ilegal por deixar o próprio rei em
xeque — esse filtro é responsabilidade do validador de lances.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Iterable

from app.domain.casa import Casa
from app.domain.cor import Cor

if TYPE_CHECKING:
    from app.domain.board import Tabuleiro
    from app.domain.moves.lance import Lance


class Peca(ABC):
    """Contrato comum a todas as peças do tabuleiro."""

    #: Letra FEN da peça em maiúsculo (ex.: "N" para o cavalo). Cada
    #: subclasse concreta define a sua.
    simbolo: str = ""
    #: Valor relativo de material, usado pelas estratégias de bot.
    valor: int = 0

    def __init__(self, cor: Cor) -> None:
        self.cor = cor

    # -- Movimento -------------------------------------------------------

    @abstractmethod
    def gerar_lances_pseudolegais(
        self, tabuleiro: "Tabuleiro", origem: Casa
    ) -> list["Lance"]:
        """Gera os lances pseudolegais da peça a partir de ``origem``."""

    def casas_atacadas(self, tabuleiro: "Tabuleiro", origem: Casa) -> set[Casa]:
        """Casas que esta peça ameaça (por padrão, os destinos dos lances).

        O peão sobrescreve este método, pois ataca de forma diferente de
        como se move.
        """
        return {lance.destino for lance in self.gerar_lances_pseudolegais(tabuleiro, origem)}

    # -- Apresentação ----------------------------------------------------

    @property
    def simbolo_fen(self) -> str:
        """Letra FEN: maiúscula para as brancas, minúscula para as pretas."""
        return self.simbolo if self.cor is Cor.BRANCA else self.simbolo.lower()

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.cor.value})"


def _lances_por_saltos(
    peca: Peca,
    tabuleiro: "Tabuleiro",
    origem: Casa,
    saltos: Iterable[tuple[int, int]],
) -> list["Lance"]:
    """Helper das peças de salto fixo (Cavalo, Rei).

    Diferente das peças que deslizam, estas alcançam apenas as casas
    imediatas indicadas pelos deslocamentos. Uma casa é destino válido se
    estiver vazia ou ocupada por uma peça adversária (captura).
    """
    from app.domain.moves.lance import Lance

    lances: list[Lance] = []
    for d_coluna, d_linha in saltos:
        coluna, linha = origem.coluna + d_coluna, origem.linha + d_linha
        if not Casa.existe(coluna, linha):
            continue
        destino = Casa(coluna, linha)
        ocupante = tabuleiro.peca_em(destino)
        if ocupante is None or ocupante.cor is not peca.cor:
            lances.append(Lance(origem, destino))
    return lances


def _lances_deslizando(
    peca: Peca,
    tabuleiro: "Tabuleiro",
    origem: Casa,
    direcoes: Iterable[tuple[int, int]],
) -> list["Lance"]:
    """Helper das peças de longo alcance (Torre, Bispo, Dama).

    Caminha em cada direção até bater numa peça ou na borda. Casa vazia
    vira lance de avanço; peça adversária vira lance de captura e encerra a
    direção; peça da mesma cor encerra sem incluir a casa.
    """
    from app.domain.moves.lance import Lance

    lances: list[Lance] = []
    for d_coluna, d_linha in direcoes:
        coluna, linha = origem.coluna + d_coluna, origem.linha + d_linha
        while Casa.existe(coluna, linha):
            destino = Casa(coluna, linha)
            ocupante = tabuleiro.peca_em(destino)
            if ocupante is None:
                lances.append(Lance(origem, destino))
            else:
                if ocupante.cor is not peca.cor:
                    lances.append(Lance(origem, destino))
                break
            coluna += d_coluna
            linha += d_linha
    return lances
