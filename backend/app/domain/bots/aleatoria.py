"""Estratégia aleatória — o nível mais fácil do bot.

Sorteia um lance qualquer entre os legais. Não olha material nem o futuro:
serve de piso de dificuldade e de baseline para comparar as demais
estratégias. Aceita um gerador de aleatoriedade injetado, o que torna o
comportamento reproduzível nos testes.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from app.domain.ports.estrategia_bot import EstrategiaDeBot

if TYPE_CHECKING:
    from app.domain.moves.lance import Lance
    from app.domain.partida import Partida


class EstrategiaAleatoria(EstrategiaDeBot):
    nome = "aleatorio"

    def __init__(self, aleatorio: random.Random | None = None) -> None:
        self._aleatorio = aleatorio or random.Random()

    def escolher_lance(self, partida: "Partida") -> "Lance | None":
        legais = partida.lances_legais()
        return self._aleatorio.choice(legais) if legais else None
