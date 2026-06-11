"""Gerador de lances pseudolegais.

Responsabilidade única (SRP): produzir todos os lances que respeitam o
*movimento* das peças do lado da vez. Ele delega a cada peça a geração dos
seus próprios lances e acrescenta o **roque**, que é o único lance que
nenhuma peça sozinha consegue decidir — depende de estado do tabuleiro
(direitos de roque, casas vazias e casas atacadas pelo adversário).

"Pseudolegal" porque ainda não se verificou se o lance deixa o próprio rei
em xeque; esse filtro é o papel do validador (``ValidadorDeLances``).
"""

from __future__ import annotations

from app.domain.board import Tabuleiro
from app.domain.casa import Casa
from app.domain.cor import Cor
from app.domain.moves.lance import Lance
from app.domain.pieces.rei import Rei


class GeradorDeLances:
    def gerar_pseudolegais(self, tabuleiro: Tabuleiro, cor: Cor) -> list[Lance]:
        lances: list[Lance] = []
        for casa, peca in tabuleiro.pecas_da_cor(cor):
            lances.extend(peca.gerar_lances_pseudolegais(tabuleiro, casa))
            if isinstance(peca, Rei):
                lances.extend(self._lances_de_roque(tabuleiro, casa, cor))
        return lances

    def _lances_de_roque(
        self, tabuleiro: Tabuleiro, casa_rei: Casa, cor: Cor
    ) -> list[Lance]:
        # O rei não pode rocar estando em xeque.
        if tabuleiro.esta_em_xeque(cor):
            return []

        linha = casa_rei.linha
        adversaria = cor.adversaria
        lances: list[Lance] = []

        direito_curto = "K" if cor is Cor.BRANCA else "k"
        direito_longo = "Q" if cor is Cor.BRANCA else "q"

        # Roque curto: casas f e g vazias; rei não passa por casa atacada.
        if direito_curto in tabuleiro.direitos_roque:
            entre = [Casa(5, linha), Casa(6, linha)]
            if all(tabuleiro.esta_vazia(c) for c in entre) and not any(
                tabuleiro.casa_atacada(c, adversaria) for c in entre
            ):
                lances.append(Lance(casa_rei, Casa(6, linha), eh_roque=True))

        # Roque longo: casas b, c e d vazias; rei não passa por c nem d atacadas.
        if direito_longo in tabuleiro.direitos_roque:
            vazias = [Casa(1, linha), Casa(2, linha), Casa(3, linha)]
            passagem = [Casa(2, linha), Casa(3, linha)]
            if all(tabuleiro.esta_vazia(c) for c in vazias) and not any(
                tabuleiro.casa_atacada(c, adversaria) for c in passagem
            ):
                lances.append(Lance(casa_rei, Casa(2, linha), eh_roque=True))

        return lances
