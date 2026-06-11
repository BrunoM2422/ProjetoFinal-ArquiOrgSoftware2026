"""Tradução entre o domínio/aplicação e os DTOs da API.

Concentrar o mapeamento aqui mantém as rotas enxutas e o domínio ignorante
da camada HTTP: nenhuma classe de domínio sabe o que é um ``PartidaView``.
A conversão de entrada (DTO → objetos de domínio) levanta ``ValueError`` para
coordenadas malformadas, que o adaptador mapeia para HTTP 400.
"""

from __future__ import annotations

from app.adapters.api.schemas import (
    AnaliseView,
    EstadoView,
    LanceRequest,
    LanceView,
    PartidaView,
    ResultadoLanceView,
)
from app.application.modelos import (
    RegistroDePartida,
    ResultadoAnalise,
    ResultadoLance,
)
from app.domain.casa import Casa
from app.domain.cor import Cor
from app.domain.moves.lance import Lance
from app.domain.states.estado import EstadoPartida


# -- Entrada: DTO -> domínio --------------------------------------------


def cor_de_texto(texto: str) -> Cor:
    """Converte 'branca'/'preta' em ``Cor`` (ValueError se inválido)."""
    return Cor(texto)


def lance_de_request(req: LanceRequest) -> Lance:
    """Constrói um ``Lance`` de intenção a partir do DTO de entrada."""
    return Lance(
        origem=Casa.de_algebrica(req.origem),
        destino=Casa.de_algebrica(req.destino),
        promocao=req.promocao,
    )


# -- Saída: domínio -> DTO ----------------------------------------------


def view_lance(lance: Lance) -> LanceView:
    return LanceView(
        origem=lance.origem.algebrica,
        destino=lance.destino.algebrica,
        promocao=lance.promocao,
        notacao=str(lance),
    )


def view_estado(estado: EstadoPartida) -> EstadoView:
    return EstadoView(
        nome=estado.nome,
        descricao=estado.descricao,
        terminada=estado.terminada,
        em_xeque=estado.em_xeque,
        resultado=estado.resultado,
    )


def view_partida(registro: RegistroDePartida) -> PartidaView:
    partida = registro.partida
    return PartidaView(
        id=registro.id,
        fen=partida.tabuleiro.para_fen(),
        vez=partida.vez.value,
        estado=view_estado(partida.estado),
        historico=[str(lance) for lance in partida.historico],
        lances_legais=[view_lance(lance) for lance in partida.lances_legais()],
        pode_desfazer=partida.pode_desfazer(),
        pode_refazer=partida.pode_refazer(),
        nivel_bot=registro.nivel_bot,
        cor_bot=registro.cor_bot.value,
        cor_humano=registro.cor_humano.value,
    )


def view_resultado_lance(resultado: ResultadoLance) -> ResultadoLanceView:
    return ResultadoLanceView(
        partida=view_partida(resultado.registro),
        lance_humano=view_lance(resultado.lance_humano),
        lance_bot=view_lance(resultado.lance_bot) if resultado.lance_bot else None,
    )


def view_analise(resultado: ResultadoAnalise) -> AnaliseView:
    hipotetica = resultado.partida_hipotetica
    return AnaliseView(
        fen=hipotetica.tabuleiro.para_fen(),
        vez=hipotetica.vez.value,
        estado=view_estado(hipotetica.estado),
        historico=[str(lance) for lance in hipotetica.historico],
        lance_sugerido=(
            view_lance(resultado.lance_sugerido)
            if resultado.lance_sugerido
            else None
        ),
    )
