"""Estados da partida — padrão **State**.

EmAndamento, Xeque, XequeMate, Empate. Cada estado decide o que é
permitido e qual a próxima transição, evitando um if/else gigante de
status espalhado pelo agregado da partida.
"""

from app.domain.states.classificador import classificar_estado
from app.domain.states.estado import (
    EmAndamento,
    Empate,
    EstadoPartida,
    Xeque,
    XequeMate,
)

__all__ = [
    "EstadoPartida",
    "EmAndamento",
    "Xeque",
    "XequeMate",
    "Empate",
    "classificar_estado",
]
