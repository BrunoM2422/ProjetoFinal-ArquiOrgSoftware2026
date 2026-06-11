"""Camada de aplicação — casos de uso que orquestram o domínio.

Coordena o domínio para realizar uma intenção do usuário (criar partida,
aplicar lance, desfazer, analisar). Não contém regra de xadrez: delega ao
domínio e fala com o mundo externo apenas através das portas.
"""
