"""Pacote raiz do backend da Plataforma de Treino de Xadrez.

Organização interna em Arquitetura Hexagonal (Ports & Adapters):

    domain/        -> núcleo: regras do xadrez. Não importa framework.
    application/   -> casos de uso que orquestram o domínio.
    adapters/      -> implementações concretas das portas (API, persistência).
    main.py        -> composition root: amarra portas a adaptadores.

Regra de dependência: as setas apontam de fora para dentro. O domínio
nunca importa de `adapters` nem de FastAPI.
"""
