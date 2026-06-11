"""Adaptador de entrada: API REST com FastAPI.

Traduz requisições HTTP em chamadas aos casos de uso e mapeia o resultado
(e as exceções do domínio, como IllegalMoveError) de volta para respostas
HTTP com os códigos corretos.
"""
