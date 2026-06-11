"""Serviço de partidas — os casos de uso da plataforma de treino.

Esta é a camada de aplicação propriamente dita: ela orquestra o domínio para
realizar as intenções do usuário (criar partida, jogar, desfazer/refazer,
analisar), mas não contém nenhuma regra de xadrez — quem sabe o que é legal
e o que é xeque-mate é a ``Partida``. O serviço apenas costura as peças:

* fala com a persistência através da porta ``RepositorioDePartidas`` (DIP);
* cria o bot através da porta ``EstrategiaDeBot``, via fábrica injetada (OCP);
* mantém a invariante de que, depois de cada caso de uso, ou a partida está
  encerrada, ou é a vez do humano.

Essa última invariante é o que torna o serviço a "cola" do jogo humano-vs-bot:
ao aplicar o lance do humano, ele dispara a resposta do bot; ao desfazer, ele
desfaz a jogada inteira (resposta do bot + lance do humano), devolvendo o
controle ao humano.
"""

from __future__ import annotations

import uuid
from typing import Callable

from app.application.erros import (
    NivelDeBotInvalidoError,
    PartidaNaoEncontradaError,
)
from app.application.modelos import (
    RegistroDePartida,
    ResultadoAnalise,
    ResultadoLance,
)
from app.application.portas import RepositorioDePartidas
from app.domain.bots.fabrica import NIVEIS_DISPONIVEIS, criar_estrategia
from app.domain.cor import Cor
from app.domain.moves.lance import Lance
from app.domain.partida import Partida
from app.domain.ports.estrategia_bot import EstrategiaDeBot

#: Como o serviço obtém uma estratégia a partir do nome do nível. Injetável
#: para permitir bots determinísticos em teste.
FabricaDeEstrategia = Callable[[str], EstrategiaDeBot]


class ServicoDePartidas:
    """Casos de uso da partida humano-vs-bot."""

    def __init__(
        self,
        repositorio: RepositorioDePartidas,
        fabrica_estrategia: FabricaDeEstrategia = criar_estrategia,
        estrategia_analise: EstrategiaDeBot | None = None,
    ) -> None:
        self._repositorio = repositorio
        self._fabrica_estrategia = fabrica_estrategia
        # A análise "e se?" usa uma estratégia forte para sugerir continuações,
        # independente do nível com que a partida é jogada.
        self._estrategia_analise = estrategia_analise or criar_estrategia("minimax")

    # -- Casos de uso ----------------------------------------------------

    def criar_partida(
        self, nivel_bot: str, cor_humano: Cor = Cor.BRANCA
    ) -> RegistroDePartida:
        """Cria uma nova partida contra um bot do nível pedido.

        Se o bot ficar com as brancas, ele já abre a partida, de modo que o
        registro devolvido tem a vez do humano. Levanta
        ``NivelDeBotInvalidoError`` para níveis desconhecidos.
        """
        if nivel_bot not in NIVEIS_DISPONIVEIS:
            raise NivelDeBotInvalidoError(nivel_bot, NIVEIS_DISPONIVEIS)

        registro = RegistroDePartida(
            id=uuid.uuid4().hex,
            partida=Partida(),
            nivel_bot=nivel_bot,
            cor_bot=cor_humano.adversaria,
        )
        # Se for o bot quem joga a primeira, ele abre antes de devolvermos.
        if registro.partida.vez == registro.cor_bot:
            self._jogar_bot(registro)

        self._repositorio.salvar(registro)
        return registro

    def obter_partida(self, id_partida: str) -> RegistroDePartida:
        """Recupera a sessão; levanta ``PartidaNaoEncontradaError`` se não há."""
        registro = self._repositorio.obter(id_partida)
        if registro is None:
            raise PartidaNaoEncontradaError(id_partida)
        return registro

    def aplicar_lance(self, id_partida: str, lance: Lance) -> ResultadoLance:
        """Aplica o lance do humano e, se for o caso, deixa o bot responder.

        Propaga ``LanceIlegalError`` / ``PartidaEncerradaError`` do domínio
        quando o lance do humano não é aceito.
        """
        registro = self.obter_partida(id_partida)
        lance_humano = registro.partida.aplicar_lance(lance)

        lance_bot = None
        if not registro.partida.terminada and registro.partida.vez == registro.cor_bot:
            lance_bot = self._jogar_bot(registro)

        self._repositorio.salvar(registro)
        return ResultadoLance(registro, lance_humano, lance_bot)

    def desfazer(self, id_partida: str) -> RegistroDePartida:
        """Desfaz a última jogada inteira, devolvendo o controle ao humano.

        Numa partida com bot, "uma jogada" são dois lances (o do humano e a
        resposta do bot); desfazer ambos é o que faz o jogo voltar ao ponto em
        que o humano decide. Se nada houver para desfazer, nada muda.
        """
        registro = self.obter_partida(id_partida)
        partida = registro.partida
        if partida.pode_desfazer():
            partida.desfazer()
            # Volta também o lance do humano, se o que desfizemos foi a resposta
            # do bot (ficou a vez do bot).
            while partida.vez == registro.cor_bot and partida.pode_desfazer():
                partida.desfazer()
            # Caso de borda: desfizemos até uma posição em que é a vez do bot
            # (p.ex. desfazer a abertura do bot) — deixamos o bot jogar de novo
            # para que volte a ser a vez do humano.
            if not partida.terminada and partida.vez == registro.cor_bot:
                self._jogar_bot(registro)

        self._repositorio.salvar(registro)
        return registro

    def refazer(self, id_partida: str) -> RegistroDePartida:
        """Refaz a última jogada inteira desfeita (lance do humano + resposta)."""
        registro = self.obter_partida(id_partida)
        partida = registro.partida
        if partida.pode_refazer():
            partida.refazer()
            while partida.vez == registro.cor_bot and partida.pode_refazer():
                partida.refazer()

        self._repositorio.salvar(registro)
        return registro

    def analisar(
        self, id_partida: str, lances: list[Lance] | None = None
    ) -> ResultadoAnalise:
        """Explora uma linha hipotética sem afetar a partida real (Prototype).

        Clona a partida, aplica os ``lances`` hipotéticos no clone e devolve a
        posição resultante junto com a continuação que a estratégia de análise
        sugere. A partida original permanece intocada. Propaga
        ``LanceIlegalError`` / ``PartidaEncerradaError`` se algum lance
        hipotético for inválido na linha.
        """
        registro = self.obter_partida(id_partida)
        hipotetica = registro.partida.clonar()
        for lance in lances or []:
            hipotetica.aplicar_lance(lance)

        sugerido = None
        if not hipotetica.terminada:
            sugerido = self._estrategia_analise.escolher_lance(hipotetica)
        return ResultadoAnalise(hipotetica, sugerido)

    # -- Bastidores ------------------------------------------------------

    def _jogar_bot(self, registro: RegistroDePartida) -> Lance | None:
        """Faz o bot da sessão jogar um lance, se houver um a jogar."""
        partida = registro.partida
        if partida.terminada:
            return None
        estrategia = self._fabrica_estrategia(registro.nivel_bot)
        lance = estrategia.escolher_lance(partida)
        if lance is not None:
            partida.aplicar_lance(lance)
        return lance
