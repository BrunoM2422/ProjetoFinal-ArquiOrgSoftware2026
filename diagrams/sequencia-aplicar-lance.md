# Diagrama de Sequência — Aplicar um lance (com resposta do bot)

Mostra o caminho completo de um lance do humano: da interface até o domínio,
passando pela validação de legalidade e pelo histórico (Command + Memento), e
em seguida a resposta automática do bot (Strategy). É o fluxo que costura a
maioria dos padrões e camadas do projeto.

```mermaid
sequenceDiagram
    actor Jogador
    participant UI as Interface (React)
    participant API as Rota POST /v1/.../moves
    participant Serv as ServicoDePartidas
    participant Part as Partida
    participant Val as ValidadorDeLances
    participant Hist as GerenciadorHistorico
    participant Cmd as ComandoLance
    participant Tab as Tabuleiro
    participant Bot as EstrategiaDeBot

    Jogador->>UI: clica origem e destino
    UI->>API: POST { origem, destino }
    API->>Serv: aplicar_lance(id, lance)
    Serv->>Part: aplicar_lance(lance)

    Part->>Val: gerar_legais(tabuleiro, vez)
    Val-->>Part: lances legais
    Note over Part: casa o pedido com um lance legal;<br/>se não houver, levanta LanceIlegalError (HTTP 400)

    Part->>Hist: executar(ComandoLance, tabuleiro)
    Hist->>Cmd: executar(tabuleiro)
    Cmd->>Tab: criar_memento()
    Tab-->>Cmd: memento (snapshot)
    Cmd->>Tab: aplicar_lance(lance)
    Part->>Part: reclassifica o estado (State)
    Part-->>Serv: lance aplicado

    alt é a vez do bot e a partida não terminou
        Serv->>Bot: escolher_lance(partida)
        Bot-->>Serv: lance do bot
        Serv->>Part: aplicar_lance(lance_bot)
    end

    Serv-->>API: ResultadoLance (humano + bot)
    API-->>UI: ResultadoLanceView (JSON)
    UI-->>Jogador: atualiza tabuleiro e lista de lances
```

## Leitura

- A **legalidade** é decidida uma única vez, no domínio (`ValidadorDeLances`).
  A interface e o serviço nunca reimplementam regra — sustenta a
  confiabilidade ("0 lances ilegais").
- O **Memento** é tirado *antes* de aplicar o lance; por isso o `desfazer()`
  não precisa reverter manualmente roque, en passant ou promoção: ele apenas
  restaura a fotografia.
- A **resposta do bot** é orquestrada na camada de aplicação, não no domínio:
  a `Partida` não sabe que existe um bot do outro lado. Isso mantém o domínio
  puro e torna o nível do bot trocável (Strategy).
