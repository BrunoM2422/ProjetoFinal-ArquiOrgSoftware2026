"""Avaliação de material — a régua compartilhada pelas estratégias.

Tanto o bot guloso quanto o minimax precisam pontuar uma posição. Aqui a
régua é deliberadamente simples: a soma do valor das peças do lado avaliado
menos a soma do valor das peças adversárias. Não há avaliação posicional
(centro, segurança do rei, estrutura de peões) — isso seria entrar no
terreno de um motor de xadrez forte, que está fora do escopo do projeto.
"""

from __future__ import annotations

from app.domain.board import Tabuleiro
from app.domain.cor import Cor


def material(tabuleiro: Tabuleiro, cor: Cor) -> int:
    """Saldo de material do ponto de vista de ``cor`` (positivo = vantagem)."""
    saldo = 0
    for peca in tabuleiro.casas.values():
        saldo += peca.valor if peca.cor is cor else -peca.valor
    return saldo
