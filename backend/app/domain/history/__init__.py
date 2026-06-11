"""Histórico de lances e undo/redo — padrões **Command** + **Memento**.

Cada lance é um Command executável e desfazível; o Memento captura o
estado do tabuleiro para o undo/redo sem expor a estrutura interna do
agregado da partida.
"""

from app.domain.history.comando import Comando, ComandoLance
from app.domain.history.gerenciador import GerenciadorHistorico
from app.domain.history.memento import MementoTabuleiro

__all__ = [
    "Comando",
    "ComandoLance",
    "GerenciadorHistorico",
    "MementoTabuleiro",
]
