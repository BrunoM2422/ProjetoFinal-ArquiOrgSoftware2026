"""Exporta a especificação OpenAPI da API para ``docs/openapi.yaml``.

Gerar o contrato a partir da própria aplicação (em vez de manter um YAML à
mão) garante que a documentação nunca diverge das rotas e schemas reais.

Uso (a partir de ``backend/``):

    .venv/bin/python scripts/exportar_openapi.py
"""

from __future__ import annotations

from pathlib import Path

import yaml

from app.main import create_app

DESTINO = Path(__file__).resolve().parents[2] / "docs" / "openapi.yaml"


def main() -> None:
    especificacao = create_app().openapi()
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    with DESTINO.open("w", encoding="utf-8") as arquivo:
        yaml.safe_dump(especificacao, arquivo, allow_unicode=True, sort_keys=False)
    print(f"OpenAPI exportada para {DESTINO}")


if __name__ == "__main__":
    main()
