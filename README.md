# ♟️ Plataforma de Treino de Xadrez

Trabalho final da disciplina **12452 — Padrões e Arquitetura de Software**
(Engenharia de Software, PUC-Campinas).

Uma plataforma onde o usuário joga partidas de xadrez contra um bot simples.
O foco do projeto **não é a força do motor de xadrez**, e sim demonstrar
**decisões arquiteturais conscientes**: arquitetura hexagonal, padrões de
projeto GoF, princípios SOLID e Clean Code. O código é a evidência; a
documentação é o produto.

## Funcionalidades

- Iniciar uma partida nova (humano vs. bot), escolhendo o nível do bot.
- Validar e aplicar lances legais (movimentos das peças, roque, en passant, promoção).
- Detectar estados: em andamento, xeque, xeque-mate e empate.
- Desfazer / refazer lances (undo/redo).
- Análise "e se?": simular lances numa cópia do tabuleiro sem afetar a partida real.
- Bot com níveis de dificuldade intercambiáveis (aleatório, guloso, minimax raso).
- Histórico de lances em notação algébrica.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.11+, FastAPI, Pydantic, Pytest |
| Frontend | React + TypeScript (Vite) |
| Arquitetura macro | Monolito modular |
| Arquitetura interna (backend) | Hexagonal (Ports & Adapters) |

## Arquitetura em uma frase

O **domínio** (`backend/app/domain`) é o tabuleiro e suas regras — ele não
sabe se quem move a peça é um humano pela API REST ou um teste do `pytest`.
Os **adaptadores** (`backend/app/adapters`) são as mãos que tocam as peças,
e o `main.py` é o árbitro que coloca todo mundo na mesa (composition root).

```
backend/app/
  domain/        # núcleo: regras do xadrez (sem framework)
  application/   # casos de uso que orquestram o domínio
  adapters/      # API REST (FastAPI) e persistência em memória
  main.py        # composition root (injeção de dependências)
```

As decisões arquiteturais estão registradas em [`/adrs`](./adrs) e os
diagramas em [`/diagrams`](./diagrams).

## Como rodar

### Pré-requisitos
- Python **3.11 ou superior**
- Node.js **18 ou superior** (com npm)

### Backend (API)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000`.
Verifique a saúde do servidor: `curl http://localhost:8000/health`.

### Frontend (interface)

Em outro terminal, com o backend rodando:

```bash
cd frontend
npm install
npm run dev
```

A interface sobe em `http://localhost:5173`. As chamadas para `/api` são
encaminhadas automaticamente para o backend (proxy do Vite).

## Testes

Os testes priorizam o domínio (geração de lances legais, transições de
estado, undo/redo), que pode ser testado sem subir a API:

```bash
cd backend
source .venv/bin/activate
pytest
```

## Documentação da API (OpenAPI)

Com o backend rodando, a especificação OpenAPI 3.x gerada pelo FastAPI fica
disponível em:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Schema JSON:** http://localhost:8000/openapi.json

Uma cópia versionada do schema é mantida em [`docs/openapi.yaml`](./docs/openapi.yaml),
gerada a partir da própria aplicação por `python scripts/exportar_openapi.py`.

## Documentação de apoio

Material que evidencia as decisões do projeto (matéria-prima para o documento final):

- **Decisões arquiteturais (ADRs):** [`adrs/`](./adrs) — formato Nygard, incluindo
  uma decisão revertida ([ADR-005](./adrs/ADR-005.md)).
- **Diagramas (Mermaid):**
  - [Contêineres (C4)](./diagrams/c4-conteineres.md)
  - [Classes dos padrões GoF](./diagrams/classes-padroes.md)
  - [Sequência — aplicar um lance](./diagrams/sequencia-aplicar-lance.md)
- **Análises:**
  - [Padrões GoF](./docs/padroes-gof.md)
  - [Princípios SOLID](./docs/solid.md)
  - [Atributos de qualidade](./docs/atributos-qualidade.md)
  - [Medições de performance](./docs/medicoes-performance.md)

## Estrutura do repositório

```
backend/    # API FastAPI + domínio hexagonal do xadrez
frontend/   # interface React + TypeScript (Vite)
adrs/       # Architecture Decision Records (formato Nygard)
diagrams/   # diagramas Mermaid (containers, classes, sequência)
docs/       # rascunhos e material de apoio para o documento final
```
