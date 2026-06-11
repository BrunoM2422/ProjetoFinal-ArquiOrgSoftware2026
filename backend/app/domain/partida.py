"""A Partida — o agregado que reúne tabuleiro, estado e histórico.

A ``Partida`` é a fachada do domínio para o resto do sistema. Ela mantém a
posição (``Tabuleiro``), o estado atual (padrão State) e o histórico de
lances, e é o único ponto por onde um lance entra no jogo. Antes de aplicar
qualquer lance, ela garante duas invariantes:

* a partida ainda aceita lances (não terminou em mate ou empate);
* o lance pedido está entre os lances **legais** da posição.

Os lances passam por um ``GerenciadorHistorico``: cada um é um Command que
carrega um Memento, o que dá undo/redo praticamente de graça. E, para a
análise "e se?", a partida sabe se **clonar** (Prototype), produzindo uma
cópia independente onde lances hipotéticos não afetam o jogo real.
"""

from __future__ import annotations

import copy

from app.domain.board import Tabuleiro
from app.domain.erros import LanceIlegalError, PartidaEncerradaError
from app.domain.history import ComandoLance, GerenciadorHistorico
from app.domain.moves.lance import Lance
from app.domain.moves.validador import ValidadorDeLances
from app.domain.states import EstadoPartida, classificar_estado


class Partida:
    def __init__(
        self,
        tabuleiro: Tabuleiro | None = None,
        validador: ValidadorDeLances | None = None,
    ) -> None:
        self._tabuleiro = tabuleiro or Tabuleiro.inicial()
        self._validador = validador or ValidadorDeLances()
        self._historico = GerenciadorHistorico()
        # Quantas vezes cada posição já apareceu — base da tripla repetição.
        self._contagem_posicoes: dict[tuple, int] = {}
        self._registrar_posicao()
        self._estado = self._classificar()

    # -- Consultas -------------------------------------------------------

    @property
    def tabuleiro(self) -> Tabuleiro:
        return self._tabuleiro

    @property
    def estado(self) -> EstadoPartida:
        return self._estado

    @property
    def vez(self):
        return self._tabuleiro.vez

    @property
    def terminada(self) -> bool:
        return self._estado.terminada

    @property
    def historico(self) -> list[Lance]:
        """Lances já jogados, na ordem em que ocorreram."""
        return [comando.lance for comando in self._historico.executados]

    def pode_desfazer(self) -> bool:
        return self._historico.pode_desfazer()

    def pode_refazer(self) -> bool:
        return self._historico.pode_refazer()

    def lances_legais(self) -> list[Lance]:
        return self._validador.gerar_legais(self._tabuleiro, self._tabuleiro.vez)

    # -- Comandos --------------------------------------------------------

    def aplicar_lance(self, lance: Lance) -> Lance:
        """Aplica um lance pedido, se for legal, e atualiza o estado.

        O ``lance`` recebido carrega apenas a intenção (origem, destino e a
        eventual promoção); a partida o casa com o lance legal correspondente
        — que já traz os marcadores corretos de roque/en passant — e aplica
        esse, através de um Command no histórico. Levanta
        ``PartidaEncerradaError`` se o jogo já acabou e ``LanceIlegalError``
        se o lance não for legal na posição.
        """
        if not self._estado.permite_lance():
            raise PartidaEncerradaError(
                f"A partida já terminou ({self._estado.descricao})."
            )

        lance_legal = self._casar_com_lance_legal(lance)
        if lance_legal is None:
            raise LanceIlegalError(f"Lance ilegal na posição atual: {lance}.")

        self._historico.executar(ComandoLance(lance_legal), self._tabuleiro)
        self._registrar_posicao()
        self._estado = self._classificar()
        return lance_legal

    def desfazer(self) -> bool:
        """Desfaz o último lance. Devolve ``False`` se não houver o que desfazer."""
        if not self._historico.pode_desfazer():
            return False
        self._remover_posicao_atual()
        self._historico.desfazer(self._tabuleiro)
        self._estado = self._classificar()
        return True

    def refazer(self) -> bool:
        """Refaz o último lance desfeito. ``False`` se não houver o que refazer."""
        if not self._historico.pode_refazer():
            return False
        self._historico.refazer(self._tabuleiro)
        self._registrar_posicao()
        self._estado = self._classificar()
        return True

    def clonar(self) -> "Partida":
        """Cria uma cópia profunda e independente da partida (Prototype).

        Usada pela análise "e se?": lances hipotéticos são aplicados no clone
        sem qualquer efeito sobre a partida original (ver ADR-005).
        """
        return copy.deepcopy(self)

    # -- Bastidores ------------------------------------------------------

    def _casar_com_lance_legal(self, pedido: Lance) -> Lance | None:
        for legal in self.lances_legais():
            if (
                legal.origem == pedido.origem
                and legal.destino == pedido.destino
                and legal.promocao == pedido.promocao
            ):
                return legal
        return None

    def _registrar_posicao(self) -> None:
        chave = self._tabuleiro.chave_posicao()
        self._contagem_posicoes[chave] = self._contagem_posicoes.get(chave, 0) + 1

    def _remover_posicao_atual(self) -> None:
        chave = self._tabuleiro.chave_posicao()
        contagem = self._contagem_posicoes.get(chave, 0)
        if contagem <= 1:
            self._contagem_posicoes.pop(chave, None)
        else:
            self._contagem_posicoes[chave] = contagem - 1

    def _classificar(self) -> EstadoPartida:
        chave_atual = self._tabuleiro.chave_posicao()
        repeticoes = self._contagem_posicoes.get(chave_atual, 0)
        return classificar_estado(self._tabuleiro, self.lances_legais(), repeticoes)
