"""Composition root da aplicação — o "árbitro" que monta a mesa.

Este é o único lugar autorizado a conhecer ao mesmo tempo as portas da
aplicação e os adaptadores concretos. Aqui as dependências são instanciadas
e injetadas (DIP): o adaptador de persistência implementa a porta, o serviço
de aplicação recebe esse repositório, e o adaptador de API recebe o serviço.

Também é onde os erros previsíveis (de domínio e de aplicação) são traduzidos
em respostas HTTP com os códigos combinados — convenção registrada no ADR-002:

* 400 — lance ilegal, nível de bot inválido, entrada malformada;
* 404 — partida inexistente;
* 409 — conflito de estado (fora de vez, partida já encerrada).
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.adapters.api.rotas import criar_rotas
from app.adapters.persistence.repositorio_memoria import RepositorioEmMemoria
from app.application.erros import (
    NivelDeBotInvalidoError,
    PartidaNaoEncontradaError,
)
from app.application.servico_partidas import ServicoDePartidas
from app.domain.erros import LanceIlegalError, PartidaEncerradaError


def create_app() -> FastAPI:
    """Constrói e configura a aplicação FastAPI (application factory)."""
    app = FastAPI(
        title="Plataforma de Treino de Xadrez",
        version="0.1.0",
        description="API REST de uma plataforma de treino de xadrez contra um bot.",
    )

    # O frontend (Vite) roda em outra origem durante o desenvolvimento.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Montagem das dependências (composition root).
    repositorio = RepositorioEmMemoria()
    servico = ServicoDePartidas(repositorio)
    app.include_router(criar_rotas(servico))

    _registrar_tratadores_de_erro(app)

    @app.get("/health", tags=["infra"])
    def health() -> dict[str, str]:
        """Sinaliza que o servidor está no ar."""
        return {"status": "ok"}

    return app


def _registrar_tratadores_de_erro(app: FastAPI) -> None:
    """Traduz as exceções previsíveis nos códigos HTTP combinados."""

    def _resposta(codigo: int, mensagem: str) -> JSONResponse:
        return JSONResponse(status_code=codigo, content={"erro": mensagem})

    @app.exception_handler(PartidaNaoEncontradaError)
    def _nao_encontrada(_: Request, exc: PartidaNaoEncontradaError) -> JSONResponse:
        return _resposta(status.HTTP_404_NOT_FOUND, str(exc))

    @app.exception_handler(LanceIlegalError)
    def _ilegal(_: Request, exc: LanceIlegalError) -> JSONResponse:
        return _resposta(status.HTTP_400_BAD_REQUEST, str(exc))

    @app.exception_handler(NivelDeBotInvalidoError)
    def _nivel_invalido(_: Request, exc: NivelDeBotInvalidoError) -> JSONResponse:
        return _resposta(status.HTTP_400_BAD_REQUEST, str(exc))

    @app.exception_handler(PartidaEncerradaError)
    def _encerrada(_: Request, exc: PartidaEncerradaError) -> JSONResponse:
        return _resposta(status.HTTP_409_CONFLICT, str(exc))

    @app.exception_handler(ValueError)
    def _valor_invalido(_: Request, exc: ValueError) -> JSONResponse:
        return _resposta(status.HTTP_400_BAD_REQUEST, str(exc))


app = create_app()
