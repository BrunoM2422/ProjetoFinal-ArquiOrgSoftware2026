"""Peças do xadrez e suas regras de movimento.

Aqui mora o padrão **Factory Method**: cada símbolo (ex.: 'N' para cavalo)
é traduzido na subclasse de peça correta, e cada peça encapsula a geração
dos seus próprios lances pseudo-legais.
"""

from app.domain.pieces.bispo import Bispo
from app.domain.pieces.cavalo import Cavalo
from app.domain.pieces.dama import Dama
from app.domain.pieces.fabrica import criar_peca
from app.domain.pieces.peao import Peao
from app.domain.pieces.peca import Peca
from app.domain.pieces.rei import Rei
from app.domain.pieces.torre import Torre

__all__ = [
    "Peca",
    "Rei",
    "Dama",
    "Torre",
    "Bispo",
    "Cavalo",
    "Peao",
    "criar_peca",
]
