"""Rotas REST da plataforma de treino.

Cada rota traduz uma requisição HTTP numa chamada a um caso de uso do
``ServicoDePartidas`` e devolve o resultado como DTO. As rotas não contêm
regra de jogo nem de orquestração: validam/convertem a entrada, delegam e
mapeiam a saída.

O router é montado por uma fábrica que recebe o serviço já pronto, deixando a
injeção de dependência a cargo do composition root (``main.py``) — é o
adaptador dependendo da aplicação por construção, nunca o contrário.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.adapters.api import mapeadores
from app.adapters.api.schemas import (
    AnaliseRequest,
    AnaliseView,
    CriarPartidaRequest,
    LanceRequest,
    PartidaView,
    ResultadoLanceView,
)
from app.application.servico_partidas import ServicoDePartidas


def criar_rotas(servico: ServicoDePartidas) -> APIRouter:
    """Cria o router /v1 ligado a uma instância do serviço de partidas."""
    router = APIRouter(prefix="/v1", tags=["partidas"])

    @router.post(
        "/games",
        response_model=PartidaView,
        status_code=status.HTTP_201_CREATED,
        summary="Cria uma nova partida contra o bot",
    )
    def criar_partida(corpo: CriarPartidaRequest) -> PartidaView:
        cor_humano = mapeadores.cor_de_texto(corpo.cor_humano)
        registro = servico.criar_partida(corpo.nivel_bot, cor_humano=cor_humano)
        return mapeadores.view_partida(registro)

    @router.get(
        "/games/{id_partida}",
        response_model=PartidaView,
        summary="Consulta o estado de uma partida",
    )
    def obter_partida(id_partida: str) -> PartidaView:
        registro = servico.obter_partida(id_partida)
        return mapeadores.view_partida(registro)

    @router.get(
        "/games/{id_partida}/moves",
        response_model=list[str],
        summary="Lista os lances já jogados",
    )
    def listar_lances(id_partida: str) -> list[str]:
        registro = servico.obter_partida(id_partida)
        return [str(lance) for lance in registro.partida.historico]

    @router.post(
        "/games/{id_partida}/moves",
        response_model=ResultadoLanceView,
        summary="Aplica um lance do humano (o bot responde)",
    )
    def aplicar_lance(id_partida: str, corpo: LanceRequest) -> ResultadoLanceView:
        registro = servico.obter_partida(id_partida)
        _garantir_vez_do_humano(registro, corpo)
        lance = mapeadores.lance_de_request(corpo)
        resultado = servico.aplicar_lance(id_partida, lance)
        return mapeadores.view_resultado_lance(resultado)

    @router.post(
        "/games/{id_partida}/undo",
        response_model=PartidaView,
        summary="Desfaz a última jogada",
    )
    def desfazer(id_partida: str) -> PartidaView:
        registro = servico.desfazer(id_partida)
        return mapeadores.view_partida(registro)

    @router.post(
        "/games/{id_partida}/redo",
        response_model=PartidaView,
        summary="Refaz a última jogada desfeita",
    )
    def refazer(id_partida: str) -> PartidaView:
        registro = servico.refazer(id_partida)
        return mapeadores.view_partida(registro)

    @router.post(
        "/games/{id_partida}/analysis",
        response_model=AnaliseView,
        summary="Explora uma linha hipotética ('e se?') sem afetar a partida",
    )
    def analisar(id_partida: str, corpo: AnaliseRequest) -> AnaliseView:
        lances = [mapeadores.lance_de_request(item) for item in corpo.lances]
        resultado = servico.analisar(id_partida, lances)
        return mapeadores.view_analise(resultado)

    return router


def _garantir_vez_do_humano(registro, corpo: LanceRequest) -> None:
    """Recusa um lance de uma peça que não é do lado da vez (HTTP 409).

    O domínio já recusaria como ilegal, mas distinguir "fora de vez" de "lance
    ilegal" dá à interface uma mensagem mais precisa (conflito de estado).
    """
    from app.domain.casa import Casa

    try:
        origem = Casa.de_algebrica(corpo.origem)
    except ValueError:
        return  # entrada malformada vira 400 mais adiante, no mapeador
    peca = registro.partida.tabuleiro.peca_em(origem)
    if peca is not None and peca.cor is not registro.partida.vez:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é a vez dessa cor.",
        )
