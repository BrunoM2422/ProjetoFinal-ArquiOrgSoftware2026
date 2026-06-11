"""Adaptadores — as "mãos" que conectam o domínio ao mundo externo.

Cada adaptador implementa uma porta definida pelo domínio:
    api/          -> adaptador de entrada (driving): rotas FastAPI + DTOs.
    persistence/  -> adaptador de saída (driven): repositório em memória.
"""
