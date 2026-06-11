"""O lance como Command — padrão **Command**.

Em vez de o tabuleiro simplesmente aplicar um lance, encapsulamos a ação
num objeto que sabe se *executar* e se *desfazer*. Essa reificação é o que
torna o undo/redo possível: o histórico guarda comandos, não chamadas de
função.

Command e Memento trabalham em par. Antes de executar, o comando pede ao
tabuleiro um memento (a fotografia do estado anterior) e o guarda; desfazer
é apenas mandar o tabuleiro restaurar esse memento. O comando não precisa
saber reverter manualmente captura, roque, en passant ou promoção — toda
essa complexidade fica resolvida pela fotografia.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from app.domain.history.memento import MementoTabuleiro
from app.domain.moves.lance import Lance

if TYPE_CHECKING:
    from app.domain.board import Tabuleiro


class Comando(ABC):
    """Ação executável e reversível sobre o tabuleiro."""

    @abstractmethod
    def executar(self, tabuleiro: "Tabuleiro") -> None: ...

    @abstractmethod
    def desfazer(self, tabuleiro: "Tabuleiro") -> None: ...


class ComandoLance(Comando):
    """Aplica um lance e sabe desfazê-lo restaurando o memento anterior."""

    def __init__(self, lance: Lance) -> None:
        self._lance = lance
        self._memento: MementoTabuleiro | None = None

    @property
    def lance(self) -> Lance:
        return self._lance

    def executar(self, tabuleiro: "Tabuleiro") -> None:
        # Fotografa o estado anterior antes de mexer no tabuleiro.
        self._memento = tabuleiro.criar_memento()
        tabuleiro.aplicar_lance(self._lance)

    def desfazer(self, tabuleiro: "Tabuleiro") -> None:
        if self._memento is None:
            raise RuntimeError("Não há memento: o comando ainda não foi executado.")
        tabuleiro.restaurar(self._memento)
