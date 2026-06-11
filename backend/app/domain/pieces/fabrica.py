"""Fábrica de peças — o ponto único de criação da hierarquia ``Peca``.

Aqui vive o padrão **Factory Method**: o resto do sistema nunca instancia
``Torre``, ``Cavalo`` etc. diretamente. Ele entrega um *símbolo* (a letra
FEN da peça) e recebe de volta a peça concreta correta, já com a cor certa.

A convenção FEN é o contrato: letra **maiúscula** indica peça **branca**,
**minúscula** indica peça **preta** — por exemplo, ``"N"`` é um cavalo
branco e ``"q"`` é uma dama preta. Centralizar a criação aqui significa
que montar o tabuleiro a partir de uma string FEN é apenas pedir uma peça
por casa, e que adicionar uma nova peça no futuro toca um só lugar.
"""

from __future__ import annotations

from app.domain.cor import Cor
from app.domain.pieces.bispo import Bispo
from app.domain.pieces.cavalo import Cavalo
from app.domain.pieces.dama import Dama
from app.domain.pieces.peao import Peao
from app.domain.pieces.peca import Peca
from app.domain.pieces.rei import Rei
from app.domain.pieces.torre import Torre

# Mapeia cada símbolo FEN (sempre em maiúsculo) para a sua classe de peça.
_CLASSES_POR_SIMBOLO: dict[str, type[Peca]] = {
    Rei.simbolo: Rei,
    Dama.simbolo: Dama,
    Torre.simbolo: Torre,
    Bispo.simbolo: Bispo,
    Cavalo.simbolo: Cavalo,
    Peao.simbolo: Peao,
}


def criar_peca(simbolo: str) -> Peca:
    """Cria a peça correspondente a um símbolo FEN.

    A cor é inferida pela caixa da letra: maiúscula = branca, minúscula =
    preta. Levanta ``ValueError`` para símbolos desconhecidos.
    """
    if len(simbolo) != 1 or not simbolo.isalpha():
        raise ValueError(f"Símbolo de peça inválido: {simbolo!r}")

    cor = Cor.BRANCA if simbolo.isupper() else Cor.PRETA
    classe = _CLASSES_POR_SIMBOLO.get(simbolo.upper())
    if classe is None:
        raise ValueError(f"Símbolo de peça desconhecido: {simbolo!r}")
    return classe(cor)
