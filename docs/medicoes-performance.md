# Medições de performance — atributo de qualidade "Eficiência/Desempenho"

> Rascunho de matéria-prima para a Seção 2 (Atributos de Qualidade) do documento.
> Medições feitas com Python 3.14 a partir da posição inicial padrão.

## Metas (definidas no escopo do projeto)

| Operação | Meta |
|----------|------|
| Geração + validação de lances legais de uma posição | < 50 ms |
| Resposta do bot raso (minimax) | < 500 ms |

## Resultados medidos

| Operação | Tempo medido | Meta | Margem |
|----------|-------------:|-----:|--------|
| Geração + validação de lances legais (posição inicial, média de 20) | ~3,3 ms | < 50 ms | ~15× abaixo |
| Bot minimax profundidade 2 + alfa-beta (posição inicial) | ~212 ms | < 500 ms | ~2,4× abaixo |
| Bot guloso (1 meio-lance) | ~6 ms | — | — |

## Leitura

- A validação de lances fica **muito** dentro da meta, o que sustenta a
  decisão de validar por simulação em cópia (deepcopy) sem comprometer o
  desempenho.
- O minimax cumpre a meta com folga graças à **poda alfa-beta** e à
  profundidade fixa e pequena (2). A maior parte do custo está nas cópias
  profundas do tabuleiro a cada nó — aceitável no escopo, e o ponto natural
  de otimização caso se quisesse aprofundar a busca (make/unmake em vez de
  clonar).

> Observação: os tempos absolutos variam com a máquina; o que importa é a
> ordem de grandeza e a margem confortável em relação às metas.
