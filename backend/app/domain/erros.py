"""Erros do domínio do xadrez.

Exceções próprias do domínio, independentes de HTTP ou de qualquer
framework. O adaptador de API é quem traduz cada uma para o código de
status adequado (ver tratamento de erros na camada de API); o domínio
apenas sinaliza, em linguagem de xadrez, o que deu errado.
"""

from __future__ import annotations


class ErroDeDominio(Exception):
    """Raiz de todos os erros do domínio."""


class LanceIlegalError(ErroDeDominio):
    """Tentou-se aplicar um lance que não está entre os lances legais."""


class PartidaEncerradaError(ErroDeDominio):
    """Tentou-se jogar numa partida que já terminou (mate ou empate)."""
