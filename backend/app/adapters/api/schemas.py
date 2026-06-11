"""DTOs da API REST (schemas pydantic).

Estes são os contratos de entrada e saída do adaptador HTTP — propositalmente
separados dos objetos de domínio. Mantê-los aqui permite que a forma da API
evolua (campos, nomes, formatos) sem pressionar o modelo do jogo, e é o que
o pydantic usa para validar a entrada e gerar a documentação OpenAPI.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# -- Entrada ------------------------------------------------------------


class CriarPartidaRequest(BaseModel):
    """Corpo de POST /games."""

    nivel_bot: str = Field(
        ...,
        description="Nível do bot adversário.",
        examples=["aleatorio", "guloso", "minimax"],
    )
    cor_humano: str = Field(
        "branca",
        description="Cor controlada pelo humano ('branca' ou 'preta').",
    )


class LanceRequest(BaseModel):
    """Um lance pedido, em coordenadas algébricas."""

    origem: str = Field(..., description="Casa de origem, ex.: 'e2'.", examples=["e2"])
    destino: str = Field(..., description="Casa de destino, ex.: 'e4'.", examples=["e4"])
    promocao: str | None = Field(
        None,
        description="Símbolo da peça promovida (Q, R, B, N), só em promoção de peão.",
    )


class AnaliseRequest(BaseModel):
    """Corpo de POST /games/{id}/analysis: a linha hipotética a explorar."""

    lances: list[LanceRequest] = Field(
        default_factory=list,
        description="Sequência hipotética de lances a aplicar sobre a posição atual.",
    )


# -- Saída --------------------------------------------------------------


class LanceView(BaseModel):
    """Representação de um lance na resposta."""

    origem: str
    destino: str
    promocao: str | None = None
    notacao: str = Field(..., description="Forma compacta, ex.: 'e2e4' ou 'a7a8=Q'.")


class EstadoView(BaseModel):
    """O estado da partida (padrão State) exposto na resposta."""

    nome: str
    descricao: str
    terminada: bool
    em_xeque: bool
    resultado: str | None = None


class PartidaView(BaseModel):
    """Fotografia completa de uma partida para a interface."""

    id: str
    fen: str
    vez: str
    estado: EstadoView
    historico: list[str] = Field(..., description="Lances jogados, em notação compacta.")
    lances_legais: list[LanceView]
    pode_desfazer: bool
    pode_refazer: bool
    nivel_bot: str
    cor_bot: str
    cor_humano: str


class ResultadoLanceView(BaseModel):
    """Resposta de POST /games/{id}/moves: o lance do humano e a resposta do bot."""

    partida: PartidaView
    lance_humano: LanceView
    lance_bot: LanceView | None = None


class AnaliseView(BaseModel):
    """Resposta de POST /games/{id}/analysis: a posição hipotética e a sugestão."""

    fen: str
    vez: str
    estado: EstadoView
    historico: list[str]
    lance_sugerido: LanceView | None = None
