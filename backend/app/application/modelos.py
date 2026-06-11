"""Modelos da camada de aplicação.

São os objetos que a aplicação guarda e devolve ao orquestrar os casos de
uso. Não são DTOs da API (esses moram no adaptador REST, Fase 7): aqui ainda
circulam objetos de domínio (``Partida``, ``Lance``, ``Cor``).

O ``RegistroDePartida`` é a "sessão de jogo": junta a posição de xadrez (uma
``Partida``, que nada sabe de bots) com a configuração de quem joga contra o
humano — o nível e a cor do bot. Essa separação mantém o domínio puro: a
noção de "tem um bot do outro lado" é uma preocupação de aplicação.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.cor import Cor
from app.domain.moves.lance import Lance
from app.domain.partida import Partida


@dataclass(frozen=True)
class RegistroDePartida:
    """Uma sessão de jogo: a partida em si mais a configuração do bot.

    A ``Partida`` referenciada é mutável e evolui a cada lance; os demais
    campos (identidade e configuração do bot) são fixos pela vida da sessão.
    """

    id: str
    partida: Partida
    nivel_bot: str
    cor_bot: Cor

    @property
    def cor_humano(self) -> Cor:
        """A cor controlada pelo humano — o oposto da cor do bot."""
        return self.cor_bot.adversaria


@dataclass(frozen=True)
class ResultadoLance:
    """O efeito de aplicar um lance do humano.

    Carrega o lance humano efetivamente aplicado (já casado com o lance legal
    correspondente) e, quando houve, a resposta do bot — útil para a interface
    mostrar de uma vez o que aconteceu na jogada.
    """

    registro: RegistroDePartida
    lance_humano: Lance
    lance_bot: Lance | None = None


@dataclass(frozen=True)
class ResultadoAnalise:
    """O resultado de uma análise "e se?".

    ``partida_hipotetica`` é um clone independente (Prototype) onde os lances
    hipotéticos foram aplicados — a partida real não é tocada. ``lance_sugerido``
    é a continuação que a estratégia de análise recomenda a partir daí, ou
    ``None`` se a posição hipotética já estiver encerrada.
    """

    partida_hipotetica: Partida
    lance_sugerido: Lance | None = None
