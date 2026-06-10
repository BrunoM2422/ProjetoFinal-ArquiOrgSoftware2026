# Diagrama de Classes — Padrões GoF

Mostra onde cada um dos cinco padrões GoF aparece no domínio e como eles se
articulam em torno do agregado central `Partida`. Detalhamento em prosa em
[`docs/padroes-gof.md`](../docs/padroes-gof.md).

```mermaid
classDiagram
    direction LR

    %% ---------- Strategy: níveis de bot ----------
    class EstrategiaDeBot {
        <<interface>>
        +escolher_lance(partida) Lance
    }
    class EstrategiaAleatoria
    class EstrategiaGulosa
    class EstrategiaMinimax
    EstrategiaDeBot <|.. EstrategiaAleatoria
    EstrategiaDeBot <|.. EstrategiaGulosa
    EstrategiaDeBot <|.. EstrategiaMinimax

    %% ---------- State: estados da partida ----------
    class EstadoPartida {
        <<interface>>
        +permite_lance() bool
        +terminada bool
        +descricao
    }
    class EmAndamento
    class Xeque
    class XequeMate
    class Empate
    EstadoPartida <|.. EmAndamento
    EstadoPartida <|.. Xeque
    EstadoPartida <|.. XequeMate
    EstadoPartida <|.. Empate

    %% ---------- Command + Memento: histórico ----------
    class Comando {
        <<interface>>
        +executar(tabuleiro)
        +desfazer(tabuleiro)
    }
    class ComandoLance
    class GerenciadorHistorico
    class MementoTabuleiro
    Comando <|.. ComandoLance
    GerenciadorHistorico o-- Comando : passado / futuro
    ComandoLance ..> MementoTabuleiro : guarda

    %% ---------- Factory Method: criação de peças ----------
    class Peca {
        <<abstract>>
        +gerar_lances_pseudolegais(tabuleiro, origem)
    }
    class Rei
    class Dama
    class Torre
    class Bispo
    class Cavalo
    class Peao
    Peca <|-- Rei
    Peca <|-- Dama
    Peca <|-- Torre
    Peca <|-- Bispo
    Peca <|-- Cavalo
    Peca <|-- Peao

    %% ---------- Agregado central ----------
    class Partida {
        +aplicar_lance(lance) Lance
        +desfazer() bool
        +refazer() bool
        +clonar() Partida
        +estado EstadoPartida
    }
    class Tabuleiro {
        +aplicar_lance(lance)
        +criar_memento() MementoTabuleiro
        +restaurar(memento)
    }

    Partida *-- Tabuleiro
    Partida o-- GerenciadorHistorico
    Partida --> EstadoPartida : estado atual
    Tabuleiro ..> MementoTabuleiro : cria / restaura
    Tabuleiro o-- Peca : casas ocupadas

    note for Partida "clonar() = Prototype<br/>(cópia profunda para a análise 'e se?')"
    note for Peca "criadas por criar_peca() = Factory Method"
```

## Os cinco padrões no diagrama

| Padrão | Onde |
|--------|------|
| **Strategy** | `EstrategiaDeBot` e suas implementações (níveis de bot intercambiáveis) |
| **State** | `EstadoPartida` e os estados concretos (mate, empate, xeque, em andamento) |
| **Command** | `Comando` / `ComandoLance` executados pelo `GerenciadorHistorico` |
| **Memento** | `MementoTabuleiro`, criado/restaurado pelo `Tabuleiro` (originador) |
| **Prototype** | `Partida.clonar()` — cópia independente para análise |
| **Factory Method** | `criar_peca()` produz a subclasse de `Peca` certa a partir do símbolo FEN |

> Observação: o enunciado pede **implementar os cinco** padrões e **detalhar três**.
> Os escolhidos para detalhamento são **Strategy**, **State** e **Command + Memento**
> (tratados como um par, pois operam juntos no undo/redo).
