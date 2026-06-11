"""Estratégias do bot — padrão **Strategy**.

Níveis de dificuldade intercambiáveis (aleatório, guloso por material,
minimax raso). O caso de uso "bot escolhe um lance" não muda; apenas a
estratégia injetada muda.
"""

from app.domain.bots.aleatoria import EstrategiaAleatoria
from app.domain.bots.fabrica import NIVEIS_DISPONIVEIS, criar_estrategia
from app.domain.bots.gulosa import EstrategiaGulosa
from app.domain.bots.minimax import EstrategiaMinimax
from app.domain.ports.estrategia_bot import EstrategiaDeBot

__all__ = [
    "EstrategiaDeBot",
    "EstrategiaAleatoria",
    "EstrategiaGulosa",
    "EstrategiaMinimax",
    "criar_estrategia",
    "NIVEIS_DISPONIVEIS",
]
