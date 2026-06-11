"""Adaptador de persistência em memória.

Implementação da porta ``RepositorioDePartidas`` que guarda as sessões num
dicionário em memória (ver ADR-004). É suficiente para o escopo de treino,
onde uma partida vive enquanto o processo está no ar. Trocar por um banco
real no futuro significa escrever outro adaptador que implemente a mesma
porta — sem tocar na aplicação nem no domínio.
"""

from __future__ import annotations

from app.application.modelos import RegistroDePartida
from app.application.portas import RepositorioDePartidas


class RepositorioEmMemoria(RepositorioDePartidas):
    """Guarda as sessões de jogo num dicionário indexado pelo identificador."""

    def __init__(self) -> None:
        self._partidas: dict[str, RegistroDePartida] = {}

    def salvar(self, registro: RegistroDePartida) -> None:
        self._partidas[registro.id] = registro

    def obter(self, id_partida: str) -> RegistroDePartida | None:
        return self._partidas.get(id_partida)
