/**
 * Componente raiz: compõe o tabuleiro, a lista de lances e os controles em
 * torno do hook `usePartida`, que centraliza o estado e as chamadas à API.
 */

import { Controles } from "./components/Controles";
import { ListaLances } from "./components/ListaLances";
import { Tabuleiro } from "./components/Tabuleiro";
import { usePartida } from "./hooks/usePartida";

export function App() {
  const {
    partida,
    erro,
    ocupado,
    sugestao,
    ultimoLanceBot,
    novaPartida,
    jogar,
    desfazer,
    refazer,
    pedirAnalise,
  } = usePartida();

  return (
    <main className="app">
      <header>
        <h1>♟️ Plataforma de Treino de Xadrez</h1>
      </header>

      <div className="conteudo">
        <section className="coluna-tabuleiro">
          {partida ? (
            <Tabuleiro
              partida={partida}
              sugestao={sugestao}
              onJogar={jogar}
              desabilitado={ocupado}
            />
          ) : (
            <div className="placeholder">
              Inicie uma nova partida para começar a jogar.
            </div>
          )}
        </section>

        <aside className="coluna-painel">
          <Controles
            partida={partida}
            ocupado={ocupado}
            onNova={novaPartida}
            onDesfazer={desfazer}
            onRefazer={refazer}
            onAnalisar={pedirAnalise}
          />

          {partida && (
            <div className="status">
              <h2>Situação</h2>
              <p className={partida.estado.em_xeque ? "xeque" : ""}>
                {partida.estado.descricao}
              </p>
              {!partida.estado.terminada && (
                <p>
                  Vez das {partida.vez === "branca" ? "brancas" : "pretas"}
                  {partida.vez === partida.cor_humano ? " (você)" : " (bot)"}.
                </p>
              )}
              {ultimoLanceBot && (
                <p>
                  Último lance do bot: <strong>{ultimoLanceBot.notacao}</strong>
                </p>
              )}
              {sugestao && (
                <p className="sugestao-texto">
                  Sugestão: <strong>{sugestao.notacao}</strong>
                </p>
              )}
            </div>
          )}

          {erro && <div className="erro">⚠️ {erro}</div>}

          {partida && <ListaLances historico={partida.historico} />}
        </aside>
      </div>
    </main>
  );
}
