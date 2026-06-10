# Diagrama de Contêineres (C4 — Nível 2)

Visão dos contêineres que compõem a plataforma e como o jogador interage com
eles. O foco é mostrar a separação entre a interface (SPA) e a API, e que a
persistência hoje vive **no mesmo processo** da API (repositório em memória,
ver [ADR-004](../adrs/ADR-004.md)).

```mermaid
C4Container
    title Contêineres — Plataforma de Treino de Xadrez

    Person(jogador, "Jogador", "Pessoa que treina jogando contra o bot")

    System_Boundary(plataforma, "Plataforma de Treino de Xadrez") {
        Container(spa, "Interface Web", "React + TypeScript (Vite)", "Tabuleiro interativo, lista de lances e controles de undo/redo/análise")
        Container(api, "API REST", "Python 3.11+, FastAPI", "Casos de uso, regras do xadrez (domínio hexagonal) e estratégias de bot")
        ContainerDb(repo, "Repositório de partidas", "Dicionário em memória (no processo da API)", "Guarda as partidas em andamento")
    }

    Rel(jogador, spa, "Joga lances, desfaz/refaz, pede análise", "HTTPS")
    Rel(spa, api, "Consome os endpoints /v1", "JSON / HTTP")
    Rel(api, repo, "Lê e grava partidas", "em processo")

    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

## Leitura

- A **Interface Web** não contém regra de xadrez: ela só desenha a posição
  (a partir da FEN) e oferece ao jogador os lances que a API já marcou como
  legais. Isso sustenta a confiabilidade — a única autoridade sobre o que é
  legal é o domínio.
- A **API REST** é a fronteira do monolito modular. Internamente segue a
  Arquitetura Hexagonal: o adaptador HTTP fala com os casos de uso, que falam
  com o domínio através de portas (ver [ADR-003](../adrs/ADR-003.md)).
- O **Repositório** é um detalhe substituível: a aplicação depende apenas da
  porta `RepositorioDePartidas`; trocar a memória por um banco é escrever
  outro adaptador, sem tocar em domínio ou aplicação.
