"""Adaptador de saída: persistência das partidas.

Implementação em memória da porta `RepositorioDePartidas` (ver ADR-004).
Trocar por um banco real no futuro exige apenas um novo adaptador, sem
tocar no domínio.
"""
