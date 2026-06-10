# Atributos de Qualidade

> Rascunho de matéria-prima para a seção de Atributos de Qualidade do
> documento final. São três os atributos priorizados, cada um com a tática que
> o sustenta e a evidência correspondente.

---

## 1. Confiabilidade — "zero lances ilegais"

**Meta:** a plataforma nunca aceita um lance ilegal nem permite jogar em
partida encerrada.

**Táticas:**

- **Autoridade única sobre legalidade.** Só o domínio decide o que é legal
  (`ValidadorDeLances`). A interface apenas oferece os lances que a API marcou
  como legais; o servidor revalida sempre (`Partida.aplicar_lance`).
- **Validação por simulação.** Um lance pseudolegal só é aceito se, simulado em
  cópia, não deixar o próprio rei em xeque.
- **Estados terminais que recusam lances** (padrão State).

**Evidência:**

- `backend/tests/test_perft.py`: `perft(1)=20`, `perft(2)=400`, `perft(3)=8902`
  batem com os valores tabelados do xadrez — prova de ouro que cobre roque, en
  passant, promoção, cravada e xeque.
- `backend/tests/test_lances_legais.py` e os erros 400/409 testados em
  `backend/tests/test_api.py`.

---

## 2. Manutenibilidade — "estender sem tocar no núcleo" (OCP)

**Meta:** adicionar capacidades (um nível de bot, uma regra) sem modificar o
código existente que já funciona.

**Táticas:**

- **Arquitetura Hexagonal** (ADR-003): domínio isolado de framework; trocar a
  persistência ou a API é trocar adaptadores.
- **Pontos de extensão por polimorfismo:** `EstrategiaDeBot`, `Peca`,
  `EstadoPartida`.
- **Decisões registradas** em ADRs (formato Nygard), inclusive uma revertida
  ([ADR-005](../adrs/ADR-005.md)), o que documenta o raciocínio para quem
  mantém.

**Evidência concreta:** adicionar a `EstrategiaMinimax` não exigiu mudança
alguma em quem consome o bot — bastou uma classe nova e uma linha na fábrica.
O mesmo vale para os quatro tipos de empate (ADR-006), acrescentados no
classificador sem tocar na `Partida`.

---

## 3. Desempenho — limites de tempo de resposta

**Meta:** validação de lances legais de uma posição **< 50 ms**; resposta do
bot raso **< 500 ms**.

**Táticas:** geração/validação enxutas sobre um mapa de casas; minimax com
**poda alfa-beta** e profundidade fixa e pequena (2).

**Evidência:** medições detalhadas em
[`medicoes-performance.md`](./medicoes-performance.md):

| Operação | Medido | Meta |
|----------|-------:|-----:|
| Geração + validação de lances legais (posição inicial) | ~3,3 ms | < 50 ms |
| Bot minimax prof. 2 + alfa-beta | ~212 ms | < 500 ms |

O teste `test_minimax_responde_dentro_da_meta_de_performance`
(`backend/tests/test_bots.py`) verifica a meta de 500 ms de forma automatizada.

---

## Resumo

| Atributo | Tática principal | Evidência |
|----------|------------------|-----------|
| Confiabilidade | Validação por simulação + autoridade única | perft(3)=8902, erros HTTP |
| Manutenibilidade | Hexagonal + OCP por polimorfismo | bot/empates adicionados sem tocar no núcleo |
| Desempenho | Alfa-beta + profundidade fixa | ~3,3 ms / ~212 ms, dentro das metas |
