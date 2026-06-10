# Padrões de Projeto GoF

> Rascunho de matéria-prima para a seção de Padrões do documento final.
> O enunciado pede **implementar cinco** padrões e **detalhar três**. Aqui os
> cinco estão descritos com a evidência no código; os três detalhados
> (**Strategy**, **State** e **Command + Memento**) ganham a análise mais
> profunda. Diagrama de classes em
> [`diagrams/classes-padroes.md`](../diagrams/classes-padroes.md).

---

## 1. Strategy — níveis de bot (detalhado)

**Intenção (GoF):** definir uma família de algoritmos, encapsular cada um e
torná-los intercambiáveis, deixando o algoritmo variar independentemente de
quem o usa.

**No projeto:** o adversário do humano escolhe lances por uma estratégia. A
porta é minúscula e estável:

- Porta: `EstrategiaDeBot` — `app/domain/ports/estrategia_bot.py`
  (`escolher_lance(partida) -> Lance | None`).
- Estratégias concretas — `app/domain/bots/`:
  - `EstrategiaAleatoria` (escolhe um lance legal ao acaso);
  - `EstrategiaGulosa` (maximiza material em 1 meio-lance);
  - `EstrategiaMinimax` (busca em profundidade 2 com poda alfa-beta).
- Seleção do algoritmo: `criar_estrategia(nivel)` em `app/domain/bots/fabrica.py`.

**Por que é Strategy e não `if/else`:** quem usa o bot (o
`ServicoDePartidas`) depende **apenas** da porta. Trocar o nível é injetar
outra implementação; **adicionar** um nível novo é criar uma classe e
registrá-la na fábrica, sem tocar em nenhum chamador (ver OCP/DIP em
[`solid.md`](./solid.md)).

**Evidência de que funciona:** `test_minimax_nao_morde_isca_que_a_gulosa_morderia`
em `backend/tests/test_bots.py` mostra duas estratégias produzindo decisões
diferentes na mesma posição — a prova viva de que os algoritmos são
intercambiáveis e distintos.

---

## 2. State — estados da partida (detalhado)

**Intenção (GoF):** permitir que um objeto altere seu comportamento quando seu
estado interno muda; o objeto parece mudar de classe.

**No projeto:** a partida está sempre em um estado — em andamento, em xeque,
xeque-mate ou empate — e é o estado que decide se ela ainda aceita lances.

- Hierarquia: `EstadoPartida` (abstrata) e os concretos `EmAndamento`,
  `Xeque`, `XequeMate`, `Empate` — `app/domain/states/estado.py`.
- Transição: `classificar_estado(...)` em
  `app/domain/states/classificador.py` examina a posição (há lances legais?
  rei em xeque? empate?) e devolve o estado correspondente.
- Uso: `Partida` guarda `self._estado` e reclassifica após cada lance
  (`app/domain/partida.py`).

**O que o polimorfismo elimina:** em vez de a `Partida` carregar flags
(`terminada`, `em_xeque`, `resultado`) e ramificações, ela pergunta ao estado
`permite_lance()`. Recusar um lance em partida encerrada é uma decisão do
estado, não um `if` espalhado.

**Empates cobertos (ver [ADR-006](../adrs/ADR-006.md)):** afogamento, material
insuficiente, regra dos 50 lances e tripla repetição. Testes em
`backend/tests/test_estados.py`.

---

## 3. Command + Memento — undo/redo (detalhado, em par)

Estes dois andam juntos: o **Command** transforma o lance num objeto
executável/desfazível, e o **Memento** é como o desfazer acontece sem reverter
nada à mão.

**Command — intenção (GoF):** encapsular uma solicitação como objeto,
permitindo enfileirar, registrar e desfazer operações.

- `Comando` (abstrata) e `ComandoLance` — `app/domain/history/comando.py`.
- Caretaker: `GerenciadorHistorico` com pilhas de passado e futuro —
  `app/domain/history/gerenciador.py`. Um lance novo descarta a linha de redo.

**Memento — intenção (GoF):** capturar e externalizar o estado interno de um
objeto sem violar o encapsulamento, para restaurá-lo depois.

- `MementoTabuleiro` (snapshot opaco) — `app/domain/history/memento.py`.
- Originador: `Tabuleiro.criar_memento()` / `Tabuleiro.restaurar(memento)` —
  `app/domain/board.py`. Só o tabuleiro conhece a estrutura interna do memento.

**A grande vantagem:** `ComandoLance.executar` fotografa o estado **antes** de
aplicar o lance; `desfazer` apenas restaura a fotografia. Resultado: roque, en
passant e promoção são desfeitos de graça, sem nenhuma lógica de reversão
específica — o que seria a parte mais frágil de um undo manual.

**Evidência:** `backend/tests/test_historico.py` desfaz e refaz lances
especiais e confere que a posição volta idêntica.

---

## 4. Prototype — análise "e se?" (implementado)

**Intenção (GoF):** criar novos objetos copiando um protótipo.

**No projeto:** `Partida.clonar()` (`app/domain/partida.py`) devolve uma cópia
profunda e independente da partida. A análise aplica lances hipotéticos no
clone sem qualquer efeito sobre o jogo real (`ServicoDePartidas.analisar`).
A decisão de usar cópia profunda está em [ADR-005](../adrs/ADR-005.md).

**Evidência:** `backend/tests/test_analise.py` e
`test_analise_nao_afeta_a_partida_real` (em `test_servico_partidas.py` e
`test_api.py`) confirmam o isolamento.

---

## 5. Factory Method — criação de peças (implementado)

**Intenção (GoF):** definir uma interface para criar um objeto, deixando as
subclasses/uma função decidirem qual classe instanciar.

**No projeto:** `criar_peca(simbolo)` em `app/domain/pieces/fabrica.py` traduz
um símbolo FEN (`'K'`, `'q'`, …) na subclasse correta de `Peca`, já com a cor.
O parser de FEN (`Tabuleiro.de_fen`) e a promoção (`Tabuleiro.aplicar_lance`)
criam peças **sem conhecer as classes concretas** — pedem à fábrica.

**Evidência:** `backend/tests/test_fabrica_pecas.py`.
