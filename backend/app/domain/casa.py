"""A casa do tabuleiro — um value object imutável.

Internamente, uma casa é um par de índices ``(coluna, linha)`` no intervalo
0..7. Externamente, ela conhece a notação algébrica padrão do xadrez:
a coluna 0 é o arquivo ``a`` e a linha 0 é a fileira ``1``. Assim, a casa
de índices ``(4, 3)`` corresponde a ``e4``.

Por ser um ``frozen dataclass``, a casa é imutável e *hashable*, o que
permite usá-la diretamente como chave do dicionário do tabuleiro.
"""

from __future__ import annotations

from dataclasses import dataclass

_ARQUIVOS = "abcdefgh"


@dataclass(frozen=True)
class Casa:
    coluna: int  # 0..7  -> arquivos a..h
    linha: int   # 0..7  -> fileiras 1..8

    def __post_init__(self) -> None:
        if not self.dentro_do_tabuleiro():
            raise ValueError(
                f"Casa fora do tabuleiro: coluna={self.coluna}, linha={self.linha}"
            )

    def dentro_do_tabuleiro(self) -> bool:
        return 0 <= self.coluna <= 7 and 0 <= self.linha <= 7

    @classmethod
    def existe(cls, coluna: int, linha: int) -> bool:
        """Indica se um par de índices cai dentro do tabuleiro 8x8.

        Útil para a geração de lances, que precisa testar deslocamentos
        antes de criar a casa (o construtor recusaria índices inválidos).
        """
        return 0 <= coluna <= 7 and 0 <= linha <= 7

    @classmethod
    def de_algebrica(cls, texto: str) -> "Casa":
        """Constrói uma casa a partir da notação algébrica, ex.: ``"e4"``."""
        texto = texto.strip().lower()
        if len(texto) != 2 or texto[0] not in _ARQUIVOS or texto[1] not in "12345678":
            raise ValueError(f"Notação algébrica inválida: {texto!r}")
        return cls(coluna=_ARQUIVOS.index(texto[0]), linha=int(texto[1]) - 1)

    @property
    def algebrica(self) -> str:
        """Devolve a casa em notação algébrica, ex.: ``"e4"``."""
        return f"{_ARQUIVOS[self.coluna]}{self.linha + 1}"

    def deslocada(self, d_coluna: int, d_linha: int) -> "Casa":
        """Devolve a casa a ``(d_coluna, d_linha)`` de distância desta.

        Levanta ``ValueError`` se o destino sair do tabuleiro — quem gera
        lances deve checar antes com :meth:`existe`.
        """
        return Casa(self.coluna + d_coluna, self.linha + d_linha)

    def __str__(self) -> str:
        return self.algebrica
