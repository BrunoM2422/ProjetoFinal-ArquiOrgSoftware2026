"""Núcleo do domínio do xadrez — o "tabuleiro e suas regras".

Esta camada é o coração da Arquitetura Hexagonal. Ela não conhece HTTP,
FastAPI nem banco de dados: sabe apenas o que é uma partida de xadrez,
quais lances são legais e em que estado o jogo se encontra.

Nada aqui pode importar de `app.adapters` ou de bibliotecas de
infraestrutura. Se o domínio precisa falar com o mundo externo, ele
declara uma *porta* (interface) em `domain/ports` e deixa um adaptador
implementá-la.
"""
