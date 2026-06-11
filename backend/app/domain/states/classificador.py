"""Classificador de estados — a transição do padrão State.

Depois de cada lance, é preciso decidir em que estado a partida caiu. Essa
decisão depende somente da *posição resultante* (e do histórico de
repetições / do relógio dos 50 lances), nunca do estado anterior — por isso
é centralizada aqui, e não espalhada dentro de cada estado.

A ordem das verificações importa: mate e afogamento (ausência de lances
legais) vêm primeiro; depois os empates "automáticos" por material, relógio
e repetição; e só então xeque ou partida em andamento.
"""

from __future__ import annotations

from app.domain.board import Tabuleiro
from app.domain.moves.lance import Lance
from app.domain.pieces import Bispo, Dama, Peao, Rei, Torre
from app.domain.states.estado import (
    EmAndamento,
    Empate,
    EstadoPartida,
    Xeque,
    XequeMate,
)

# Limite da regra dos 50 lances, contado em meios-lances (50 de cada lado).
_LIMITE_50_LANCES = 100
# Número de repetições da mesma posição que caracteriza empate.
_REPETICOES_PARA_EMPATE = 3


def classificar_estado(
    tabuleiro: Tabuleiro,
    lances_legais: list[Lance],
    repeticoes_posicao_atual: int,
) -> EstadoPartida:
    cor = tabuleiro.vez
    em_xeque = tabuleiro.esta_em_xeque(cor)

    if not lances_legais:
        # Sem resposta legal: em xeque é mate; fora de xeque é afogamento.
        return XequeMate(vencedor=cor.adversaria) if em_xeque else Empate("afogamento")

    if _material_insuficiente(tabuleiro):
        return Empate("material insuficiente")
    if tabuleiro.meio_lances_sem_progresso >= _LIMITE_50_LANCES:
        return Empate("regra dos 50 lances")
    if repeticoes_posicao_atual >= _REPETICOES_PARA_EMPATE:
        return Empate("tripla repetição")

    return Xeque() if em_xeque else EmAndamento()


def _material_insuficiente(tabuleiro: Tabuleiro) -> bool:
    """Indica se nenhum dos lados tem material para dar mate.

    Cobre os casos clássicos de posição morta: rei contra rei, rei e uma
    peça menor contra rei, e rei e bispo contra rei e bispo com os bispos
    na mesma cor de casa. Peão, torre ou dama em campo já bastam para haver
    material suficiente.
    """
    pecas_sem_rei = [peca for peca in tabuleiro.casas.values() if not isinstance(peca, Rei)]

    if any(isinstance(peca, (Peao, Torre, Dama)) for peca in pecas_sem_rei):
        return False

    # A partir daqui só restam bispos e cavalos além dos reis.
    if len(pecas_sem_rei) <= 1:
        return True  # rei contra rei, ou rei e uma peça menor contra rei

    if len(pecas_sem_rei) == 2 and all(isinstance(peca, Bispo) for peca in pecas_sem_rei):
        return _bispos_na_mesma_cor(tabuleiro)

    return False


def _bispos_na_mesma_cor(tabuleiro: Tabuleiro) -> bool:
    cores_das_casas = {
        (casa.coluna + casa.linha) % 2
        for casa, peca in tabuleiro.casas.items()
        if isinstance(peca, Bispo)
    }
    return len(cores_das_casas) == 1
