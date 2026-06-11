"""Portas de saída da camada de aplicação.

Uma porta de saída (driven) é uma abstração que a aplicação **precisa** para
falar com o mundo externo, mas cuja implementação fica num adaptador. Aqui
está a porta de persistência: a aplicação depende apenas deste contrato, e o
adaptador concreto (em memória hoje, um banco amanhã) é injetado de fora —
é o exemplo de DIP/ISP do ADR-004.

A interface é deliberadamente mínima (ISP): guardar uma sessão e recuperá-la
por identificador é tudo de que os casos de uso precisam.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.application.modelos import RegistroDePartida


class RepositorioDePartidas(ABC):
    """Contrato de armazenamento das sessões de jogo."""

    @abstractmethod
    def salvar(self, registro: RegistroDePartida) -> None:
        """Persiste (ou atualiza) a sessão identificada por ``registro.id``."""

    @abstractmethod
    def obter(self, id_partida: str) -> RegistroDePartida | None:
        """Recupera a sessão pelo identificador, ou ``None`` se não existir."""
