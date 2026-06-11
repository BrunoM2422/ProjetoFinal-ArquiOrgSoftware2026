"""Portas do domínio — interfaces que o núcleo expõe ou consome.

São abstrações pequenas e focadas (ISP). Os adaptadores em `app.adapters`
as implementam, e o `main.py` injeta as implementações concretas (DIP).
Exemplo: a porta `RepositorioDePartidas` é definida aqui; o adaptador em
memória vive em `adapters/persistence`.
"""
