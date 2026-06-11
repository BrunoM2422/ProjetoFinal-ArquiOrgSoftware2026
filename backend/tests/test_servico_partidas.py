"""Testes da camada de aplicação (ServicoDePartidas + repositório em memória)."""

import random

import pytest

from app.adapters.persistence.repositorio_memoria import RepositorioEmMemoria
from app.application.erros import (
    NivelDeBotInvalidoError,
    PartidaNaoEncontradaError,
)
from app.application.servico_partidas import ServicoDePartidas
from app.domain.bots.aleatoria import EstrategiaAleatoria
from app.domain.casa import Casa
from app.domain.cor import Cor
from app.domain.erros import LanceIlegalError
from app.domain.moves.lance import Lance


def _lance(texto: str) -> Lance:
    """Constrói um lance a partir de uma string algébrica como "e2e4"."""
    origem = Casa.de_algebrica(texto[:2])
    destino = Casa.de_algebrica(texto[2:4])
    promocao = texto[5:] or None if "=" in texto else None
    return Lance(origem, destino, promocao)


def _servico() -> ServicoDePartidas:
    # Bot determinístico para os testes: aleatório com semente fixa, qualquer
    # que seja o nível pedido. A análise também usa um bot rápido.
    aleatorio = random.Random(7)
    return ServicoDePartidas(
        RepositorioEmMemoria(),
        fabrica_estrategia=lambda nivel: EstrategiaAleatoria(aleatorio),
        estrategia_analise=EstrategiaAleatoria(random.Random(1)),
    )


def test_criar_partida_humano_de_brancas_nao_dispara_bot():
    servico = _servico()
    registro = servico.criar_partida("aleatorio")
    assert registro.cor_bot == Cor.PRETA
    assert registro.cor_humano == Cor.BRANCA
    assert registro.partida.vez == Cor.BRANCA
    assert registro.partida.historico == []


def test_criar_partida_humano_de_pretas_faz_bot_abrir():
    servico = _servico()
    registro = servico.criar_partida("aleatorio", cor_humano=Cor.PRETA)
    assert registro.cor_bot == Cor.BRANCA
    # O bot (brancas) abriu, então já é a vez do humano (pretas).
    assert registro.partida.vez == Cor.PRETA
    assert len(registro.partida.historico) == 1


def test_criar_partida_recusa_nivel_invalido():
    servico = _servico()
    with pytest.raises(NivelDeBotInvalidoError):
        servico.criar_partida("grandmaster")


def test_obter_partida_inexistente_levanta_erro():
    servico = _servico()
    with pytest.raises(PartidaNaoEncontradaError):
        servico.obter_partida("nao-existe")


def test_obter_partida_recupera_a_sessao_salva():
    servico = _servico()
    registro = servico.criar_partida("aleatorio")
    assert servico.obter_partida(registro.id) is registro


def test_aplicar_lance_humano_dispara_resposta_do_bot():
    servico = _servico()
    registro = servico.criar_partida("aleatorio")
    resultado = servico.aplicar_lance(registro.id, _lance("e2e4"))

    assert str(resultado.lance_humano) == "e2e4"
    assert resultado.lance_bot is not None
    # Depois da jogada inteira, volta a ser a vez do humano.
    assert resultado.registro.partida.vez == Cor.BRANCA
    assert len(resultado.registro.partida.historico) == 2


def test_aplicar_lance_ilegal_propaga_erro_de_dominio():
    servico = _servico()
    registro = servico.criar_partida("aleatorio")
    with pytest.raises(LanceIlegalError):
        servico.aplicar_lance(registro.id, _lance("e2e5"))


def test_desfazer_volta_a_jogada_inteira():
    servico = _servico()
    registro = servico.criar_partida("aleatorio")
    servico.aplicar_lance(registro.id, _lance("e2e4"))

    atualizado = servico.desfazer(registro.id)
    assert atualizado.partida.historico == []
    assert atualizado.partida.vez == Cor.BRANCA
    assert atualizado.partida.pode_desfazer() is False


def test_refazer_restaura_a_jogada_inteira():
    servico = _servico()
    registro = servico.criar_partida("aleatorio")
    servico.aplicar_lance(registro.id, _lance("e2e4"))
    servico.desfazer(registro.id)

    atualizado = servico.refazer(registro.id)
    assert len(atualizado.partida.historico) == 2
    assert atualizado.partida.vez == Cor.BRANCA


def test_analisar_nao_afeta_a_partida_real():
    servico = _servico()
    registro = servico.criar_partida("aleatorio")

    resultado = servico.analisar(registro.id, [_lance("e2e4")])

    # O clone avançou; a partida original continua intocada.
    assert len(resultado.partida_hipotetica.historico) == 1
    assert registro.partida.historico == []
    assert resultado.partida_hipotetica is not registro.partida


def test_analisar_sem_lances_sugere_a_partir_da_posicao_atual():
    servico = _servico()
    registro = servico.criar_partida("aleatorio")

    resultado = servico.analisar(registro.id)

    assert resultado.partida_hipotetica.historico == []
    assert resultado.lance_sugerido is not None
