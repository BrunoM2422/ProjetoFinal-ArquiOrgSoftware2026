"""Erros da camada de aplicação.

Distintos dos erros de domínio (``app.domain.erros``): estes nascem da
orquestração dos casos de uso, não das regras do xadrez. O adaptador REST
(Fase 7) traduz cada um no código HTTP adequado — por exemplo,
``PartidaNaoEncontradaError`` vira 404 e ``NivelDeBotInvalidoError`` vira 400.
"""

from __future__ import annotations


class ErroDeAplicacao(Exception):
    """Raiz dos erros previsíveis da camada de aplicação."""


class PartidaNaoEncontradaError(ErroDeAplicacao):
    """Pediu-se uma partida cujo identificador não existe no repositório."""

    def __init__(self, id_partida: str) -> None:
        super().__init__(f"Partida não encontrada: {id_partida!r}.")
        self.id_partida = id_partida


class NivelDeBotInvalidoError(ErroDeAplicacao):
    """O nível de bot pedido ao criar a partida não é um nível conhecido."""

    def __init__(self, nivel: str, disponiveis: tuple[str, ...]) -> None:
        super().__init__(
            f"Nível de bot inválido: {nivel!r}. Disponíveis: {disponiveis}."
        )
        self.nivel = nivel
        self.disponiveis = disponiveis
