"""Porta da estratégia de bot — onde o Strategy se conecta ao domínio.

Esta é uma porta pequena e focada (ISP): tudo que uma estratégia de bot
precisa expor é "dada uma partida, escolha um lance". Quem orquestra o bot
(o caso de uso) depende apenas desta abstração, nunca de uma estratégia
concreta — é o que permite trocar o nível de dificuldade injetando outra
implementação, sem tocar no código que usa o bot (DIP + OCP).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.moves.lance import Lance
    from app.domain.partida import Partida


class EstrategiaDeBot(ABC):
    """Contrato de uma estratégia que escolhe lances por um lado."""

    #: Identificador do nível, usado pela API e pela fábrica de estratégias.
    nome: str = ""

    @abstractmethod
    def escolher_lance(self, partida: "Partida") -> "Lance | None":
        """Escolhe um lance legal para o lado da vez.

        Devolve ``None`` quando não há lance possível (a partida já acabou),
        deixando a quem chamou a decisão sobre o que fazer nesse caso.
        """
