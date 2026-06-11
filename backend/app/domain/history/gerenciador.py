"""Gerenciador de histórico — o caretaker do undo/redo.

Mantém duas pilhas: o **passado** (comandos já executados, prontos para
desfazer) e o **futuro** (comandos desfeitos, prontos para refazer). É um
caretaker no sentido do padrão Memento: guarda os comandos — e os mementos
que eles carregam — sem nunca inspecionar o conteúdo dessas fotografias.

A regra clássica do redo: assim que um lance *novo* é executado, o futuro é
descartado. Não faz sentido "refazer" uma linha que foi abandonada ao
seguir por outro caminho.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.history.comando import ComandoLance

if TYPE_CHECKING:
    from app.domain.board import Tabuleiro


class GerenciadorHistorico:
    def __init__(self) -> None:
        self._passado: list[ComandoLance] = []
        self._futuro: list[ComandoLance] = []

    @property
    def executados(self) -> list[ComandoLance]:
        """Comandos já executados, do mais antigo ao mais recente."""
        return list(self._passado)

    def pode_desfazer(self) -> bool:
        return bool(self._passado)

    def pode_refazer(self) -> bool:
        return bool(self._futuro)

    def executar(self, comando: ComandoLance, tabuleiro: "Tabuleiro") -> None:
        comando.executar(tabuleiro)
        self._passado.append(comando)
        self._futuro.clear()  # um lance novo abandona a linha de redo

    def desfazer(self, tabuleiro: "Tabuleiro") -> ComandoLance:
        comando = self._passado.pop()
        comando.desfazer(tabuleiro)
        self._futuro.append(comando)
        return comando

    def refazer(self, tabuleiro: "Tabuleiro") -> ComandoLance:
        comando = self._futuro.pop()
        comando.executar(tabuleiro)
        self._passado.append(comando)
        return comando
