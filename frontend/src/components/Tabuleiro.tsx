/**
 * O tabuleiro interativo.
 *
 * Renderiza a posição a partir da FEN devolvida pela API e implementa o
 * "clicar para mover": primeiro clique seleciona uma peça do humano, segundo
 * clique numa casa de destino legal envia o lance. Os destinos legais vêm
 * prontos da API (`lances_legais`), de modo que o front não reimplementa
 * nenhuma regra de xadrez — ele apenas oferece os lances que o domínio já
 * disse serem válidos.
 */

import { useState } from "react";

import type { LanceInput, LanceView, PartidaView } from "../api/tipos";

// Usamos sempre os glifos "sólidos" (preenchidos) para as duas cores; a
// distinção entre brancas e pretas é feita por CSS (preenchimento + contorno),
// o que garante contraste consistente em qualquer casa do tema escuro.
const GLIFOS: Record<string, string> = {
  k: "♚", q: "♛", r: "♜", b: "♝", n: "♞", p: "♟",
};

const ARQUIVOS = "abcdefgh";

/** Converte a parte de posição da FEN num mapa casa-algébrica -> peça. */
function casasDoFen(fen: string): Record<string, string> {
  const posicao = fen.split(" ")[0];
  const casas: Record<string, string> = {};
  posicao.split("/").forEach((fileira, indice) => {
    const linha = 8 - indice; // a FEN começa pela 8ª fileira
    let coluna = 0;
    for (const caractere of fileira) {
      if (/\d/.test(caractere)) {
        coluna += Number(caractere);
      } else {
        casas[`${ARQUIVOS[coluna]}${linha}`] = caractere;
        coluna += 1;
      }
    }
  });
  return casas;
}

function ehPecaDe(simbolo: string | undefined, cor: string): boolean {
  if (!simbolo) return false;
  const branca = simbolo === simbolo.toUpperCase();
  return (cor === "branca") === branca;
}

interface Props {
  partida: PartidaView;
  sugestao: LanceView | null;
  onJogar: (lance: LanceInput) => void;
  desabilitado: boolean;
}

export function Tabuleiro({ partida, sugestao, onJogar, desabilitado }: Props) {
  const [selecionada, setSelecionada] = useState<string | null>(null);

  const casas = casasDoFen(partida.fen);
  const ehVezDoHumano = partida.vez === partida.cor_humano;
  const podeInteragir = !desabilitado && ehVezDoHumano && !partida.estado.terminada;

  // Casas de destino legais a partir da casa selecionada.
  const destinos = selecionada
    ? partida.lances_legais
        .filter((l) => l.origem === selecionada)
        .map((l) => l.destino)
    : [];

  function aoClicar(casa: string) {
    if (!podeInteragir) return;

    if (selecionada) {
      const candidatos = partida.lances_legais.filter(
        (l) => l.origem === selecionada && l.destino === casa
      );
      if (candidatos.length > 0) {
        let escolha = candidatos[0];
        // Promoção: vários candidatos (Q/R/B/N) para a mesma casa.
        if (candidatos.length > 1 || escolha.promocao) {
          const pedido =
            window.prompt("Promover para? (Q, R, B, N)", "Q")?.toUpperCase() ?? "Q";
          escolha = candidatos.find((c) => c.promocao === pedido) ?? escolha;
        }
        onJogar({
          origem: escolha.origem,
          destino: escolha.destino,
          promocao: escolha.promocao,
        });
        setSelecionada(null);
        return;
      }
      // Clicar noutra peça própria troca a seleção.
      if (ehPecaDe(casas[casa], partida.cor_humano)) {
        setSelecionada(casa);
        return;
      }
      setSelecionada(null);
      return;
    }

    if (ehPecaDe(casas[casa], partida.cor_humano)) {
      setSelecionada(casa);
    }
  }

  // Orientação: o humano sempre vê suas peças embaixo.
  const linhas = partida.cor_humano === "branca"
    ? [8, 7, 6, 5, 4, 3, 2, 1]
    : [1, 2, 3, 4, 5, 6, 7, 8];
  const colunas = partida.cor_humano === "branca"
    ? [0, 1, 2, 3, 4, 5, 6, 7]
    : [7, 6, 5, 4, 3, 2, 1, 0];

  return (
    <div className="tabuleiro" role="grid" aria-label="Tabuleiro de xadrez">
      {linhas.map((linha) =>
        colunas.map((coluna) => {
          const casa = `${ARQUIVOS[coluna]}${linha}`;
          const peca = casas[casa];
          const clara = (coluna + linha) % 2 === 0;
          const classes = ["casa", clara ? "clara" : "escura"];
          if (casa === selecionada) classes.push("selecionada");
          if (destinos.includes(casa)) {
            classes.push("destino");
            if (peca) classes.push("captura"); // destino ocupado = captura
          }
          if (sugestao && (casa === sugestao.origem || casa === sugestao.destino)) {
            classes.push("sugestao");
          }
          return (
            <button
              key={casa}
              type="button"
              className={classes.join(" ")}
              onClick={() => aoClicar(casa)}
              disabled={!podeInteragir}
              aria-label={casa}
            >
              {peca ? (
                <span
                  className={
                    "peca " +
                    (peca === peca.toUpperCase() ? "branca" : "preta")
                  }
                >
                  {GLIFOS[peca.toLowerCase()]}
                </span>
              ) : (
                destinos.includes(casa) && <span className="ponto" />
              )}
            </button>
          );
        })
      )}
    </div>
  );
}
