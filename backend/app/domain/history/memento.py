"""O Memento do tabuleiro — padrão **Memento**.

Um memento é uma "fotografia" do estado do tabuleiro tirada antes de um
lance, para que o undo possa restaurá-la depois. O ponto do padrão é a
*opacidade*: só o tabuleiro (o originador) sabe ler o conteúdo desta
fotografia; o gerenciador de histórico (o caretaker) apenas a guarda numa
pilha, sem nunca espiar lá dentro. Assim, a estrutura interna do tabuleiro
não vaza para quem cuida do histórico.

O conteúdo é guardado já em cópia profunda (ver ADR-005): se a fotografia
compartilhasse as mesmas listas e dicionários do tabuleiro vivo, um lance
posterior a corromperia, e o undo deixaria de ser confiável.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.casa import Casa
from app.domain.cor import Cor

if TYPE_CHECKING:
    from app.domain.pieces.peca import Peca


class MementoTabuleiro:
    """Estado congelado do tabuleiro. Opaco para todos, exceto o tabuleiro."""

    def __init__(
        self,
        casas: dict[Casa, "Peca"],
        vez: Cor,
        direitos_roque: set[str],
        alvo_en_passant: Casa | None,
        meio_lances_sem_progresso: int,
    ) -> None:
        # Atributos "privados": fazem parte da interface ampla que só o
        # originador (Tabuleiro) acessa. O caretaker trata o memento como
        # uma caixa-preta.
        self._casas = casas
        self._vez = vez
        self._direitos_roque = direitos_roque
        self._alvo_en_passant = alvo_en_passant
        self._meio_lances_sem_progresso = meio_lances_sem_progresso
