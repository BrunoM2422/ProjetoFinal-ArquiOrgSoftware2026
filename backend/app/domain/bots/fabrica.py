"""Fábrica de estratégias de bot.

Traduz o nome de um nível de dificuldade (como chega pela API) na estratégia
concreta correspondente. Concentrar a criação aqui mantém o resto do sistema
dependente só da porta ``EstrategiaDeBot``: adicionar um novo nível no futuro
significa registrar mais uma entrada neste mapa, sem tocar em quem usa o bot.
"""

from __future__ import annotations

import random

from app.domain.bots.aleatoria import EstrategiaAleatoria
from app.domain.bots.gulosa import EstrategiaGulosa
from app.domain.bots.minimax import EstrategiaMinimax
from app.domain.ports.estrategia_bot import EstrategiaDeBot

# Níveis disponíveis, na ordem do mais fácil para o mais difícil.
NIVEIS_DISPONIVEIS = (EstrategiaAleatoria.nome, EstrategiaGulosa.nome, EstrategiaMinimax.nome)


def criar_estrategia(
    nivel: str, aleatorio: random.Random | None = None
) -> EstrategiaDeBot:
    """Cria a estratégia de bot do ``nivel`` pedido.

    Levanta ``ValueError`` para níveis desconhecidos, deixando a validação do
    nome num único ponto.
    """
    if nivel == EstrategiaAleatoria.nome:
        return EstrategiaAleatoria(aleatorio)
    if nivel == EstrategiaGulosa.nome:
        return EstrategiaGulosa(aleatorio)
    if nivel == EstrategiaMinimax.nome:
        return EstrategiaMinimax(aleatorio=aleatorio)
    raise ValueError(
        f"Nível de bot desconhecido: {nivel!r}. Disponíveis: {NIVEIS_DISPONIVEIS}."
    )
