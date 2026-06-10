# Princípios SOLID — evidências no código

> Rascunho de matéria-prima para a seção SOLID do documento final. Cada
> princípio aponta para código real do projeto.

---

## S — Responsabilidade Única (SRP)

Cada classe do domínio tem um motivo para mudar:

- `Tabuleiro` (`app/domain/board.py`) **guarda e executa** a posição, mas não
  decide legalidade.
- `GeradorDeLances` (`app/domain/moves/gerador.py`) **gera** lances
  pseudolegais.
- `ValidadorDeLances` (`app/domain/moves/validador.py`) **filtra** os que
  deixariam o rei em xeque.

A separação gerador/validador é deliberada: a regra "o lance não pode expor o
próprio rei" mudou de lugar uma vez só, sem mexer em quem gera os lances das
peças.

---

## O — Aberto/Fechado (OCP)

O sistema é aberto para extensão e fechado para modificação em dois pontos-chave:

- **Novo nível de bot:** criar uma classe que implemente `EstrategiaDeBot` e
  registrá-la em `criar_estrategia` (`app/domain/bots/fabrica.py`). Nenhum
  chamador do bot muda.
- **Nova peça / regra de peça:** cada peça encapsula seus próprios lances
  (`gerar_lances_pseudolegais`). O gerador e o validador iteram sobre `Peca`
  sem `isinstance` por tipo de peça.

É o mesmo princípio que sustenta o atributo de **manutenibilidade**
(ver [`atributos-qualidade.md`](./atributos-qualidade.md)).

---

## L — Substituição de Liskov (LSP)

As hierarquias são substituíveis sem surpresas:

- Qualquer `Peca` pode ser usada onde se espera `Peca` — todas honram o
  contrato de `gerar_lances_pseudolegais` / `casas_atacadas` (o `Peao`
  redefine `casas_atacadas` mantendo o contrato: ataca só as diagonais).
- Qualquer `EstrategiaDeBot` devolve um `Lance | None` válido.
- Qualquer `EstadoPartida` responde a `permite_lance()` coerentemente
  (estados terminais recusam lances).

A suíte `perft` (`backend/tests/test_perft.py`) é uma prova indireta forte:
ela só bate com os valores tabelados se todas as peças se comportarem
corretamente sob a mesma interface.

---

## I — Segregação de Interfaces (ISP)

As portas são pequenas e focadas — o cliente não depende de métodos que não usa:

- `EstrategiaDeBot` (`app/domain/ports/estrategia_bot.py`): um único método,
  `escolher_lance`.
- `RepositorioDePartidas` (`app/application/portas.py`): só `salvar` e
  `obter`.

Interfaces enxutas tornam triviais as implementações alternativas e os dublês
de teste.

---

## D — Inversão de Dependências (DIP)

As dependências apontam para **abstrações**, e a ligação concreta acontece num
único lugar:

- O `ServicoDePartidas` (`app/application/servico_partidas.py`) depende da
  porta `RepositorioDePartidas` e de uma fábrica de estratégias — nunca de
  `RepositorioEmMemoria` nem de uma estratégia concreta.
- O **composition root** (`app/main.py`) é o único ponto que conhece os
  adaptadores concretos: instancia `RepositorioEmMemoria`, injeta no serviço e
  injeta o serviço nas rotas.

Esse arranjo é o coração da Arquitetura Hexagonal (ver
[ADR-003](../adrs/ADR-003.md)): o domínio e a aplicação no centro, os
adaptadores na borda, e as setas de dependência sempre apontando para dentro.
