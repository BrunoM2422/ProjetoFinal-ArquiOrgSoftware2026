"""Estados da partida — o padrão **State**.

Em vez de espalhar um ``if status == "xeque_mate"`` por todo o agregado, o
estado da partida é um objeto. Cada estado responde de forma polimórfica a
duas perguntas que o resto do sistema faz o tempo todo:

* *a partida ainda aceita lances?* (``permite_lance``)
* *qual é o resultado?* (``resultado``)

Assim, encerrar a partida ao dar xeque-mate não é um ``if`` no meio do
fluxo de lances: é simplesmente estar num estado terminal cujo
``permite_lance`` devolve ``False``. Adicionar um novo estado no futuro não
exige mexer no código que já existe (OCP).

A *transição* entre estados — decidir, depois de um lance, em qual estado a
partida caiu — depende apenas da posição resultante, não do estado
anterior. Por isso ela é centralizada no classificador
(``states/classificador.py``), e não duplicada dentro de cada estado.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.cor import Cor


class EstadoPartida(ABC):
    """Contrato comum aos estados da partida."""

    #: Identificador estável do estado (útil para serializar na API).
    nome: str = ""
    #: Indica se a partida chegou ao fim (mate ou empate).
    terminada: bool = False
    #: Indica se o rei do lado da vez está sob ataque.
    em_xeque: bool = False
    #: Resultado em notação PGN: "1-0", "0-1", "1/2-1/2" ou None se em curso.
    resultado: str | None = None

    def permite_lance(self) -> bool:
        """Só estados não terminais aceitam novos lances."""
        return not self.terminada

    @property
    @abstractmethod
    def descricao(self) -> str:
        """Texto legível do estado, para exibição."""


class EmAndamento(EstadoPartida):
    nome = "em_andamento"

    @property
    def descricao(self) -> str:
        return "Partida em andamento."


class Xeque(EstadoPartida):
    nome = "xeque"
    em_xeque = True

    @property
    def descricao(self) -> str:
        return "O rei do lado da vez está em xeque."


class XequeMate(EstadoPartida):
    nome = "xeque_mate"
    terminada = True
    em_xeque = True

    def __init__(self, vencedor: Cor) -> None:
        self.vencedor = vencedor
        self.resultado = "1-0" if vencedor is Cor.BRANCA else "0-1"

    @property
    def descricao(self) -> str:
        return f"Xeque-mate. Vitória das peças {self.vencedor.value}s."


class Empate(EstadoPartida):
    nome = "empate"
    terminada = True
    resultado = "1/2-1/2"

    def __init__(self, motivo: str) -> None:
        self.motivo = motivo

    @property
    def descricao(self) -> str:
        return f"Empate por {self.motivo}."
